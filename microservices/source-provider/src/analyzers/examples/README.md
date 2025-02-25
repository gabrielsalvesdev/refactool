# Exemplo de Uso do RefactoolAnalyzer

Este diretório contém exemplos práticos de como utilizar o RefactoolAnalyzer para analisar projetos.

## Pré-requisitos

1. Python 3.8 ou superior
2. Dependências instaladas (veja `requirements.txt` na raiz do projeto)
3. Arquivo `.env` configurado com as chaves necessárias

## Configuração

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp ../.env.example .env
   ```

2. Configure suas chaves de API no arquivo `.env`:
   ```env
   DEEPSEEK_API_KEY=sua-chave-api-aqui
   OLLAMA_API_URL=http://localhost:11434/api/generate
   ```

## Uso

O script `analyze_project.py` é um exemplo completo de como usar o RefactoolAnalyzer. Para executá-lo:

```bash
python analyze_project.py /caminho/do/seu/projeto
```

### Exemplo de Saída

O script irá:
1. Analisar todo o projeto especificado
2. Gerar um relatório detalhado em `reports/refactool_analysis.txt`
3. Mostrar um resumo no console com:
   - Total de arquivos analisados
   - Linguagens encontradas
   - Localização do relatório completo

### Logs

O script usa logging estruturado com `structlog` e mostrará:
- Progresso da análise
- Avisos sobre configurações faltantes
- Erros encontrados durante a análise

## Estrutura do Relatório

O relatório gerado inclui:

1. **Visão Geral do Projeto**
   - Total de arquivos
   - Estrutura do projeto

2. **Linguagens Utilizadas**
   - Lista de linguagens
   - Quantidade de arquivos por linguagem

3. **Dependências**
   - Dependências por linguagem
   - Versões utilizadas

4. **Arquivos Importantes**
   - Arquivos de configuração
   - Arquivos de build
   - Documentação

5. **Problemas e Sugestões**
   - Code smells encontrados
   - Sugestões de melhoria
   - Recomendações da IA

## Exemplos de Uso Avançado

### Análise de Subdiretório

```bash
python analyze_project.py /seu/projeto/src
```

### Análise com Ollama Local

1. Inicie o Ollama localmente:
   ```bash
   ollama run codellama
   ```

2. Configure o `.env`:
   ```env
   OLLAMA_API_URL=http://localhost:11434/api/generate
   OLLAMA_MODEL=codellama
   ```

3. Execute a análise:
   ```bash
   python analyze_project.py /seu/projeto
   ```

## Dicas

1. Para projetos grandes, a análise pode levar alguns minutos
2. O relatório é salvo em texto plano para fácil integração com outras ferramentas
3. Os logs estruturados facilitam o monitoramento do processo
4. A análise continuará mesmo se alguns arquivos falharem 