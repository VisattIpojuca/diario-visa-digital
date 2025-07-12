"""
Validadores de dados para o Diário de Campo Digital
"""
import re
from datetime import datetime
from typing import Tuple, Optional

class Validators:
    @staticmethod
    def validate_cnpj(cnpj: str) -> Tuple[bool, str]:
        """Valida CNPJ"""
        if not cnpj:
            return False, "CNPJ é obrigatório"
        
        # Remove caracteres não numéricos
        cnpj_numbers = re.sub(r'\D', '', cnpj)
        
        if len(cnpj_numbers) != 14:
            return False, "CNPJ deve ter 14 dígitos"
        
        # Validação básica (pode ser expandida)
        if cnpj_numbers == cnpj_numbers[0] * 14:
            return False, "CNPJ inválido"
        
        return True, ""
    
    @staticmethod
    def validate_estabelecimento(nome: str) -> Tuple[bool, str]:
        """Valida nome do estabelecimento"""
        if not nome or len(nome.strip()) < 3:
            return False, "Nome do estabelecimento deve ter pelo menos 3 caracteres"
        
        if len(nome) > 200:
            return False, "Nome do estabelecimento muito longo (máximo 200 caracteres)"
        
        return True, ""
    
    @staticmethod
    def validate_atividade(atividade: str) -> Tuple[bool, str]:
        """Valida atividade principal"""
        if not atividade or len(atividade.strip()) < 3:
            return False, "Atividade principal deve ter pelo menos 3 caracteres"
        
        if len(atividade) > 100:
            return False, "Atividade principal muito longa (máximo 100 caracteres)"
        
        return True, ""
    
    @staticmethod
    def validate_data_inspecao(data: datetime) -> Tuple[bool, str]:
        """Valida data da inspeção"""
        if not data:
            return False, "Data da inspeção é obrigatória"
        
        hoje = datetime.now().date()
        if data.date() > hoje:
            return False, "Data da inspeção não pode ser futura"
        
        # Não pode ser muito antiga (mais de 1 ano)
        if (hoje - data.date()).days > 365:
            return False, "Data da inspeção muito antiga (máximo 1 ano)"
        
        return True, ""
    
    @staticmethod
    def validate_prazo(prazo: Optional[datetime], data_inspecao: datetime) -> Tuple[bool, str]:
        """Valida prazo de retorno"""
        if not prazo:
            return True, ""  # Prazo é opcional
        
        if prazo.date() <= data_inspecao.date():
            return False, "Prazo deve ser posterior à data da inspeção"
        
        # Prazo não pode ser muito distante (mais de 1 ano)
        if (prazo.date() - data_inspecao.date()).days > 365:
            return False, "Prazo muito distante (máximo 1 ano)"
        
        return True, ""
    
    @staticmethod
    def validate_observacoes(observacoes: str) -> Tuple[bool, str]:
        """Valida observações"""
        if not observacoes or len(observacoes.strip()) < 10:
            return False, "Observações devem ter pelo menos 10 caracteres"
        
        if len(observacoes) > 2000:
            return False, "Observações muito longas (máximo 2000 caracteres)"
        
        return True, ""
    
    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        """Formata CNPJ para exibição"""
        cnpj_numbers = re.sub(r'\D', '', cnpj)
        if len(cnpj_numbers) == 14:
            return f"{cnpj_numbers[:2]}.{cnpj_numbers[2:5]}.{cnpj_numbers[5:8]}/{cnpj_numbers[8:12]}-{cnpj_numbers[12:]}"
        return cnpj

# Instância global dos validadores
validators = Validators()

