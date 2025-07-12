"""
Gerenciador de dados CSV para o Diário de Campo Digital
"""
import pandas as pd
import streamlit as st
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.inspecoes_file = os.path.join(data_dir, "inspecoes.csv")
        self.ensure_data_files()
    
    def ensure_data_files(self):
        """Garante que os arquivos de dados existem"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.inspecoes_file):
            # Criar arquivo de inspeções vazio com estrutura
            empty_df = pd.DataFrame(columns=[
                'id', 'estabelecimento', 'cnpj', 'atividade_principal',
                'classificacao_risco', 'data_inspecao', 'observacoes',
                'prazo_inspetor', 'prazo_coordenacao', 'status',
                'inspetor_id', 'territorio', 'data_criacao',
                'data_atualizacao', 'comentarios_internos'
            ])
            empty_df.to_csv(self.inspecoes_file, index=False)
    
    def load_inspecoes(self) -> pd.DataFrame:
        """Carrega dados das inspeções"""
        try:
            df = pd.read_csv(self.inspecoes_file)
            # Converter datas
            date_columns = ['data_inspecao', 'prazo_inspetor', 'prazo_coordenacao', 
                          'data_criacao', 'data_atualizacao']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Erro ao carregar inspeções: {e}")
            return pd.DataFrame()
    
    def save_inspecoes(self, df: pd.DataFrame):
        """Salva dados das inspeções"""
        try:
            df.to_csv(self.inspecoes_file, index=False)
        except Exception as e:
            st.error(f"Erro ao salvar inspeções: {e}")
    
    def create_inspecao(self, data: Dict[str, Any], user_id: int) -> bool:
        """Cria nova inspeção"""
        try:
            df = self.load_inspecoes()
            
            # Gerar ID único
            new_id = str(uuid.uuid4())
            
            # Preparar dados da nova inspeção
            new_inspecao = {
                'id': new_id,
                'estabelecimento': data['estabelecimento'],
                'cnpj': data['cnpj'],
                'atividade_principal': data['atividade_principal'],
                'classificacao_risco': data['classificacao_risco'],
                'data_inspecao': data['data_inspecao'],
                'observacoes': data['observacoes'],
                'prazo_inspetor': data.get('prazo_inspetor'),
                'prazo_coordenacao': None,
                'status': 'pendente',
                'inspetor_id': user_id,
                'territorio': data.get('territorio', ''),
                'data_criacao': datetime.now(),
                'data_atualizacao': datetime.now(),
                'comentarios_internos': ''
            }
            
            # Adicionar nova linha
            new_df = pd.concat([df, pd.DataFrame([new_inspecao])], ignore_index=True)
            self.save_inspecoes(new_df)
            return True
        except Exception as e:
            st.error(f"Erro ao criar inspeção: {e}")
            return False
    
    def update_inspecao(self, inspecao_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza inspeção existente"""
        try:
            df = self.load_inspecoes()
            mask = df['id'] == inspecao_id
            
            if not mask.any():
                st.error("Inspeção não encontrada")
                return False
            
            # Atualizar dados
            for key, value in data.items():
                if key in df.columns:
                    df.loc[mask, key] = value
            
            df.loc[mask, 'data_atualizacao'] = datetime.now()
            self.save_inspecoes(df)
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar inspeção: {e}")
            return False
    
    def get_inspecoes_by_user(self, user_id: int, user_profile: str) -> pd.DataFrame:
        """Retorna inspeções filtradas por usuário"""
        df = self.load_inspecoes()
        
        if user_profile == 'inspetor':
            # Inspetores veem apenas suas inspeções
            return df[df['inspetor_id'] == user_id]
        else:
            # Coordenadores e gerência veem todas
            return df
    
    def get_inspecoes_vencidas(self) -> pd.DataFrame:
        """Retorna inspeções vencidas"""
        df = self.load_inspecoes()
        hoje = datetime.now().date()
        
        # Verificar prazos do inspetor e coordenação
        mask_vencidas = (
            ((df['prazo_inspetor'].dt.date < hoje) | 
             (df['prazo_coordenacao'].dt.date < hoje)) &
            (df['status'] == 'pendente')
        )
        
        return df[mask_vencidas]
    
    def get_inspecoes_proximas_vencimento(self, dias: int = 3) -> pd.DataFrame:
        """Retorna inspeções próximas do vencimento"""
        df = self.load_inspecoes()
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=dias)
        
        mask_proximas = (
            ((df['prazo_inspetor'].dt.date <= limite) | 
             (df['prazo_coordenacao'].dt.date <= limite)) &
            ((df['prazo_inspetor'].dt.date >= hoje) | 
             (df['prazo_coordenacao'].dt.date >= hoje)) &
            (df['status'] == 'pendente')
        )
        
        return df[mask_proximas]
    
    def get_estatisticas(self, user_id: int = None, user_profile: str = None) -> Dict[str, Any]:
        """Retorna estatísticas das inspeções"""
        df = self.load_inspecoes()
        
        if user_profile == 'inspetor' and user_id:
            df = df[df['inspetor_id'] == user_id]
        
        total = len(df)
        pendentes = len(df[df['status'] == 'pendente'])
        concluidas = len(df[df['status'] == 'concluido'])
        vencidas = len(self.get_inspecoes_vencidas())
        
        return {
            'total': total,
            'pendentes': pendentes,
            'concluidas': concluidas,
            'vencidas': vencidas,
            'percentual_cumprimento': (concluidas / total * 100) if total > 0 else 0
        }
    
    def export_to_csv(self, df: pd.DataFrame) -> str:
        """Exporta DataFrame para CSV e retorna o caminho"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_inspecoes_{timestamp}.csv"
            filepath = os.path.join(self.data_dir, filename)
            df.to_csv(filepath, index=False)
            return filepath
        except Exception as e:
            st.error(f"Erro ao exportar dados: {e}")
            return None

# Instância global do gerenciador de dados
data_manager = DataManager()

