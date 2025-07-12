"""
Diário de Campo Digital para Inspetores Sanitários
Aplicação principal - Sistema de Login
"""
import streamlit as st
import os
import sys

# Adicionar o diretório atual ao path para importar utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.auth import auth_manager
from utils.notifications import notification_manager

# Configuração da página
st.set_page_config(
    page_title="VISA - Diário Digital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def show_login_page():
    """Exibe a página de login"""
    st.markdown("""
    <div class="main-header">
        <h1>🏥 VISA - Diário Digital</h1>
        <p>Sistema de Gestão de Inspeções Sanitárias</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Container de login centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("### 🔐 Acesso ao Sistema")
        
        # Formulário de login
        with st.form("login_form"):
            username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            submit_button = st.form_submit_button("🚀 Entrar", use_container_width=True)
            
            if submit_button:
                if username and password:
                    if auth_manager.login(username, password):
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos!")
                else:
                    st.warning("⚠️ Preencha todos os campos!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informações de teste
        with st.expander("ℹ️ Usuários de Teste"):
            st.markdown("""
            **Administrador/Gerência:**
            - Usuário: `admin`
            - Senha: `admin123`
            
            **Coordenador:**
            - Usuário: `coord1`
            - Senha: `coord123`
            
            **Inspetor:**
            - Usuário: `insp1`
            - Senha: `insp123`
            """)

def show_main_app():
    """Exibe a aplicação principal após login"""
    user = auth_manager.get_current_user()
    
    # Header da aplicação
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="main-header">
            <h2>🏥 VISA - Diário Digital</h2>
            <p>Bem-vindo(a), {user['nome']} ({user['perfil'].title()})</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            auth_manager.logout()
    
    # Sidebar com notificações
    with st.sidebar:
        st.markdown(f"### 👤 {user['nome']}")
        st.markdown(f"**Perfil:** {user['perfil'].title()}")
        if user['territorio']:
            st.markdown(f"**Território:** {user['territorio']}")
        
        st.markdown("---")
        
        # Exibir notificações
        notification_manager.show_notifications_sidebar(user['id'], user['perfil'])
    
    # Conteúdo principal - Dashboard básico
    st.markdown("### 🏠 Dashboard")
    
    # Exibir alertas
    notification_manager.show_dashboard_alerts(user['id'], user['perfil'])
    
    # Estatísticas básicas
    from utils.data_manager import data_manager
    stats = data_manager.get_estatisticas(user['id'], user['perfil'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total de Inspeções", stats['total'])
    
    with col2:
        st.metric("⏳ Pendentes", stats['pendentes'])
    
    with col3:
        st.metric("✅ Concluídas", stats['concluidas'])
    
    with col4:
        st.metric("🔴 Vencidas", stats['vencidas'])
    
    # Informações sobre navegação
    st.markdown("---")
    st.markdown("""
    ### 📱 Navegação
    
    Use o menu lateral para acessar as diferentes funcionalidades:
    
    - **🏠 Dashboard**: Visão geral e alertas
    - **📝 Nova Inspeção**: Cadastrar nova inspeção
    - **📋 Minhas Inspeções**: Listar e gerenciar inspeções
    - **👥 Painel Coordenação**: Gestão de processos (coordenadores/gerência)
    - **📊 Indicadores**: Relatórios e estatísticas
    """)

def main():
    """Função principal da aplicação"""
    # Verificar se o usuário está autenticado
    if not auth_manager.is_authenticated():
        show_login_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()

