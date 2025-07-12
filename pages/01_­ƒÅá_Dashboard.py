"""
Dashboard principal do Diário de Campo Digital
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import auth_manager
from utils.data_manager import data_manager
from utils.notifications import notification_manager

# Configuração da página
st.set_page_config(
    page_title="Dashboard - VISA Digital",
    page_icon="🏠",
    layout="wide"
)

# Verificar autenticação
auth_manager.require_auth()

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .alert-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .alert-high {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    
    .alert-medium {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    
    .alert-low {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

def main():
    user = auth_manager.get_current_user()
    
    # Header
    st.markdown(f"""
    # 🏠 Dashboard
    **Bem-vindo(a), {user['nome']}!**
    """)
    
    # Sidebar com informações do usuário
    with st.sidebar:
        st.markdown(f"### 👤 {user['nome']}")
        st.markdown(f"**Perfil:** {user['perfil'].title()}")
        if user['territorio']:
            st.markdown(f"**Território:** {user['territorio']}")
        
        st.markdown("---")
        notification_manager.show_notifications_sidebar(user['id'], user['perfil'])
    
    # Alertas principais
    notification_manager.show_dashboard_alerts(user['id'], user['perfil'])
    
    st.markdown("---")
    
    # Métricas principais
    stats = data_manager.get_estatisticas(user['id'], user['perfil'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📋 Total</h3>
            <h2 style="color: #1f77b4;">{}</h2>
            <p>Inspeções</p>
        </div>
        """.format(stats['total']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⏳ Pendentes</h3>
            <h2 style="color: #ff7f0e;">{}</h2>
            <p>Em andamento</p>
        </div>
        """.format(stats['pendentes']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Concluídas</h3>
            <h2 style="color: #2ca02c;">{}</h2>
            <p>Finalizadas</p>
        </div>
        """.format(stats['concluidas']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🔴 Vencidas</h3>
            <h2 style="color: #d62728;">{}</h2>
            <p>Atrasadas</p>
        </div>
        """.format(stats['vencidas']), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos e análises
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribuição por Status")
        
        if stats['total'] > 0:
            # Gráfico de pizza
            labels = ['Pendentes', 'Concluídas', 'Vencidas']
            values = [stats['pendentes'], stats['concluidas'], stats['vencidas']]
            colors = ['#ff7f0e', '#2ca02c', '#d62728']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values,
                marker_colors=colors,
                hole=0.3
            )])
            
            fig.update_layout(
                showlegend=True,
                height=300,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma inspeção cadastrada ainda.")
    
    with col2:
        st.markdown("### 📈 Tendência Mensal")
        
        # Carregar dados para gráfico de tendência
        df = data_manager.get_inspecoes_by_user(user['id'], user['perfil'])
        
        if len(df) > 0:
            # Agrupar por mês
            df['mes'] = pd.to_datetime(df['data_inspecao']).dt.to_period('M')
            monthly_counts = df.groupby('mes').size().reset_index(name='count')
            monthly_counts['mes_str'] = monthly_counts['mes'].astype(str)
            
            fig = px.line(
                monthly_counts, 
                x='mes_str', 
                y='count',
                title='',
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Mês",
                yaxis_title="Número de Inspeções",
                height=300,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados insuficientes para gráfico de tendência.")
    
    # Últimas inspeções
    st.markdown("### 📋 Últimas Inspeções")
    
    df = data_manager.get_inspecoes_by_user(user['id'], user['perfil'])
    
    if len(df) > 0:
        # Ordenar por data de criação (mais recentes primeiro)
        df_recent = df.sort_values('data_criacao', ascending=False).head(5)
        
        # Preparar dados para exibição
        display_df = df_recent[['estabelecimento', 'data_inspecao', 'classificacao_risco', 'status']].copy()
        display_df['data_inspecao'] = pd.to_datetime(display_df['data_inspecao']).dt.strftime('%d/%m/%Y')
        
        # Adicionar ícones de status
        status_icons = {
            'pendente': '⏳',
            'concluido': '✅',
            'vencido': '🔴'
        }
        
        display_df['Status'] = display_df['status'].map(lambda x: f"{status_icons.get(x, '❓')} {x.title()}")
        
        # Renomear colunas
        display_df = display_df.rename(columns={
            'estabelecimento': 'Estabelecimento',
            'data_inspecao': 'Data',
            'classificacao_risco': 'Risco'
        })
        
        # Exibir tabela
        st.dataframe(
            display_df[['Estabelecimento', 'Data', 'Risco', 'Status']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma inspeção cadastrada ainda.")
    
    # Ações rápidas
    st.markdown("### ⚡ Ações Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Nova Inspeção", use_container_width=True):
            st.switch_page("pages/02_📝_Nova_Inspecao.py")
    
    with col2:
        if st.button("📋 Minhas Inspeções", use_container_width=True):
            st.switch_page("pages/03_📋_Minhas_Inspecoes.py")
    
    with col3:
        if user['perfil'] in ['coordenador', 'gerencia']:
            if st.button("👥 Painel Coordenação", use_container_width=True):
                st.switch_page("pages/04_👥_Painel_Coordenacao.py")
        else:
            if st.button("📊 Indicadores", use_container_width=True):
                st.switch_page("pages/05_📊_Indicadores.py")

if __name__ == "__main__":
    main()

