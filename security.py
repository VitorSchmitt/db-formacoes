from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
EXP_MINUTES = 60

def criar_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXP_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def validar_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
