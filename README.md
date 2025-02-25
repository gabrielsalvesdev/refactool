# Analisador de Repositórios

Este é um analisador de código que pode analisar qualquer repositório GitHub, fornecendo métricas e sugestões de melhorias.

## Funcionalidades

- Análise estática de código
- Detecção de problemas comuns (code smells)
- Sugestões de melhorias usando IA
- Suporte a múltiplas linguagens
- Relatórios detalhados

## Requisitos

- Python 3.8+
- Git instalado
- Ollama (opcional, para análise com IA local)
- Chave API OpenAI ou DeepSeek (opcional, para análise com IA em nuvem)

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

3. Configure as variáveis de ambiente (opcional):
```bash
# Para usar OpenAI
export OPENAI_API_KEY=sua-chave-api

# Para usar DeepSeek
export DEEPSEEK_API_KEY=sua-chave-api

# Para usar Git em Windows
export GIT_PYTHON_GIT_EXECUTABLE="C:\Program Files\Git\bin\git.exe"
```

## Uso

### Análise Básica

Para analisar um repositório:

```bash
python analyze_repo.py https://github.com/usuario/repositorio
```

### Opções Adicionais

- Salvar relatório em arquivo:
```bash
python analyze_repo.py https://github.com/usuario/repositorio -o relatorio.txt
```

- Usar arquivo de configuração personalizado:
```bash
python analyze_repo.py https://github.com/usuario/repositorio -c config.json
```

### Configuração Personalizada

Você pode criar um arquivo de configuração JSON com suas preferências:

```json
{
    "timeout": 300,
    "ollama_model": "llama2:13b",
    "max_method_lines": 30,
    "max_complexity": 10
}
```

## Provedores de IA Suportados

1. OpenAI (requer chave API)
   - Modelos mais precisos
   - Análise em nuvem
   - Custo por uso

2. DeepSeek (requer chave API)
   - Especializado em código
   - Análise em nuvem
   - Custo por uso

3. Ollama (local)
   - Gratuito
   - Execução local
   - Requer mais recursos do computador

O analisador tentará usar os provedores na seguinte ordem:
1. OpenAI (se OPENAI_API_KEY estiver configurada)
2. DeepSeek (se DEEPSEEK_API_KEY estiver configurada)
3. Ollama (fallback local)

## Exemplos de Uso

1. Análise rápida:
```bash
python analyze_repo.py https://github.com/usuario/repositorio
```

2. Análise completa com relatório:
```bash
python analyze_repo.py https://github.com/usuario/repositorio -o relatorio.txt -c config.json
```

3. Análise com configuração específica:
```bash
python analyze_repo.py https://github.com/usuario/repositorio -c custom_config.json
```

## Guia Detalhado de Personalização

### 1. Arquivo de Configuração

Você pode criar um arquivo `config.json` com as seguintes configurações:

```json
{
    "timeout": 300,
    
    // Configurações de IA
    "ollama_model": "llama2:13b",
    "ollama_timeout": 60,
    "ollama_url": "http://localhost:11434/api/generate",
    
    "openai_model": "gpt-3.5-turbo-instruct",
    "openai_timeout": 30,
    
    "deepseek_model": "deepseek-coder-33b-instruct",
    "deepseek_timeout": 30,
    
    // Limites de Análise
    "max_method_lines": 30,        // Máximo de linhas por método
    "max_complexity": 10,          // Complexidade ciclomática máxima
    "max_class_lines": 300,        // Máximo de linhas por classe
    "max_parameters": 5,           // Máximo de parâmetros por função
    "min_duplicate_lines": 6,      // Mínimo de linhas para detectar duplicação
    "min_similarity": 0.8          // Similaridade mínima para código duplicado
}
```

### 2. Arquivos Importantes

O analisador presta atenção especial aos seguintes tipos de arquivos:

```json
{
    "important_files": {
        "build": [
            "setup.py", "requirements.txt", "package.json",
            "Cargo.toml", "build.gradle", "pom.xml"
        ],
        "config": [
            ".env", "config.yaml", "config.json",
            "docker-compose.yml", "Dockerfile"
        ],
        "docs": [
            "README.md", "CONTRIBUTING.md", "API.md",
            "CHANGELOG.md", "docs/"
        ],
        "tests": [
            "test/", "tests/", "spec/", "__tests__/"
        ],
        "ci": [
            ".github/workflows/", ".gitlab-ci.yml", "Jenkinsfile"
        ]
    }
}
```

### 3. Linguagens Suportadas

O analisador suporta as seguintes extensões de arquivo:

- `.py`: Python
- `.js`: JavaScript
- `.ts`: TypeScript
- `.java`: Java
- `.go`: Go
- `.rs`: Rust
- `.cpp`: C++
- `.cs`: C#
- `.rb`: Ruby
- `.php`: PHP
- E mais...

### 4. Dicas de Personalização

#### Para Projetos Grandes
- Aumente o `timeout` para permitir análise completa
- Reduza `min_duplicate_lines` para encontrar mais duplicações
- Ajuste `max_class_lines` e `max_method_lines` conforme necessário

#### Para Análise Rigorosa
- Reduza `max_method_lines` (ex: 20 linhas)
- Diminua `max_complexity` (ex: 5-7)
- Reduza `max_parameters` (ex: 3-4)
- Aumente `min_similarity` para duplicações (ex: 0.9)

#### Para Análise Rápida
- Use Ollama local em vez de OpenAI/DeepSeek
- Aumente `min_duplicate_lines`
- Reduza o escopo de arquivos importantes

#### Para Análise Precisa
- Use OpenAI com GPT-4 (requer chave API)
- Aumente timeouts para permitir análise profunda
- Ajuste `important_files` para seu tipo de projeto

### 5. Variáveis de Ambiente

Configure as seguintes variáveis conforme necessário:

```bash
# Para usar OpenAI
export OPENAI_API_KEY=sua-chave-api

# Para usar DeepSeek
export DEEPSEEK_API_KEY=sua-chave-api

# Para Git no Windows
export GIT_PYTHON_GIT_EXECUTABLE="C:\Program Files\Git\bin\git.exe"
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a GNU Lesser General Public License v3.0 (LGPL-3.0).

Para mais detalhes, consulte o arquivo [LICENSE](LICENSE) ou visite [GNU Lesser General Public License v3.0](https://www.gnu.org/licenses/lgpl-3.0.html).
