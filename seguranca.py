from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt

import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256" # Algoritmo da assinatura/Token

pwd_hash = PasswordHash.recommended()
OAuth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def gerar_hash(senha: str) -> str:
    return pwd_hash.hash(senha)

def verificar_senha(senha, hash_senha) -> bool:
    return pwd_hash.verify(senha, hash_senha)

def criar_token(dados: dict) -> str:
    payload = dados.copy() # conteúdo do token
    exp = datetime.now(timezone.utc) + timedelta(minutes=30) # validade de 30 minutos
    payload.update({"exp": exp})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
