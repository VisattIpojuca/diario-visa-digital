"""
Página para cadastro de nova inspeção
"""
import streamlit as st
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
    page_title="Nova Inspeção - VISA Digital",
    page_icon="📝",
    layout="wide"
)

# Verificar autenticação
auth_manager.require_auth()

def main():
    user = auth_manager.get_current_user()
    
    # Header
    st.markdown("# 📝 Nova Inspeção")
    st.markdown("Cadastre uma nova inspeção sanitária")
    
    # Formulário de cadastro
    with st.form("nova_inspecao_form", clear_on_submit=True):
        st.markdown("### 🏢 Dados do Estabelecimento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            estabelecimento = st.text_input(
                "Nome do Estabelecimento *",
                placeholder="Ex: Restaurante Bom Sabor",
                help="Nome completo do estabelecimento inspecionado"
            )
            
            atividade_principal = st.text_input(
                "Atividade Principal *",
                placeholder="Ex: Restaurante, Farmácia, Mercado",
                help="Principal atividade desenvolvida no estabelecimento"
            )
        
        with col2:
            cnpj = st.text_input(
                "CNPJ *",
                placeholder="00.000.000/0000-00",
                help="CNPJ do estabelecimento (apenas números ou formatado)"
            )
            
            classificacao_risco = st.selectbox(
                "Classificação de Risco *",
                options=["", "Baixo", "Médio", "Alto"],
                help="Classificação de risco sanitário do estabelecimento"
            )
        
        st.markdown("### 📅 Dados da Inspeção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_inspecao = st.date_input(
                "Data da Inspeção *",
                value=datetime.now().date(),
                max_value=datetime.now().date(),
                help="Data em que a inspeção foi realizada"
            )
            
            territorio = st.text_input(
                "Território",
                value=user.get('territorio', ''),
                help="Território onde está localizado o estabelecimento"
            )
        
        with col2:
            prazo_inspetor = st.date_input(
                "Prazo de Retorno",
                value=None,
                min_value=datetime.now().date(),
                help="Prazo definido pelo inspetor para retorno/regularização"
            )
        
        st.markdown("### 📝 Observações")
        
        observacoes = st.text_area(
            "Observações da Inspeção *",
            placeholder="Descreva os principais achados da inspeção, não conformidades encontradas, orientações dadas, etc.",
            height=150,
            help="Descrição detalhada dos achados da inspeção (mínimo 10 caracteres)"
        )
        
        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                "💾 Salvar Inspeção",
                use_container_width=True,
                type="primary"
            )
        
        with col3:
            if st.form_submit_button("🔄 Limpar Formulário", use_container_width=True):
                st.rerun()
    
    # Processar submissão do formulário
    if submitted:
        # Validações
        errors = []
        
        # Validar estabelecimento
        valid, msg = validators.validate_estabelecimento(estabelecimento)
        if not valid:
            errors.append(msg)
        
        # Validar CNPJ
        valid, msg = validators.validate_cnpj(cnpj)
        if not valid:
            errors.append(msg)
        
        # Validar atividade
        valid, msg = validators.validate_atividade(atividade_principal)
        if not valid:
            errors.append(msg)
        
        # Validar classificação de risco
        if not classificacao_risco:
            errors.append("Classificação de risco é obrigatória")
        
        # Validar data da inspeção
        valid, msg = validators.validate_data_inspecao(datetime.combine(data_inspecao, datetime.min.time()))
        if not valid:
            errors.append(msg)
        
        # Validar prazo (se informado)
        if prazo_inspetor:
            valid, msg = validators.validate_prazo(
                datetime.combine(prazo_inspetor, datetime.min.time()),
                datetime.combine(data_inspecao, datetime.min.time())
            )
            if not valid:
                errors.append(msg)
        
        # Validar observações
        valid, msg = validators.validate_observacoes(observacoes)
        if not valid:
            errors.append(msg)
        
        # Se há erros, exibir
        if errors:
            st.error("❌ Corrija os seguintes erros:")
            for error in errors:
                st.error(f"• {error}")
        else:
            # Preparar dados para salvamento
            inspecao_data = {
                'estabelecimento': estabelecimento.strip(),
                'cnpj': validators.format_cnpj(cnpj),
                'atividade_principal': atividade_principal.strip(),
                'classificacao_risco': classificacao_risco.lower(),
                'data_inspecao': data_inspecao,
                'observacoes': observacoes.strip(),
                'prazo_inspetor': prazo_inspetor,
                'territorio': territorio.strip() if territorio else user.get('territorio', '')
            }
            
            # Salvar inspeção
            if data_manager.create_inspecao(inspecao_data, user['id']):
                st.success("✅ Inspeção cadastrada com sucesso!")
                st.balloons()
                
                # Opções pós-cadastro
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📝 Cadastrar Nova Inspeção", use_container_width=True):
                        st.rerun()
                
                with col2:
                    if st.button("📋 Ver Minhas Inspeções", use_container_width=True):
                        st.switch_page("pages/03_📋_Minhas_Inspecoes.py")
            else:
                st.error("❌ Erro ao cadastrar inspeção. Tente novamente.")
    
    # Informações adicionais
    with st.expander("ℹ️ Informações sobre o Cadastro"):
        st.markdown("""
        **Campos Obrigatórios (*):**
        - Nome do Estabelecimento (mínimo 3 caracteres)
        - CNPJ (14 dígitos)
        - Atividade Principal (mínimo 3 caracteres)
        - Classificação de Risco
        - Data da Inspeção
        - Observações (mínimo 10 caracteres)
        
        **Dicas:**
        - A data da inspeção não pode ser futura
        - O prazo de retorno deve ser posterior à data da inspeção
        - Use observações detalhadas para facilitar o acompanhamento
        - O CNPJ pode ser digitado com ou sem formatação
        """)

if __name__ == "__main__":
    main()

