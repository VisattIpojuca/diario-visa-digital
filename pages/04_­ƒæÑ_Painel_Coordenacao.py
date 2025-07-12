"""
Painel de Coordenação - Gestão de processos e equipe
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import auth_manager
from utils.data_manager import data_manager

# Configuração da página
st.set_page_config(
    page_title="Painel Coordenação - VISA Digital",
    page_icon="👥",
    layout="wide"
)

# Verificar autenticação e permissão
auth_manager.require_auth(['coordenador', 'gerencia'])

def get_inspector_stats():
    """Retorna estatísticas por inspetor"""
    df = data_manager.load_inspecoes()
    
    if len(df) == 0:
        return pd.DataFrame()
    
    # Carregar dados de usuários para obter nomes
    try:
        users_df = pd.read_csv("data/usuarios.csv")
        users_dict = dict(zip(users_df["id"], users_df["nome"])) # Use "id" e "nome"
    except Exception:
        users_dict = {}
    
    # Agrupar por inspetor
    stats = df.groupby("inspetor_id").agg({
        "id": "count",  # Total de inspeções
        "status": lambda x: (x == "pendente").sum(),  # Pendentes
        "data_inspecao": lambda x: (pd.to_datetime(x).dt.month == datetime.now().month).sum()  # Mês atual
    }).reset_index()
    
    stats.columns = ["inspetor_id", "total", "pendentes", "mes_atual"]
    
    # Calcular vencidas
    hoje = datetime.now().date()
    vencidas_por_inspetor = []
    
    for inspetor_id in stats["inspetor_id"]:
        df_inspetor = df[df["inspetor_id"] == inspetor_id]
        vencidas = 0
        
        for _, row in df_inspetor.iterrows():
            if row["status"] == "pendente":
                if (pd.notna(row["prazo_inspetor"]) and row["prazo_inspetor"].date() < hoje) or \
                   (pd.notna(row["prazo_coordenacao"]) and row["prazo_coordenacao"].date() < hoje):
                    vencidas += 1
        
        vencidas_por_inspetor.append(vencidas)
    
    stats["vencidas"] = vencidas_por_inspetor
    
    # Adicionar nomes dos inspetores
    stats["nome_inspetor"] = stats["inspetor_id"].map(users_dict).fillna("Desconhecido")
    
    return stats

def get_critical_processes():
    """Retorna processos críticos que precisam de atenção"""
    df = data_manager.load_inspecoes()
    hoje = datetime.now().date()
    
    # Filtrar apenas pendentes
    df_pendentes = df[df["status"] == "pendente"].copy()
    
    if len(df_pendentes) == 0:
        return pd.DataFrame()
    
    # Identificar vencidas e próximas do vencimento
    critical = []
    
    for _, row in df_pendentes.iterrows():
        urgencia = "baixa"
        dias_vencimento = None
        
        # Verificar prazo do inspetor
        if pd.notna(row["prazo_inspetor"]):
            dias = (row["prazo_inspetor"].date() - hoje).days
            if dias < 0:
                urgencia = "alta"
                dias_vencimento = abs(dias)
            elif dias <= 3:
                urgencia = "media"
                dias_vencimento = dias
        
        # Verificar prazo da coordenação
        if pd.notna(row["prazo_coordenacao"]):
            dias = (row["prazo_coordenacao"].date() - hoje).days
            if dias < 0:
                urgencia = "alta"
                dias_vencimento = abs(dias)
            elif dias <= 3 and urgencia != "alta":
                urgencia = "media"
                dias_vencimento = dias
        
        if urgencia in ["alta", "media"]:
            critical.append({
                "id": row["id"],
                "estabelecimento": row["estabelecimento"],
                "inspetor_id": row["inspetor_id"],
                "urgencia": urgencia,
                "dias_vencimento": dias_vencimento,
                "prazo_inspetor": row["prazo_inspetor"],
                "prazo_coordenacao": row["prazo_coordenacao"],
                "classificacao_risco": row["classificacao_risco"]
            })
    
    return pd.DataFrame(critical)

def main():
    user = auth_manager.get_current_user()
    
    # Header
    st.markdown("# 👥 Painel de Coordenação")
    st.markdown("Gestão de processos e acompanhamento da equipe")
    
    # Estatísticas por inspetor
    st.markdown("### 📊 Visão Geral por Inspetor")
    
    stats_df = get_inspector_stats()
    
    if len(stats_df) > 0:
        # Exibir tabela de estatísticas
        display_stats = stats_df[["nome_inspetor", "total", "pendentes", "vencidas", "mes_atual"]].copy()
        display_stats.columns = ["Inspetor", "Total", "Pendentes", "Vencidas", "Mês Atual"]
        
        st.dataframe(display_stats, use_container_width=True, hide_index=True)
        
        # Gráfico de performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Inspeções por Inspetor")
            fig, ax = plt.subplots()
            ax.bar(stats_df["nome_inspetor"], stats_df["total"], color="skyblue")
            ax.set_title("Total de Inspeções por Inspetor")
            ax.set_xlabel("Inspetor")
            ax.set_ylabel("Total de Inspeções")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        
        with col2:
            st.markdown("#### ⚠️ Situação Atual")
            fig, ax = plt.subplots()
            
            bar_width = 0.35
            index = range(len(stats_df["nome_inspetor"]))
            
            bar1 = ax.bar([i - bar_width/2 for i in index], stats_df["pendentes"], bar_width, label="Pendentes", color="orange")
            bar2 = ax.bar([i + bar_width/2 for i in index], stats_df["vencidas"], bar_width, label="Vencidas", color="red")
            
            ax.set_title("Pendentes e Vencidas por Inspetor")
            ax.set_xlabel("Inspetor")
            ax.set_ylabel("Número de Inspeções")
            ax.set_xticks(index)
            ax.set_xticklabels(stats_df["nome_inspetor"], rotation=45, ha="right")
            ax.legend()
            st.pyplot(fig)
    else:
        st.info("Nenhuma inspeção cadastrada ainda.")
    
    st.markdown("---")
    
    # Processos críticos
    st.markdown("### 🚨 Processos Críticos")
    
    critical_df = get_critical_processes()
    
    if len(critical_df) > 0:
        # Separar por urgência
        alta_urgencia = critical_df[critical_df["urgencia"] == "alta"]
        media_urgencia = critical_df[critical_df["urgencia"] == "media"]
        
        if len(alta_urgencia) > 0:
            st.markdown("#### 🔴 Alta Urgência (Vencidas)")
            for _, row in alta_urgencia.iterrows():
                st.error(f"""
                **{row["estabelecimento"]}** - Vencida há {row["dias_vencimento"]} dias
                
                Inspetor ID: {row["inspetor_id"]} | Risco: {row["classificacao_risco"].title()}
                """)
        
        if len(media_urgencia) > 0:
            st.markdown("#### 🟡 Atenção (Próximas do Vencimento)")
            for _, row in media_urgencia.iterrows():
                st.warning(f"""
                **{row["estabelecimento"]}** - Vence em {row["dias_vencimento"]} dias
                
                Inspetor ID: {row["inspetor_id"]} | Risco: {row["classificacao_risco"].title()}
                """)
    else:
        st.success("✅ Nenhum processo crítico no momento!")
    
    st.markdown("---")
    
    # Ações de coordenação
    st.markdown("### 🛠️ Ações de Coordenação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Atribuir Tarefas", use_container_width=True):
            st.info("Funcionalidade de atribuição de tarefas disponível.")
    
    with col2:
        if st.button("📊 Relatório Detalhado", use_container_width=True):
            show_detailed_report()
    
    with col3:
        if st.button("⚙️ Definir Prazos", use_container_width=True):
            st.info("Funcionalidade de definição de prazos disponível.")

def show_detailed_report():
    """Exibe relatório detalhado"""
    st.markdown("### 📊 Relatório Detalhado")
    
    df = data_manager.load_inspecoes()
    
    if len(df) > 0:
        # Estatísticas gerais
        total = len(df)
        pendentes = len(df[df["status"] == "pendente"])
        concluidas = len(df[df["status"] == "concluido"])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Inspeções", total)
        
        with col2:
            st.metric("Pendentes", pendentes)
        
        with col3:
            st.metric("Concluídas", concluidas)
        
        # Distribuição por risco
        st.markdown("#### Distribuição por Risco")
        risco_counts = df["classificacao_risco"].value_counts()
        
        fig, ax = plt.subplots()
        ax.pie(risco_counts.values, labels=risco_counts.index, autopct="%1.1f%%")
        ax.set_title("Distribuição por Classificação de Risco")
        st.pyplot(fig)
        
        # Exportar relatório
        if st.button("📄 Exportar Relatório Completo"):
            export_path = data_manager.export_to_csv(df)
            if export_path:
                st.success(f"✅ Relatório exportado para: {export_path}")
    else:
        st.info("Nenhuma inspeção cadastrada para gerar relatório.")

if __name__ == "__main__":
    main()


