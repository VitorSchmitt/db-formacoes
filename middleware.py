from fastapi import Request
from fastapi.responses import JSONResponse

# ======================
# CONFIG
# ======================

PERMISSOES = {
    "admin": ["*"],

    "operador": [
        "/api/dashboard",
        "/web/dashboard"
    ]
}

PUBLIC_PATHS = [
    "/",
    "/login",
    "/docs",
    "/openapi.json"
]

PUBLIC_PREFIX = [
    "/static",
    "/web"
]

# ======================
# HELPERS
# ======================

def is_public(path: str):

    return (
        path in PUBLIC_PATHS
        or any(path.startswith(p) for p in PUBLIC_PREFIX)
    )


def tem_permissao(perfil: str, path: str):

    regras = PERMISSOES.get(perfil, [])

    if "*" in regras:
        return True

    return any(path.startswith(p) for p in regras)

# ======================
# MIDDLEWARE
# ======================

async def auth_middleware(request: Request, call_next):

    path = request.url.path

    # libera públicas
    if is_public(path):
        return await call_next(request)

    # sessão protegida
    try:
        user = request.session.get("user")
    except Exception:
        user = None

    # não autenticado
    if not user:
        return JSONResponse(
            status_code=401,
            content={"erro": "Não autenticado"}
        )

    # perfil
    perfil = user.get("perfil")

    # sem permissão
    if not tem_permissao(perfil, path):
        return JSONResponse(
            status_code=403,
            content={"erro": "Sem permissão"}
        )

    return await call_next(request)
