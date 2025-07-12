"""
Sistema de notificações para o Diário de Campo Digital
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .data_manager import data_manager

class NotificationManager:
    def __init__(self):
        self.data_manager = data_manager
    
    def get_notifications(self, user_id: int, user_profile: str) -> List[Dict[str, Any]]:
        """Retorna lista de notificações para o usuário"""
        notifications = []
        
        # Buscar inspeções vencidas
        vencidas = self.data_manager.get_inspecoes_vencidas()
        if user_profile == 'inspetor':
            vencidas = vencidas[vencidas['inspetor_id'] == user_id]
        
        for _, inspecao in vencidas.iterrows():
            notifications.append({
                'tipo': 'vencida',
                'titulo': 'Inspeção Vencida',
                'mensagem': f"Estabelecimento: {inspecao['estabelecimento']}",
                'urgencia': 'alta',
                'data': inspecao['prazo_inspetor'] or inspecao['prazo_coordenacao']
            })
        
        # Buscar inspeções próximas do vencimento
        proximas = self.data_manager.get_inspecoes_proximas_vencimento()
        if user_profile == 'inspetor':
            proximas = proximas[proximas['inspetor_id'] == user_id]
        
        for _, inspecao in proximas.iterrows():
            notifications.append({
                'tipo': 'proxima_vencimento',
                'titulo': 'Prazo Próximo',
                'mensagem': f"Estabelecimento: {inspecao['estabelecimento']}",
                'urgencia': 'media',
                'data': inspecao['prazo_inspetor'] or inspecao['prazo_coordenacao']
            })
        
        return sorted(notifications, key=lambda x: x['data'] if x['data'] else datetime.min)
    
    def show_notifications_sidebar(self, user_id: int, user_profile: str):
        """Exibe notificações na sidebar"""
        notifications = self.get_notifications(user_id, user_profile)
        
        if notifications:
            st.sidebar.markdown("### 🔔 Notificações")
            
            for notif in notifications[:5]:  # Mostrar apenas as 5 mais urgentes
                if notif['urgencia'] == 'alta':
                    st.sidebar.error(f"🔴 {notif['titulo']}: {notif['mensagem']}")
                elif notif['urgencia'] == 'media':
                    st.sidebar.warning(f"🟡 {notif['titulo']}: {notif['mensagem']}")
                else:
                    st.sidebar.info(f"🔵 {notif['titulo']}: {notif['mensagem']}")
            
            if len(notifications) > 5:
                st.sidebar.info(f"... e mais {len(notifications) - 5} notificações")
    
    def show_dashboard_alerts(self, user_id: int, user_profile: str):
        """Exibe alertas no dashboard principal"""
        notifications = self.get_notifications(user_id, user_profile)
        
        if not notifications:
            st.success("✅ Nenhum alerta no momento!")
            return
        
        st.markdown("### ⚠️ Alertas")
        
        # Contar por tipo
        vencidas = len([n for n in notifications if n['tipo'] == 'vencida'])
        proximas = len([n for n in notifications if n['tipo'] == 'proxima_vencimento'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if vencidas > 0:
                st.error(f"🔴 {vencidas} inspeção(ões) vencida(s)")
        
        with col2:
            if proximas > 0:
                st.warning(f"🟡 {proximas} inspeção(ões) próxima(s) do vencimento")
        
        # Mostrar detalhes em expander
        if notifications:
            with st.expander("Ver detalhes dos alertas"):
                for notif in notifications:
                    data_str = notif['data'].strftime("%d/%m/%Y") if notif['data'] else "Data não definida"
                    if notif['urgencia'] == 'alta':
                        st.error(f"🔴 **{notif['titulo']}** - {notif['mensagem']} (Prazo: {data_str})")
                    else:
                        st.warning(f"🟡 **{notif['titulo']}** - {notif['mensagem']} (Prazo: {data_str})")

# Instância global do gerenciador de notificações
notification_manager = NotificationManager()

