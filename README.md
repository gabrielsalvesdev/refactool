# Refactool Analisador de Código

Este projeto é uma ferramenta de análise de código que utiliza múltiplos provedores de IA para fornecer sugestões de melhoria em projetos. Por padrão, utiliza o Google Gemini, mas suporta integração com outros provedores.

## Funcionalidades

- Análise estática de código
- Sugestões de melhoria em português do Brasil
- Suporte a múltiplos provedores de IA:
  - Google Gemini (padrão)
  - OpenAI GPT
  - DeepSeek
  - Ollama (para execução local)
- Análise de repositórios Git
- Relatórios detalhados em formato JSON
- Configuração flexível de provedores de IA

## Requisitos

- Python 3.8+
- Git instalado
- Pelo menos uma das seguintes chaves de API:
  - Google Gemini API Key
  - OpenAI API Key
  - DeepSeek API Key
  - Ollama instalado localmente (opcional)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/refactool-beta.git
cd refactool-beta
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env`:
```env
# Configuração do Gemini (Padrão)
GEMINI_API_KEY=sua-chave-api-aqui

# Configuração do Git (Windows)
GIT_PYTHON_GIT_EXECUTABLE=C:\Program Files\Git\bin\git.exe

# Configurações Opcionais de Outros Provedores
OPENAI_API_KEY=sua-chave-openai-aqui
DEEPSEEK_API_KEY=sua-chave-deepseek-aqui
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama2:13b
```

## Uso

### Análise Básica
Para analisar um repositório usando o provedor padrão (Gemini):

```bash
python analyze_repo.py https://github.com/usuario/repositorio
```

### Análise com Provedor Específico
Para especificar qual provedor de IA usar:

```bash
# Usando OpenAI
python analyze_repo.py https://github.com/usuario/repositorio --provider openai

# Usando DeepSeek
python analyze_repo.py https://github.com/usuario/repositorio --provider deepseek

# Usando Ollama local
python analyze_repo.py https://github.com/usuario/repositorio --provider ollama
```

### Opções Adicionais

```bash
# Salvar relatório em arquivo específico
python analyze_repo.py https://github.com/usuario/repositorio -o relatorio.json

# Usar arquivo de configuração personalizado
python analyze_repo.py https://github.com/usuario/repositorio -c config.json

# Análise com múltiplos provedores
python analyze_repo.py https://github.com/usuario/repositorio --providers gemini,openai,deepseek

# Análise focada em diretórios específicos
python analyze_repo.py https://github.com/usuario/repositorio --dirs src/,tests/
```

### Configuração Personalizada

Você pode criar um arquivo `config.json` para personalizar a análise:

```json
{
    "providers": {
        "gemini": {
            "enabled": true,
            "model": "gemini-2.0-flash",
            "temperature": 0.7
        },
        "openai": {
            "enabled": true,
            "model": "gpt-4",
            "temperature": 0.5
        },
        "deepseek": {
            "enabled": true,
            "model": "deepseek-coder-33b-instruct"
        },
        "ollama": {
            "enabled": true,
            "model": "llama2:13b",
            "url": "http://localhost:11434/api/generate"
        }
    },
    "analysis": {
        "max_method_lines": 30,
        "max_complexity": 10,
        "ignore_patterns": ["*.min.js", "vendor/*"]
    }
}
```

## Estrutura do Projeto

```
/
├── microservices/
│   └── source-provider/
│       └── src/
│           ├── analyzers/         # Módulos de análise
│           │   ├── ai_providers.py  # Provedores de IA
│           │   └── ...
│           ├── analyze_repo.py    # Script principal
│           └── test_gemini.py     # Testes do Gemini
├── requirements.txt   # Dependências
└── README.md         # Este arquivo
```

## Publicação

Este pacote está disponível no PyPI e pode ser instalado via pip:

```bash
pip install refactool
```

Novas versões são publicadas automaticamente através do pipeline de CI/CD quando uma nova tag é criada no repositório.

> **Nota para desenvolvedores internos**: Instruções detalhadas sobre o processo de publicação estão disponíveis na documentação interna do projeto.

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a GNU Lesser General Public License v3.0 (LGPL-3.0).

Para mais detalhes, consulte o arquivo [LICENSE](LICENSE) ou visite [GNU Lesser General Public License v3.0](https://www.gnu.org/licenses/lgpl-3.0.html).
