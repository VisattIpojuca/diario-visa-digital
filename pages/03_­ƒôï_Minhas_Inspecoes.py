"""
Página para listar e gerenciar inspeções
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import auth_manager
from utils.data_manager import data_manager
from utils.validators import validators

# Configuração da página
st.set_page_config(
    page_title="Minhas Inspeções - VISA Digital",
    page_icon="📋",
    layout="wide"
)

# Verificar autenticação
auth_manager.require_auth()

def format_status_display(status, prazo_inspetor, prazo_coordenacao):
    """Formata o status para exibição com ícones"""
    hoje = datetime.now().date()
    
    if status == 'concluido':
        return "✅ Concluído"
    
    # Verificar se está vencido
    vencido = False
    if prazo_inspetor and pd.notna(prazo_inspetor):
        if prazo_inspetor.date() < hoje:
            vencido = True
    
    if prazo_coordenacao and pd.notna(prazo_coordenacao):
        if prazo_coordenacao.date() < hoje:
            vencido = True
    
    if vencido:
        return "🔴 Vencido"
    
    # Verificar se está próximo do vencimento (3 dias)
    proximo = False
    if prazo_inspetor and pd.notna(prazo_inspetor):
        if prazo_inspetor.date() <= hoje + timedelta(days=3):
            proximo = True
    
    if prazo_coordenacao and pd.notna(prazo_coordenacao):
        if prazo_coordenacao.date() <= hoje + timedelta(days=3):
            proximo = True
    
    if proximo:
        return "🟡 Próximo Vencimento"
    
    return "🟢 Pendente"

def show_details_modal(inspecao, user):
    """Exibe detalhes da inspeção em modal"""
    st.markdown("### 👁️ Detalhes da Inspeção")
    st.markdown(f"**Estabelecimento:** {inspecao['estabelecimento']}")
    st.markdown(f"**CNPJ:** {inspecao['cnpj']}")
    st.markdown(f"**Atividade:** {inspecao['atividade_principal']}")
    st.markdown(f"**Risco:** {inspecao['classificacao_risco'].title()}")
    st.markdown(f"**Data da Inspeção:** {inspecao['data_inspecao'].strftime('%d/%m/%Y')}")
    
    if pd.notna(inspecao['prazo_inspetor']):
        st.markdown(f"**Prazo Inspetor:** {inspecao['prazo_inspetor'].strftime('%d/%m/%Y')}")
    
    if pd.notna(inspecao['prazo_coordenacao']):
        st.markdown(f"**Prazo Coordenação:** {inspecao['prazo_coordenacao'].strftime('%d/%m/%Y')}")
    
    st.markdown(f"**Território:** {inspecao.get('territorio', 'Não informado')}")
    st.markdown(f"**Status:** {inspecao['status'].title()}")
    
    st.markdown("**Observações:**")
    st.text_area("", value=inspecao['observacoes'], disabled=True, height=100, key="obs_details")
    
    if user['perfil'] in ['coordenador', 'gerencia'] and inspecao.get('comentarios_internos'):
        st.markdown("**Comentários Internos:**")
        st.text_area("", value=inspecao['comentarios_internos'], disabled=True, height=80, key="com_details")

def main():
    user = auth_manager.get_current_user()
    
    # Header
    if user['perfil'] == 'inspetor':
        st.markdown("# 📋 Minhas Inspeções")
    else:
        st.markdown("# 📋 Todas as Inspeções")
    
    # Carregar dados
    df = data_manager.get_inspecoes_by_user(user['id'], user['perfil'])
    
    if len(df) == 0:
        st.info("Nenhuma inspeção cadastrada ainda.")
        if st.button("📝 Cadastrar Nova Inspeção"):
            st.switch_page("pages/02_📝_Nova_Inspecao.py")
        return
    
    # Filtros
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        busca_texto = st.text_input(
            "🔍 Buscar",
            placeholder="Nome do estabelecimento...",
            help="Buscar por nome do estabelecimento"
        )
    
    with col2:
        filtro_risco = st.selectbox(
            "⚠️ Risco",
            options=["Todos", "Alto", "Médio", "Baixo"]
        )
    
    with col3:
        filtro_status = st.selectbox(
            "📊 Status",
            options=["Todos", "Pendente", "Vencido", "Próximo Vencimento", "Concluído"]
        )
    
    with col4:
        if user['perfil'] in ['coordenador', 'gerencia']:
            # Filtro por inspetor (apenas para coordenadores/gerência)
            inspetores_unicos = df['inspetor_id'].unique()
            filtro_inspetor = st.selectbox(
                "👤 Inspetor",
                options=["Todos"] + list(inspetores_unicos)
            )
        else:
            filtro_inspetor = "Todos"
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    # Filtro por texto
    if busca_texto:
        df_filtrado = df_filtrado[
            df_filtrado['estabelecimento'].str.contains(busca_texto, case=False, na=False)
        ]
    
    # Filtro por risco
    if filtro_risco != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado['classificacao_risco'].str.title() == filtro_risco
        ]
    
    # Filtro por status
    if filtro_status != "Todos":
        hoje = datetime.now().date()
        
        if filtro_status == "Concluído":
            df_filtrado = df_filtrado[df_filtrado['status'] == 'concluido']
        elif filtro_status == "Vencido":
            mask_vencido = (
                ((df_filtrado['prazo_inspetor'].dt.date < hoje) | 
                 (df_filtrado['prazo_coordenacao'].dt.date < hoje)) &
                (df_filtrado['status'] == 'pendente')
            )
            df_filtrado = df_filtrado[mask_vencido]
        elif filtro_status == "Próximo Vencimento":
            limite = hoje + timedelta(days=3)
            mask_proximo = (
                ((df_filtrado['prazo_inspetor'].dt.date <= limite) | 
                 (df_filtrado['prazo_coordenacao'].dt.date <= limite)) &
                ((df_filtrado['prazo_inspetor'].dt.date >= hoje) | 
                 (df_filtrado['prazo_coordenacao'].dt.date >= hoje)) &
                (df_filtrado['status'] == 'pendente')
            )
            df_filtrado = df_filtrado[mask_proximo]
        elif filtro_status == "Pendente":
            hoje = datetime.now().date()
            mask_pendente = (
                (df_filtrado['status'] == 'pendente') &
                ((df_filtrado['prazo_inspetor'].dt.date > hoje) | 
                 (df_filtrado['prazo_coordenacao'].dt.date > hoje) |
                 (df_filtrado['prazo_inspetor'].isna() & df_filtrado['prazo_coordenacao'].isna()))
            )
            df_filtrado = df_filtrado[mask_pendente]
    
    # Filtro por inspetor
    if filtro_inspetor != "Todos":
        df_filtrado = df_filtrado[df_filtrado['inspetor_id'] == filtro_inspetor]
    
    # Exibir resultados
    st.markdown(f"### 📊 Resultados ({len(df_filtrado)} registros)")
    
    if len(df_filtrado) == 0:
        st.warning("Nenhuma inspeção encontrada com os filtros aplicados.")
        return
    
    # Preparar dados para exibição
    display_df = df_filtrado.copy()
    
    # Formatar datas
    display_df['Data Inspeção'] = pd.to_datetime(display_df['data_inspecao']).dt.strftime('%d/%m/%Y')
    
    # Formatar prazos
    display_df['Prazo Inspetor'] = display_df['prazo_inspetor'].apply(
        lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else '-'
    )
    
    display_df['Prazo Coordenação'] = display_df['prazo_coordenacao'].apply(
        lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else '-'
    )
    
    # Adicionar status formatado
    display_df['Status'] = display_df.apply(
        lambda row: format_status_display(row['status'], row['prazo_inspetor'], row['prazo_coordenacao']),
        axis=1
    )
    
    # Selecionar colunas para exibição
    columns_to_show = [
        'estabelecimento', 'Data Inspeção', 'classificacao_risco', 
        'Prazo Inspetor', 'Prazo Coordenação', 'Status'
    ]
    
    if user['perfil'] in ['coordenador', 'gerencia']:
        columns_to_show.insert(-1, 'inspetor_id')
    
    # Renomear colunas
    column_names = {
        'estabelecimento': 'Estabelecimento',
        'classificacao_risco': 'Risco',
        'inspetor_id': 'Inspetor ID'
    }
    
    display_final = display_df[columns_to_show].rename(columns=column_names)
    
    # Exibir tabela
    st.dataframe(
        display_final,
        use_container_width=True,
        hide_index=True
    )
    
    # Seleção de registro para ações
    if len(df_filtrado) > 0:
        st.markdown("### 🔧 Ações")
        
        # Selectbox para escolher inspeção
        opcoes_inspecao = [f"{row['estabelecimento']} - {row['data_inspecao'].strftime('%d/%m/%Y')}" 
                          for _, row in df_filtrado.iterrows()]
        
        if opcoes_inspecao:
            selected_option = st.selectbox(
                "Selecionar inspeção para ação:",
                options=["Selecione..."] + opcoes_inspecao
            )
            
            if selected_option != "Selecione...":
                selected_idx = opcoes_inspecao.index(selected_option)
                selected_inspecao = df_filtrado.iloc[selected_idx]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("👁️ Ver Detalhes", use_container_width=True):
                        show_details_modal(selected_inspecao, user)
                
                with col2:
                    if user['perfil'] in ['coordenador', 'gerencia'] or selected_inspecao['inspetor_id'] == user['id']:
                        if st.button("✏️ Editar", use_container_width=True):
                            st.info("Funcionalidade de edição será implementada em modal separado.")
                
                with col3:
                    if user['perfil'] in ['coordenador', 'gerencia']:
                        if st.button("💬 Comentários", use_container_width=True):
                            st.info("Funcionalidade de comentários será implementada em modal separado.")
    
    # Botões de ação geral
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Nova Inspeção", use_container_width=True):
            st.switch_page("pages/02_📝_Nova_Inspecao.py")
    
    with col2:
        if st.button("📊 Exportar CSV", use_container_width=True):
            export_path = data_manager.export_to_csv(df_filtrado)
            if export_path:
                st.success(f"✅ Dados exportados para: {export_path}")
    
    with col3:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()

