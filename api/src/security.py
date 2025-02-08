from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # type: ignore

def validate_token(token: str = Depends(oauth2_scheme)):
    if token != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden: token inválido")
    return token 