"""
Dashboard de Indicadores e Relatórios
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import auth_manager
from utils.data_manager import data_manager

# Configuração da página
st.set_page_config(
    page_title="Indicadores - VISA Digital",
    page_icon="📊",
    layout="wide"
)

# Verificar autenticação
auth_manager.require_auth()

def calculate_kpis(df, user_profile, user_id):
    """Calcula KPIs principais"""
    if user_profile == 'inspetor':
        df = df[df['inspetor_id'] == user_id]
    
    total = len(df)
    if total == 0:
        return {
            'total_inspecoes': 0,
            'cumprimento_prazos': 0,
            'media_dias_prazo': 0,
            'inspecoes_mes': 0,
            'percentual_alto_risco': 0
        }
    
    # Cumprimento de prazos
    hoje = datetime.now().date()
    concluidas = df[df['status'] == 'concluido']
    cumprimento = len(concluidas) / total * 100 if total > 0 else 0
    
    # Média de dias para conclusão
    if len(concluidas) > 0:
        concluidas_copy = concluidas.copy()
        concluidas_copy['dias_conclusao'] = (
            pd.to_datetime(concluidas_copy['data_atualizacao']) - 
            pd.to_datetime(concluidas_copy['data_inspecao'])
        ).dt.days
        media_dias = concluidas_copy['dias_conclusao'].mean()
    else:
        media_dias = 0
    
    # Inspeções do mês atual
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    inspecoes_mes = len(df[
        (pd.to_datetime(df['data_inspecao']).dt.month == mes_atual) &
        (pd.to_datetime(df['data_inspecao']).dt.year == ano_atual)
    ])
    
    # Percentual de alto risco
    alto_risco = len(df[df['classificacao_risco'] == 'alto'])
    percentual_alto_risco = alto_risco / total * 100 if total > 0 else 0
    
    return {
        'total_inspecoes': total,
        'cumprimento_prazos': cumprimento,
        'media_dias_prazo': media_dias,
        'inspecoes_mes': inspecoes_mes,
        'percentual_alto_risco': percentual_alto_risco
    }

def create_monthly_trend_chart(df, user_profile, user_id):
    """Cria gráfico de tendência mensal"""
    if user_profile == 'inspetor':
        df = df[df['inspetor_id'] == user_id]
    
    if len(df) == 0:
        return None
    
    # Agrupar por mês
    df_copy = df.copy()
    df_copy['data_inspecao'] = pd.to_datetime(df_copy['data_inspecao'])
    df_copy['mes_ano'] = df_copy['data_inspecao'].dt.to_period('M')
    
    monthly_data = df_copy.groupby(['mes_ano', 'status']).size().unstack(fill_value=0)
    monthly_data.index = monthly_data.index.astype(str)
    
    fig, ax = plt.subplots()
    
    if 'pendente' in monthly_data.columns:
        ax.plot(monthly_data.index, monthly_data['pendente'], marker='o', label='Pendentes', color='orange')
    
    if 'concluido' in monthly_data.columns:
        ax.plot(monthly_data.index, monthly_data['concluido'], marker='o', label='Concluídas', color='green')
    
    ax.set_title('Tendência Mensal de Inspeções')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Número de Inspeções')
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig

def create_risk_distribution_chart(df, user_profile, user_id):
    """Cria gráfico de distribuição por risco"""
    if user_profile == 'inspetor':
        df = df[df['inspetor_id'] == user_id]
    
    if len(df) == 0:
        return None
    
    risk_counts = df['classificacao_risco'].value_counts()
    
    colors = {
        'alto': '#d62728',
        'medio': '#ff7f0e', 
        'baixo': '#2ca02c'
    }
    
    fig, ax = plt.subplots()
    ax.pie(risk_counts.values, labels=[name.title() for name in risk_counts.index], autopct='%1.1f%%', colors=[colors.get(name, '#7f7f7f') for name in risk_counts.index])
    ax.set_title('Distribuição por Classificação de Risco')
    
    return fig

def create_status_chart(df, user_profile, user_id):
    """Cria gráfico de status das inspeções"""
    if user_profile == 'inspetor':
        df = df[df['inspetor_id'] == user_id]
    
    if len(df) == 0:
        return None
    
    # Calcular status atual incluindo vencidas
    hoje = datetime.now().date()
    status_atual = []
    
    for _, row in df.iterrows():
        if row['status'] == 'concluido':
            status_atual.append('Concluída')
        elif row['status'] == 'pendente':
            vencida = False
            if pd.notna(row['prazo_inspetor']) and pd.to_datetime(row['prazo_inspetor']).date() < hoje:
                vencida = True
            if pd.notna(row['prazo_coordenacao']) and pd.to_datetime(row['prazo_coordenacao']).date() < hoje:
                vencida = True
            
            if vencida:
                status_atual.append('Vencida')
            else:
                status_atual.append('Pendente')
        else:
            status_atual.append('Outro')
    
    status_counts = pd.Series(status_atual).value_counts()
    
    colors = {
        'Concluída': '#2ca02c',
        'Pendente': '#ff7f0e',
        'Vencida': '#d62728',
        'Outro': '#7f7f7f'
    }
    
    fig, ax = plt.subplots()
    ax.bar(status_counts.index, status_counts.values, color=[colors.get(status, '#7f7f7f') for status in status_counts.index])
    ax.set_title('Status Atual das Inspeções')
    ax.set_xlabel('Status')
    ax.set_ylabel('Quantidade')
    plt.tight_layout()
    
    return fig

def create_inspector_performance_chart(df):
    """Cria gráfico de performance por inspetor (apenas para coordenadores/gerência)"""
    if len(df) == 0:
        return None
    
    # Carregar dados de usuários
    try:
        users_df = pd.read_csv("data/usuarios.csv")
        users_dict = dict(zip(users_df['id'], users_df['nome']))
    except:
        users_dict = {}
    
    # Agrupar por inspetor
    inspector_stats = df.groupby('inspetor_id').agg({
        'id': 'count',
        'status': lambda x: (x == 'concluido').sum()
    }).reset_index()
    
    inspector_stats.columns = ['inspetor_id', 'total', 'concluidas']
    inspector_stats['pendentes'] = inspector_stats['total'] - inspector_stats['concluidas']
    inspector_stats['nome'] = inspector_stats['inspetor_id'].map(users_dict).fillna('Desconhecido')
    
    fig, ax = plt.subplots()
    
    bar_width = 0.35
    index = range(len(inspector_stats['nome']))
    
    bar1 = ax.bar([i - bar_width/2 for i in index], inspector_stats['concluidas'], bar_width, label='Concluídas', color='green')
    bar2 = ax.bar([i + bar_width/2 for i in index], inspector_stats['pendentes'], bar_width, label='Pendentes', color='orange')
    
    ax.set_title('Performance por Inspetor')
    ax.set_xlabel('Inspetor')
    ax.set_ylabel('Número de Inspeções')
    ax.set_xticks(index)
    ax.set_xticklabels(inspector_stats['nome'], rotation=45, ha='right')
    ax.legend()
    plt.tight_layout()
    
    return fig

def main():
    user = auth_manager.get_current_user()
    
    # Header
    st.markdown("# 📊 Indicadores e Relatórios")
    
    if user['perfil'] == 'inspetor':
        st.markdown("Seus indicadores de performance")
    else:
        st.markdown("Indicadores gerais do sistema")
    
    # Carregar dados
    df = data_manager.load_inspecoes()
    
    if len(df) == 0:
        st.info("Nenhuma inspeção cadastrada ainda.")
        return
    
    # Filtros de período
    st.markdown("### 📅 Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        periodo = st.selectbox(
            "Período:",
            options=["Todos", "Último mês", "Últimos 3 meses", "Último ano", "Personalizado"]
        )
    
    with col2:
        if periodo == "Personalizado":
            data_inicio = st.date_input("Data início:")
        else:
            data_inicio = None
    
    with col3:
        if periodo == "Personalizado":
            data_fim = st.date_input("Data fim:")
        else:
            data_fim = None
    
    # Aplicar filtros de período
    df_filtrado = df.copy()
    hoje = datetime.now().date()
    
    if periodo == "Último mês":
        inicio = hoje - timedelta(days=30)
        df_filtrado = df_filtrado[pd.to_datetime(df_filtrado['data_inspecao']).dt.date >= inicio]
    elif periodo == "Últimos 3 meses":
        inicio = hoje - timedelta(days=90)
        df_filtrado = df_filtrado[pd.to_datetime(df_filtrado['data_inspecao']).dt.date >= inicio]
    elif periodo == "Último ano":
        inicio = hoje - timedelta(days=365)
        df_filtrado = df_filtrado[pd.to_datetime(df_filtrado['data_inspecao']).dt.date >= inicio]
    elif periodo == "Personalizado" and data_inicio and data_fim:
        df_filtrado = df_filtrado[
            (pd.to_datetime(df_filtrado['data_inspecao']).dt.date >= data_inicio) &
            (pd.to_datetime(df_filtrado['data_inspecao']).dt.date <= data_fim)
        ]
    
    # KPIs principais
    st.markdown("### 📈 Indicadores Principais")
    
    kpis = calculate_kpis(df_filtrado, user['perfil'], user['id'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "📋 Total de Inspeções",
            kpis['total_inspecoes']
        )
    
    with col2:
        st.metric(
            "✅ Cumprimento",
            f"{kpis['cumprimento_prazos']:.1f}%"
        )
    
    with col3:
        st.metric(
            "⏱️ Média de Dias",
            f"{kpis['media_dias_prazo']:.0f}"
        )
    
    with col4:
        st.metric(
            "📅 Mês Atual",
            kpis['inspecoes_mes']
        )
    
    with col5:
        st.metric(
            "⚠️ Alto Risco",
            f"{kpis['percentual_alto_risco']:.1f}%"
        )
    
    st.markdown("---")
    
    # Gráficos
    st.markdown("### 📊 Análises Visuais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tendência mensal
        fig_trend = create_monthly_trend_chart(df_filtrado, user['perfil'], user['id'])
        if fig_trend:
            st.pyplot(fig_trend)
        else:
            st.info("Dados insuficientes para gráfico de tendência")
    
    with col2:
        # Distribuição por risco
        fig_risk = create_risk_distribution_chart(df_filtrado, user['perfil'], user['id'])
        if fig_risk:
            st.pyplot(fig_risk)
        else:
            st.info("Dados insuficientes para gráfico de risco")
    
    # Segunda linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Status das inspeções
        fig_status = create_status_chart(df_filtrado, user['perfil'], user['id'])
        if fig_status:
            st.pyplot(fig_status)
        else:
            st.info("Dados insuficientes para gráfico de status")
    
    with col2:
        # Performance por inspetor (apenas para coordenadores/gerência)
        if user['perfil'] in ['coordenador', 'gerencia']:
            fig_performance = create_inspector_performance_chart(df_filtrado)
            if fig_performance:
                st.pyplot(fig_performance)
            else:
                st.info("Dados insuficientes para gráfico de performance")
        else:
            # Para inspetores, mostrar evolução pessoal
            st.markdown("#### 📈 Sua Evolução")
            if len(df_filtrado) > 0:
                df_inspetor = df_filtrado[df_filtrado['inspetor_id'] == user['id']]
                if len(df_inspetor) > 0:
                    # Gráfico simples de evolução
                    df_inspetor_copy = df_inspetor.copy()
                    df_inspetor_copy['data_inspecao'] = pd.to_datetime(df_inspetor_copy['data_inspecao'])
                    df_inspetor_copy = df_inspetor_copy.sort_values('data_inspecao')
                    df_inspetor_copy['acumulado'] = range(1, len(df_inspetor_copy) + 1)
                    
                    fig, ax = plt.subplots()
                    ax.plot(df_inspetor_copy['data_inspecao'], df_inspetor_copy['acumulado'], marker='o')
                    ax.set_title('Suas Inspeções Acumuladas')
                    ax.set_xlabel('Data da Inspeção')
                    ax.set_ylabel('Inspeções Acumuladas')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Você ainda não possui inspeções no período selecionado")
            else:
                st.info("Nenhuma inspeção no período selecionado")
    
    st.markdown("---")
    
    # Tabela detalhada
    st.markdown("### 📋 Dados Detalhados")
    
    if len(df_filtrado) > 0:
        # Preparar dados para exibição
        display_df = df_filtrado.copy()
        
        # Filtrar por perfil
        if user['perfil'] == 'inspetor':
            display_df = display_df[display_df['inspetor_id'] == user['id']]
        
        # Formatar datas
        display_df['Data Inspeção'] = pd.to_datetime(display_df['data_inspecao']).dt.strftime('%d/%m/%Y')
        display_df['Prazo Inspetor'] = display_df['prazo_inspetor'].apply(
            lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notna(x) else '-'
        )
        display_df['Prazo Coordenação'] = display_df['prazo_coordenacao'].apply(
            lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notna(x) else '-'
        )
        
        # Selecionar colunas
        columns = ['estabelecimento', 'Data Inspeção', 'classificacao_risco', 
                  'Prazo Inspetor', 'Prazo Coordenação', 'status']
        
        if user['perfil'] in ['coordenador', 'gerencia']:
            columns.insert(-1, 'inspetor_id')
        
        # Renomear colunas
        column_names = {
            'estabelecimento': 'Estabelecimento',
            'classificacao_risco': 'Risco',
            'status': 'Status',
            'inspetor_id': 'Inspetor ID'
        }
        
        display_final = display_df[columns].rename(columns=column_names)
        
        st.dataframe(display_final, use_container_width=True, hide_index=True)
        
        # Exportar dados
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("📄 Exportar Relatório", use_container_width=True):
                export_path = data_manager.export_to_csv(display_df)
                if export_path:
                    st.success(f"✅ Relatório exportado para: {export_path}")
                    
                    # Informações sobre o arquivo
                    with st.expander("ℹ️ Informações do Arquivo"):
                        st.markdown(f"""
                        **Arquivo:** {export_path}
                        **Registros:** {len(display_df)}
                        **Período:** {periodo}
                        **Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                        """)
    else:
        st.info("Nenhuma inspeção encontrada no período selecionado.")

if __name__ == "__main__":
    main()


