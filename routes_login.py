import logging
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Usuario
from security import verify_password, hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["auth"])

# ===============================
# LOGIN
# ===============================
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(..., description="Nome de usuário"),
    senha: str = Form(..., description="Senha do usuário"),
    db: Session = Depends(get_db)
):
    """
    Realiza o login do usuário
    
    - Valida credenciais
    - Cria sessão segura
    - Registra último login
    
    Args:
        request: Requisição FastAPI
        username: Nome de usuário
        senha: Senha em texto plano
        db: Sessão do banco de dados
    
    Returns:
        dict: Confirmação de sucesso e URL para redirecionamento
        JSONResponse com erro se falhar
    """
    try:
        # 🔍 Busca usuário no banco
        user = db.query(Usuario).filter(
            Usuario.username == username,
            Usuario.ativo == True
        ).first()

        # ❌ Usuário não encontrado ou inativo
        if not user:
            logger.warning(f"Tentativa de login: usuário '{username}' não encontrado")
            return JSONResponse(
                status_code=401,
                content={"erro": "Usuário ou senha inválidos"}
            )

        # 🔐 Verifica senha
        if not verify_password(senha, user.senha):
            logger.warning(f"Tentativa de login falha: senha incorreta para '{username}'")
            return JSONResponse(
                status_code=401,
                content={"erro": "Usuário ou senha inválidos"}
            )

        # ✅ Login bem-sucedido
        # Atualiza último login
        user.ultimo_login = datetime.utcnow()
        db.commit()

        # 🔐 Cria sessão segura
        request.session["user"] = {
            "id": user.id,
            "username": user.username,
            "perfil": user.perfil,
            "email": user.email
        }

        logger.info(f"✅ Login bem-sucedido: {username} ({user.perfil})")
        
        return {
            "ok": True,
            "redirect": "/web/dashboard",
            "message": f"Bem-vindo, {user.username}!"
        }

    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"erro": "Erro ao processar login"}
        )


# ===============================
# LOGOUT
# ===============================
@router.get("/logout")
async def logout(request: Request):
    """
    Realiza o logout do usuário
    
    - Limpa sessão
    - Redireciona para login
    
    Args:
        request: Requisição FastAPI
    
    Returns:
        dict: Confirmação de sucesso e URL para redirecionamento
    """
    try:
        username = request.session.get("user", {}).get("username", "desconhecido")
        request.session.clear()
        
        logger.info(f"✅ Logout: {username}")
        
        return {
            "ok": True,
            "redirect": "/login",
            "message": "Logout realizado com sucesso"
        }
    except Exception as e:
        logger.error(f"Erro no logout: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"erro": "Erro ao realizar logout"}
        )


# ===============================
# VERIFICAR AUTENTICAÇÃO
# ===============================
@router.get("/api/auth/check")
async def check_auth(request: Request):
    """
    Verifica se o usuário está autenticado
    
    Args:
        request: Requisição FastAPI
    
    Returns:
        dict: Status de autenticação e dados do usuário
    """
    user = request.session.get("user")
    
    if not user:
        return JSONResponse(
            status_code=401,
            content={"autenticado": False}
        )
    
    return {
        "autenticado": True,
        "usuario": user
    }
