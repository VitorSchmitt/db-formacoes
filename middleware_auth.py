from fastapi import Request
from fastapi.responses import JSONResponse
from security import validar_token

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
        "/api/enums"
    ],

    "custom": [
        "/api/servidores",
        "/api/formacoes"
    ]
}

def tem_permissao(perfil, path):
    regras = PERMISSOES.get(perfil, [])

    if "*" in regras:
        return True

    return any(path.startswith(p) for p in regras)

async def auth_middleware(request: Request, call_next):

    path = request.url.path

    # 🔓 rotas públicas
    if path in ["/", "/login", "/docs", "/openapi.json"] or path.startswith("/web"):
        return await call_next(request)

    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"erro": "Não autenticado"})

    token = auth.split(" ")[1]
    payload = validar_token(token)

    if not payload:
        return JSONResponse(status_code=401, content={"erro": "Token inválido"})

    request.state.user = payload

    if not tem_permissao(payload["perfil"], path):
        return JSONResponse(status_code=403, content={"erro": "Sem permissão"})

    return await call_next(request)
