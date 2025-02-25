# Refactool

Uma ferramenta poderosa para análise e refatoração de código, com suporte a múltiplas linguagens e integração com IA.

## 🚀 Funcionalidades

- 📊 Análise estática de código multi-linguagem
- 🤖 Análise semântica com IA (DeepSeek e Ollama)
- 🔄 Sistema de webhooks para notificações
- 📝 Geração de relatórios detalhados
- 🔍 Detecção de code smells e sugestões de melhoria
- 🔗 Integração direta com GitHub

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Git
- Ollama (opcional, para análise local)
- Chave API do DeepSeek (opcional, para análise em nuvem)
- Token do GitHub (para integração com repositórios)

## 🛠️ Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/refactool.git
   cd refactool
   ```

2. Instale as dependências:
   ```bash
   pip install -r microservices/source-provider/src/requirements.txt
   ```

3. Configure o ambiente:
   ```bash
   cp microservices/source-provider/src/.env.example microservices/source-provider/src/.env
   ```

## ⚙️ Configuração

### Arquivo .env

```env
# Configurações do DeepSeek
DEEPSEEK_API_KEY=sua-chave-api-aqui
DEEPSEEK_MODEL=deepseek-coder-33b-instruct
DEEPSEEK_TEMPERATURE=0.3
DEEPSEEK_MAX_TOKENS=2000
DEEPSEEK_CHUNK_SIZE=1000

# Configurações do Ollama
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=codellama
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=2000
OLLAMA_CHUNK_SIZE=1000

# Configurações de Webhook
DISCORD_WEBHOOK_URL=sua-url-webhook-aqui

# Configurações do GitHub
GITHUB_TOKEN=seu-token-aqui
GITHUB_API_URL=https://api.github.com
```

### Configuração do GitHub

1. Gere um token de acesso pessoal:
   - Acesse GitHub > Settings > Developer settings > Personal access tokens
   - Clique em "Generate new token"
   - Selecione os escopos: `repo`, `workflow`
   - Copie o token e adicione ao seu `.env`

2. Configure as credenciais do Git:
   ```bash
   git config --global user.name "Seu Nome"
   git config --global user.email "seu@email.com"
   ```

### Configuração do Ollama (Opcional)

1. Instale o Ollama:
   ```bash
   # Linux/MacOS
   curl https://ollama.ai/install.sh | sh
   
   # Windows
   # Baixe o instalador em https://ollama.ai/download
   ```

2. Execute o modelo CodeLlama:
   ```bash
   ollama run codellama
   ```

## 📊 Uso

### Análise de Repositório GitHub

1. Análise direta via URL:
   ```python
   from analyzers import RefactoolAnalyzer
   from github_integration import GitHubManager

   async def analisar_repositorio_github():
       github = GitHubManager(os.getenv("GITHUB_TOKEN"))
       analyzer = RefactoolAnalyzer()
       
       # Analisa diretamente do GitHub
       await analyzer.analyze_github_repo(
           "usuario/repositorio",
           branch="main"
       )
   ```

2. Análise e criação de Pull Request:
   ```python
   async def analisar_e_criar_pr():
       github = GitHubManager(os.getenv("GITHUB_TOKEN"))
       analyzer = RefactoolAnalyzer()
       
       # Analisa e cria PR com sugestões
       results = await analyzer.analyze_github_repo(
           "usuario/repositorio",
           create_pull_request=True,
           pr_title="refactor: Melhorias sugeridas pela Refactool",
           pr_body="Sugestões automáticas de refatoração"
       )
   ```

3. Análise de Pull Request específico:
   ```python
   async def analisar_pull_request():
       github = GitHubManager(os.getenv("GITHUB_TOKEN"))
       analyzer = RefactoolAnalyzer()
       
       # Analisa um PR específico
       await analyzer.analyze_github_pr(
           "usuario/repositorio",
           pr_number=123
       )
   ```

### Análise de Repositório Local

```bash
cd microservices/source-provider/src/analyzers/examples
python analyze_project.py /caminho/do/seu/projeto
```

### Análise via API

```python
from analyzers import RefactoolAnalyzer

async def analisar_projeto():
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project("/caminho/do/projeto")
```

## 📄 Relatórios

Os relatórios são gerados em `reports/refactool_analysis.txt` e incluem:

- Visão geral do projeto
- Linguagens utilizadas
- Dependências encontradas
- Code smells e sugestões
- Recomendações da IA

## 🔔 Webhooks

Configure webhooks para receber notificações sobre:

- Conclusão da análise
- Problemas críticos encontrados
- Sugestões de melhoria
- Atualizações de Pull Requests

Exemplo de configuração:
```python
from webhook_manager import WebhookManager, WebhookConfig

webhook_config = WebhookConfig(
    url="sua-url-webhook",
    event_types=["analysis.completed", "critical.issue", "pr.created"],
    retry_count=3
)

manager = WebhookManager()
manager.register_webhook(webhook_config)
```

## 🎯 Exemplos de Uso

### Análise Básica
```python
from analyzers import RefactoolAnalyzer

async def analise_basica():
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_project("./meu-projeto")
```

### Análise com Filtros
```python
from analyzers import RefactoolAnalyzer

async def analise_com_filtros():
    analyzer = RefactoolAnalyzer()
    analyzer.code_analyzer.config.max_complexity = 15
    analyzer.code_analyzer.config.max_method_lines = 50
    await analyzer.analyze_project("./meu-projeto")
```

### Análise com Webhook e GitHub
```python
from analyzers import RefactoolAnalyzer
from webhook_manager import WebhookManager, WebhookConfig
from github_integration import GitHubManager

async def analise_completa():
    # Configura webhook
    webhook = WebhookConfig(
        url=os.getenv("DISCORD_WEBHOOK_URL"),
        event_types=["analysis.completed", "pr.created"]
    )
    
    # Inicializa gerenciadores
    webhook_manager = WebhookManager()
    webhook_manager.register_webhook(webhook)
    
    github = GitHubManager(os.getenv("GITHUB_TOKEN"))
    
    # Executa análise e cria PR
    analyzer = RefactoolAnalyzer()
    await analyzer.analyze_github_repo(
        "usuario/repositorio",
        create_pull_request=True
    )
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: nova funcionalidade'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a GNU Lesser General Public License v3.0. Veja o arquivo [LICENCE](LICENCE) para mais detalhes.

## 🔗 Links Úteis

- [Documentação do DeepSeek](https://platform.deepseek.ai/)
- [Documentação do Ollama](https://ollama.ai/docs)
- [Documentação da API do GitHub](https://docs.github.com/en/rest)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Código de Conduta](CODE_OF_CONDUCT.md)
