# api/src/main.py
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.src.security import validate_token
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import os
from pathlib import Path

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
# app.add_middleware(SlowAPIMiddleware)

class AnalyzeRequest(BaseModel):
    path: str

@app.post("/analyze")
# @limiter.limit("10/minute")
async def analyze_code(request: AnalyzeRequest, token: str = Depends(validate_token)):
    try:
        if not request.path:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Path é obrigatório", "status": "ERROR"}
            )
        
        # Verifica se o caminho existe
        path = Path(request.path)
        if not path.exists():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Caminho inválido ou não existe", "status": "ERROR"}
            )
            
        # Simulação de análise de código
        return {
            "status": "SUCCESS",
            "issues": []
        }
    except Exception as e:
        # Log da exceção pode ser adicionado aqui
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Erro interno ao processar a análise: {str(e)}", "status": "ERROR"}
        )

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    return {"task_id": task_id, "status": "completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
