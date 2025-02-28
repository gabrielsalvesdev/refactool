from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import os

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def validate_token(api_key: str = Security(api_key_header)) -> str:
    """
    Valida o token de API fornecido no header Authorization
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Token is missing"
        )
    
    # Remove o prefixo "Bearer " se presente
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]
    
    expected_api_key = os.getenv("API_KEY", "test_key")
        
    if api_key != expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid token"
        )
    
    return api_key

if __name__ == '__main__':
    # Teste simples
    print(validate_token()) 