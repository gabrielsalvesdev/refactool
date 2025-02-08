# microservices/code-analyzer/src/analyzer.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze")
async def analyze(request: dict):
    # Mock: Listar arquivos do projeto
    return {"project": request["path"], "files": ["src/main.py"], "issues": []}
