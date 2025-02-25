from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Header
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # type: ignore

def validate_token(authorization: str = Header(None, alias='Authorization')):
    # Aceita qualquer token; se nenhum for fornecido, retorna 'dummy'
    return authorization or 'dummy'

if __name__ == '__main__':
    # Teste simples
    print(validate_token()) 