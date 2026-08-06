# Refactool – Analisador de Código com IA

Refactool é uma ferramenta de análise de código que utiliza múltiplos provedores de IA
para sugerir melhorias em projetos reais, com foco em relatórios claros em português
do Brasil.

## Funcionalidades

- Análise estática de repositórios Git.
- Sugestões de melhoria em português (Brasil).
- Suporte a múltiplos provedores de IA:
  - Google Gemini (padrão)
  - OpenAI GPT
  - DeepSeek
  - Ollama (execução local)
- Geração de relatórios em formato JSON.
- Configuração flexível de provedores e parâmetros de análise.

## Requisitos

- Python 3.8+
- Git instalado
- Pelo menos uma das seguintes chaves de API:
  - Google Gemini
  - OpenAI
  - DeepSeek
- Ollama instalado localmente (opcional, para execução local).

## Instalação

Via PyPI:

```bash
pip install refactool
```

Ou via repositório:

```bash
git clone https://github.com/gabrielsalvesdev/refactool
cd refactool
pip install -r requirements.txt
```

Configure o arquivo `.env` com suas credenciais:

```env
# Provedor padrão (Gemini)
GEMINI_API_KEY=sua-chave-api-aqui

# Git (Windows)
GIT_PYTHON_GIT_EXECUTABLE=C:\Program Files\Git\bin\git.exe

# Provedores opcionais
OPENAI_API_KEY=sua-chave-openai-aqui
DEEPSEEK_API_KEY=sua-chave-deepseek-aqui
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama2:13b
```

## Uso básico

Analisar um repositório com o provedor padrão (Gemini):

```bash
python analyze_repo.py https://github.com/usuario/repositorio
```

Escolher um provedor específico:

```bash
# OpenAI
python analyze_repo.py https://github.com/usuario/repositorio --provider openai

# DeepSeek
python analyze_repo.py https://github.com/usuario/repositorio --provider deepseek

# Ollama (local)
python analyze_repo.py https://github.com/usuario/repositorio --provider ollama
```

Salvar relatório em arquivo:

```bash
python analyze_repo.py https://github.com/usuario/repositorio -o relatorio.json
```

## Configuração avançada

Para cenários mais avançados (múltiplos provedores, ajustes finos de análise),
você pode usar um arquivo `config.json` e apontar para ele com:

```bash
python analyze_repo.py https://github.com/usuario/repositorio -c config.json
```

Exemplos de configuração e detalhes adicionais estão disponíveis na documentação
do projeto e nos arquivos de exemplo deste repositório.

## Contribuindo

1. Faça um fork do projeto.
2. Crie uma branch para sua feature:

   ```bash
   git checkout -b feature/nova-feature
   ```

3. Commit suas mudanças:

   ```bash
   git commit -am "Adiciona nova feature"
   ```

4. Envie para seu fork:

   ```bash
   git push origin feature/nova-feature
   ```

5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a GNU Lesser General Public License v3.0 (LGPL-3.0).  
Consulte o arquivo `LICENSE` ou visite a [página oficial da licença](https://www.gnu.org/licenses/lgpl-3.0.html).
