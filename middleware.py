from fastapi import Request
from fastapi.responses import JSONResponse

PERMISSOES = {
    "admin": ["*"],
    "operador": [
        "/api/servidores",
        "/api/formacoes",
        "/api/dashboard"
    ]
}

PUBLIC_PATHS = [
    "/",
    "/login",
    "/docs",
    "/openapi.json"
]

PUBLIC_PREFIX = ["/static", "/web"]


def is_public(path: str):
    return path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIX)


def tem_permissao(perfil: str, path: str):
    regras = PERMISSOES.get(perfil, [])

    if "*" in regras:
        return True

    return any(path.startswith(p) for p in regras)


async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if is_public(path):
        return await call_next(request)

    user = request.session.get("user")

    if not user:
        return JSONResponse(status_code=401, content={"erro": "Não autenticado"})

    if not tem_permissao(user.get("perfil"), path):
        return JSONResponse(status_code=403, content={"erro": "Sem permissão"})

    request.state.user = user
    return await call_next(request)
