"""
Sistema de autenticação para o Diário de Campo Digital
"""
import streamlit as st
import pandas as pd
import bcrypt
import os
from typing import Optional, Dict, Any

class AuthManager:
    def __init__(self, users_file: str = "data/usuarios.csv"):
        self.users_file = users_file
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Garante que o arquivo de usuários existe com dados iniciais"""
        if not os.path.exists(self.users_file):
            # Criar usuários padrão
            default_users = pd.DataFrame([
                {
                    'id': 1,
                    'username': 'admin',
                    'password': self.hash_password('admin123'),
                    'nome': 'Administrador',
                    'perfil': 'gerencia',
                    'territorio': 'Todos',
                    'ativo': True
                },
                {
                    'id': 2,
                    'username': 'coord1',
                    'password': self.hash_password('coord123'),
                    'nome': 'Coordenador Teste',
                    'perfil': 'coordenador',
                    'territorio': 'Centro',
                    'ativo': True
                },
                {
                    'id': 3,
                    'username': 'insp1',
                    'password': self.hash_password('insp123'),
                    'nome': 'Inspetor Teste',
                    'perfil': 'inspetor',
                    'territorio': 'Norte',
                    'ativo': True
                }
            ])
            default_users.to_csv(self.users_file, index=False)
    
    def hash_password(self, password: str) -> str:
        """Gera hash da senha"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha confere com o hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica usuário e retorna dados se válido"""
        try:
            users_df = pd.read_csv(self.users_file)
            user = users_df[users_df['username'] == username]
            
            if len(user) == 1 and user.iloc[0]['ativo']:
                user_data = user.iloc[0].to_dict()
                if self.verify_password(password, user_data['password']):
                    # Remove senha dos dados retornados
                    del user_data['password']
                    return user_data
            return None
        except Exception as e:
            st.error(f"Erro na autenticação: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Verifica se há usuário autenticado na sessão"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retorna dados do usuário atual"""
        if self.is_authenticated():
            return st.session_state.user
        return None
    
    def login(self, username: str, password: str) -> bool:
        """Realiza login do usuário"""
        user = self.authenticate(username, password)
        if user:
            st.session_state.user = user
            return True
        return False
    
    def logout(self):
        """Realiza logout do usuário"""
        if 'user' in st.session_state:
            del st.session_state.user
        st.rerun()
    
    def require_auth(self, allowed_profiles: list = None):
        """Decorator/função para exigir autenticação"""
        if not self.is_authenticated():
            st.error("Acesso negado. Faça login para continuar.")
            st.stop()
        
        if allowed_profiles:
            user = self.get_current_user()
            if user['perfil'] not in allowed_profiles:
                st.error("Você não tem permissão para acessar esta página.")
                st.stop()
    
    def has_permission(self, required_profile: str) -> bool:
        """Verifica se o usuário tem permissão específica"""
        if not self.is_authenticated():
            return False
        
        user = self.get_current_user()
        user_profile = user['perfil']
        
        # Hierarquia de permissões
        hierarchy = {
            'inspetor': 1,
            'coordenador': 2,
            'gerencia': 3
        }
        
        return hierarchy.get(user_profile, 0) >= hierarchy.get(required_profile, 0)

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()

