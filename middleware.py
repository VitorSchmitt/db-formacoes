from fastapi import Request
from fastapi.responses import JSONResponse

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

    # 🔐 AGORA É SESSÃO (não token)
    user = request.session.get("user")

    if not user:
        return JSONResponse(status_code=401, content={"erro": "Não autenticado"})

    request.state.user = user

    perfil = user.get("perfil")

    # 🔒 permissões continuam funcionando
    if not tem_permissao(perfil, path):
        return JSONResponse(status_code=403, content={"erro": "Sem permissão"})

    return await call_next(request)
