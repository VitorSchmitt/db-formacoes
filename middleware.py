"""Middleware de autenticação e autorização"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable

# ===============================
# LOGGER
# ===============================
logger = logging.getLogger(__name__)

# ===============================
# PERMISSÕES POR PERFIL
# ===============================
PERMISSOES = {
    "admin": ["*"],

    "operador": [
        "/api/servidor",
        "/api/servidores",
        "/api/formacao",
        "/api/formacoes",
        "/api/participacao",
        "/api/participacoes",
        "/api/cargos",
        "/api/lotacoes",
        "/api/dashboard",
        "/api/enums"
    ],

    "consultor": [
        "/api/servidores",
        "/api/formacoes",
        "/api/dashboard"
    ]
}

# ===============================
# ROTAS PÚBLICAS
# ===============================
PUBLIC_PATHS = [
    "/",
    "/login",
    "/logout",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json"
]

PUBLIC_PATH_PREFIXES = [
    "/static/",
    "/web/"
]


def is_public_route(path: str) -> bool:
    """
    Verifica se a rota é pública
    
    Args:
        path: Caminho da requisição
    
    Returns:
        bool: True se é pública, False caso contrário
    """
    if path in PUBLIC_PATHS:
        return True
    
    return any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES)


def tem_permissao(perfil: str, path: str) -> bool:
    """
    Verifica se um perfil tem permissão para acessar uma rota
    
    Args:
        perfil: Perfil do usuário (admin, operador, consultor)
        path: Caminho da requisição
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    regras = PERMISSOES.get(perfil, [])

    # Admin tem acesso total
    if "*" in regras:
        return True

    # Verifica se o caminho começa com alguma rota permitida
    return any(path.startswith(p) for p in regras)


def is_admin(request: Request) -> bool:
    """Verifica se o usuário é admin"""
    user = getattr(request.state, "user", None)
    return user and user.get("perfil") == "admin"


def is_operador(request: Request) -> bool:
    """Verifica se o usuário é operador"""
    user = getattr(request.state, "user", None)
    return user and user.get("perfil") == "operador"


def is_consultor(request: Request) -> bool:
    """Verifica se o usuário é consultor"""
    user = getattr(request.state, "user", None)
    return user and user.get("perfil") == "consultor"


# ===============================
# MIDDLEWARE DE AUTENTICAÇÃO
# ===============================
async def auth_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[JSONResponse]]
) -> JSONResponse:
    """
    Middleware de autenticação e autorização
    
    - Libera rotas públicas
    - Verifica autenticação do usuário
    - Valida permissões por perfil
    
    Args:
        request: Requisição FastAPI
        call_next: Função para chamar o próximo middleware
    
    Returns:
        JSONResponse: Resposta da requisição ou erro de autenticação/autorização
    """
    path = request.url.path
    method = request.method

    # 🔓 Libera rotas públicas
    if is_public_route(path):
        return await call_next(request)

    # 🔐 Obtém usuário da sessão
    try:
        session = getattr(request, "session", {})
        user = session.get("user")
    except Exception as e:
        logger.error(f"Erro ao obter sessão: {str(e)}")
        user = None

    # ❌ Usuário não autenticado
    if not user:
        logger.warning(f"Requisição não autenticada para {method} {path}")
        return JSONResponse(
            status_code=401,
            content={
                "erro": "Não autenticado",
                "message": "Realize o login para continuar"
            }
        )

    # ✅ Armazena usuário no estado da requisição
    request.state.user = user

    # 🔐 Verifica permissões
    perfil = user.get("perfil", "")
    if not tem_permissao(perfil, path):
        logger.warning(
            f"Acesso negado: usuário {user.get('username')} ({perfil}) "
            f"tentou acessar {method} {path}"
        )
        return JSONResponse(
            status_code=403,
            content={
                "erro": "Sem permissão",
                "message": f"Seu perfil ({perfil}) não tem acesso a este recurso"
            }
        )

    # ✅ Prossegue com a requisição
    logger.info(f"Acesso autorizado: {user.get('username')} - {method} {path}")
    return await call_next(request)
