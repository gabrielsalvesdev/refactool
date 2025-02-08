# microservices/ai-module/src/ai_model.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/suggest")
async def generate_suggestions(request: dict):
    return {"suggestions": ["Refatorar módulo X usando padrão Y"]}
