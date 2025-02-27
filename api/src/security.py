from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import os

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def validate_token(api_key: str = Security(api_key_header)) -> str:
    """
    Valida o token de API fornecido no header X-API-Key
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is missing"
        )
    
    expected_api_key = os.getenv("API_KEY")
    if not expected_api_key:
        # Em desenvolvimento, aceita qualquer chave
        return api_key
        
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return api_key

if __name__ == '__main__':
    # Teste simples
    print(validate_token()) 