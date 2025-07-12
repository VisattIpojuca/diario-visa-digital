# Diário de Campo Digital - VISA

Sistema de gestão de inspeções sanitárias desenvolvido em Streamlit para inspetores da Vigilância Sanitária.

## 📋 Funcionalidades

### Para Inspetores
- ✅ Cadastro de novas inspeções
- ✅ Visualização e gerenciamento das próprias inspeções
- ✅ Dashboard com estatísticas pessoais
- ✅ Sistema de notificações e lembretes

### Para Coordenadores
- ✅ Painel de coordenação com visão geral da equipe
- ✅ Gestão de processos críticos e vencidos
- ✅ Atribuição de tarefas e definição de prazos
- ✅ Relatórios detalhados

### Para Gerência
- ✅ Dashboard de indicadores gerais
- ✅ Relatórios e análises estatísticas
- ✅ Visão completa de todas as inspeções
- ✅ Exportação de dados

## 🚀 Como Usar

### Acesso ao Sistema
1. Acesse a aplicação através do link fornecido
2. Faça login com suas credenciais

### Usuários de Teste
- **Administrador/Gerência:** `admin` / `admin123`
- **Coordenador:** `coord1` / `coord123`
- **Inspetor:** `insp1` / `insp123`

### Navegação
- Use o menu lateral para navegar entre as páginas
- **Dashboard:** Visão geral e estatísticas
- **Nova Inspeção:** Cadastrar nova inspeção
- **Minhas Inspeções:** Listar e gerenciar inspeções
- **Painel Coordenação:** Gestão de equipe (coordenadores)
- **Indicadores:** Relatórios e análises (gerência)

## 📊 Estrutura de Dados

### Inspeções
- Dados do estabelecimento (nome, CNPJ, atividade)
- Classificação de risco (alto, médio, baixo)
- Datas e prazos (inspeção, retorno, coordenação)
- Status (pendente, concluído)
- Observações e comentários

### Usuários
- Perfis: inspetor, coordenador, gerencia
- Controle de acesso baseado em perfil
- Territórios de atuação

## 🛠️ Tecnologias

- **Frontend:** Streamlit
- **Backend:** Python + Pandas
- **Dados:** CSV (persistência local)
- **Gráficos:** Plotly
- **Autenticação:** bcrypt

## 📁 Estrutura do Projeto

```
diario_visat/
├── app.py                 # Aplicação principal
├── pages/                 # Páginas do sistema
│   ├── 01_🏠_Dashboard.py
│   ├── 02_📝_Nova_Inspecao.py
│   ├── 03_📋_Minhas_Inspecoes.py
│   ├── 04_👥_Painel_Coordenacao.py
│   └── 05_📊_Indicadores.py
├── utils/                 # Utilitários
│   ├── auth.py           # Sistema de autenticação
│   ├── data_manager.py   # Gerenciamento de dados
│   ├── notifications.py  # Sistema de notificações
│   └── validators.py     # Validadores
├── data/                 # Dados persistidos
└── requirements.txt      # Dependências
```

## 🔧 Instalação Local

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

## 📈 Indicadores Disponíveis

- Total de inspeções por período
- Distribuição por classificação de risco
- Taxa de conclusão de inspeções
- Processos vencidos e próximos do vencimento
- Performance por inspetor
- Análise temporal de inspeções

## 🔒 Segurança

- Autenticação obrigatória
- Controle de acesso baseado em perfil
- Senhas criptografadas com bcrypt
- Validação de dados de entrada

## 📞 Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.

---

**Desenvolvido para a Vigilância Sanitária**
*Sistema de Diário de Campo Digital v1.0*

