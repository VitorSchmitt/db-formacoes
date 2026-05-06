"""Funções de segurança para autenticação e criptografia"""
import os
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict

# ===============================
# PASSWORD HASHING
# ===============================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


def hash_password(password: str) -> str:
    """
    Hash uma senha usando bcrypt
    
    Args:
        password: Senha em texto plano
    
    Returns:
        str: Senha criptografada
    
    Example:
        >>> hashed = hash_password("minha_senha")
        >>> verify_password("minha_senha", hashed)
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto plano corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Senha hash armazenada no banco
    
    Returns:
        bool: True se as senhas correspondem, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===============================
# JWT TOKEN MANAGEMENT
# ===============================
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
EXP_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", 60))


def criar_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um JWT token com os dados fornecidos
    
    Args:
        data: Dicionário com dados a serem incluídos no token
        expires_delta: Tempo de expiração customizado (padrão: EXP_MINUTES)
    
    Returns:
        str: JWT token codificado
    
    Example:
        >>> token = criar_token({"sub": "user123", "perfil": "admin"})
        >>> payload = validar_token(token)
        >>> print(payload["sub"])
        user123
    """
    payload = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=EXP_MINUTES)
    
    payload["exp"] = expire
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def validar_token(token: str) -> Optional[Dict]:
    """
    Valida e decodifica um JWT token
    
    Args:
        token: JWT token a validar
    
    Returns:
        dict: Payload do token se válido, None se inválido
    
    Example:
        >>> token = criar_token({"sub": "user123"})
        >>> payload = validar_token(token)
        >>> print(payload["sub"])
        user123
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Erro ao validar token: {str(e)}")
        return None


def is_token_expired(token: str) -> bool:
    """
    Verifica se um token está expirado
    
    Args:
        token: JWT token a verificar
    
    Returns:
        bool: True se expirado, False caso contrário
    """
    payload = validar_token(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if not exp:
        return True
    
    return datetime.utcfromtimestamp(exp) < datetime.utcnow()
