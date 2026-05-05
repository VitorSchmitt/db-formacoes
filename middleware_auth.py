from fastapi import Request
from fastapi.responses import JSONResponse

# ===============================
# ROTAS POR PERFIL
# ===============================
PERMISSOES = {
    "admin": ["*"],

    "operador": [
        "/api/servidor",
        "/api/servidores",
        "/api/formacao",
        "/api/formacoes",
        "/api/participacao",
        "/api/participacoes"
    ],

    "custom": [
        "/api/servidores",
        "/api/formacoes"
    ]
}


# ===============================
# FUNÇÃO DE VALIDAÇÃO
# ===============================
def tem_permissao(perfil: str, path: str) -> bool:

    if not perfil:
        return False

    regras = PERMISSOES.get(perfil, [])

    # admin → tudo liberado
    if "*" in regras:
        return True

    # verifica se a rota começa com alguma permitida
    return any(path.startswith(p) for p in regras)


# ===============================
# MIDDLEWARE
# ===============================
async def auth_middleware(request: Request, call_next):

    # libera rotas públicas
    if request.url.path in ["/login", "/", "/docs", "/openapi.json"]:
        return await call_next(request)

    perfil = request.headers.get("perfil")

    # 🔴 sem perfil → bloqueia
    if not perfil:
        return JSONResponse(
            status_code=401,
            content={"erro": "Não autenticado"}
        )

    # 🔴 sem permissão
    if not tem_permissao(perfil, request.url.path):
        return JSONResponse(
            status_code=403,
            content={"erro": "Sem permissão"}
        )

    return await call_next(request)
