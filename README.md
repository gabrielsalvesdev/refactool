# Refactool

![Refactool](https://img.shields.io/badge/Refactool-API-green)

## 📋 Visão Geral do Projeto

O Refactool é uma ferramenta para análise e refatoração de código. Ele é composto por tais módulos principais:

- **API RESTful (porta 8000)**: Orquestra as chamadas aos microserviços.
- **Microserviço Code-analyzer (porta 5000)**: Realiza análise detalhada do código.
- **Microserviço AI-module (porta 6000)**: Sugere refatorações com base em padrões de código.
- **CLI**: Ferramenta de linha de comando que facilita a análise e consulta de status.


----



## 🚀 Começando

### Pré-requisitos

Certifique-se de ter o Docker e Docker Compose instalados em sua máquina:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Instalação

Clone o repositório e inicie os containers:

```sh
git clone https://github.com/gabrielsalvesdev/refactool
cd refactool
docker compose up -d

```

----------


## 🛠️ Uso Básico via CLI

#### Iniciar uma Análise

Para iniciar uma análise, com os containers ativos, execute:

```
refactool analyze --path "/caminho/do/projeto"
```

Isso enviará uma requisição para a API, que encaminha a análise para o microserviço de análise de código.

### Consultar o Status de uma Tarefa

Para consultar o status de uma análise em andamento:


```
refactool status --task_id <ID_DA_TAREFA>
```

Este comando retorna o status atual da tarefa, permitindo que você acompanhe o progresso da análise.

----------



# 📦 Arquitetura do Projeto


```
|-- api
|   |-- main.py
|   |-- ...
|
|-- microservices
|   |-- code-analyzer
|   |   |-- app.py
|   |   |-- ...
|   |
|   |-- ai-module
|       |-- app.py
|       |-- ...
|
|-- cli
|   |-- refactool.py
|   |-- ...
|
|-- docker-compose.yml
|-- README.md

```

----------

## 🌟 Funcionalidades Principais

-   **Análise de Código**: Identifique problemas no seu código e receba sugestões de melhoria.
-   **Refatoração Inteligente**: Aproveite a IA para sugestões automáticas de refatoração.
-   **CLI Amigável**: Execute análises e consulte status diretamente do terminal.

----------

## 🔍 Referência de API

### Analisar Código

**Endpoint:**  `POST /analyze`

**Exemplo de Requisição:**

```
{
  "path": "/caminho/do/projeto"
}
```

**Exemplo de Resposta:**

```
{
  "task_id": "12345"
}
```

#### Chamada via cURL

Você pode chamar a API utilizando o seguinte comando via cURL:

```sh
curl -v -H 'Authorization: dummy' -d '{"path":"/caminhodoprojeto"}' -H 'Content-Type: application/json' http://localhost:8000/analyze | cat
```

Explicação:
- O parâmetro `-v` ativa o modo verbose, exibindo detalhes da requisição e da resposta.
- A opção `-H 'Authorization: dummy'` define o header de autorização (necessário para o endpoint, conforme implementado na API).
- A opção `-d '{"path":"/caminhodoprojeto"}'` envia o corpo da requisição em formato JSON com a chave "path", onde você deve substituir "/caminhodoprojeto" pelo caminho do projeto real.
- A opção `-H 'Content-Type: application/json'` garante que o servidor saiba que o payload está em JSON.
- O comando `| cat` é usado para garantir que toda a saída seja enviada para o terminal.

### Consultar Status

**Endpoint:**  `GET /status/{task_id}`

**Exemplo de Resposta:**

```
{
  "task_id": "12345",
  "status": "completed",
  "details": {
    "files_analyzed": 25,
    "issues_found": 5
  }
}
```

----------

## 🌐 Contribuindo

Contribuições são bem-vindas! Siga os passos abaixo para contribuir com o projeto:

1.  Fork o repositório
2.  Crie uma branch (`git checkout -b feature/sua-feature`)
3.  Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4.  Push para a branch (`git push origin feature/sua-feature`)
5.  Abra um Pull Request

----------

## 📄 Licença

Este projeto é licenciado sob a GNU Lesser General Public License v3.0.  [LICENSE]([https://github.com/gabrielsalvesdev/refactool/blob/main/LICENCE)  para mais detalhes.

----------

## 💬 Contato

Para dúvidas ou sugestões, entre em contato:

-   **Email:**  [[contato@gabrielsousa.dev](mailto:contato@gabrielsousa.dev)]
