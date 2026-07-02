from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import Request

# ======================
# CONFIG
# ======================

PUBLIC_PATHS = [
    "/",
    "/login",
    "/docs",
    "/openapi.json",
    "/web/dashboard",   
    "/web/servidores",
    "/web/formacoes",
    "/web/participacoes",
    "/web/usuarios",
    "/web/lotacoes",
    "/web/certificados",
    "/web/plano_anual",
    "/web/cronograma",
    "/web/relatorio_servidor",
    "/web/facilitadores",
    "/web/relatorio_facilitador"
    
]

PUBLIC_PREFIX = [
    "/static"
]

PERMISSOES = {
    "admin": ["*"],


    "operadorIII":[
        "/web/beneficios",        
        "/web/classificacoes",        
        "/web/contratos",
        "/web/valores_bolsa_auxilio",
        "/web/estagiarios",
        "/api/beneficio_estagiario",
        "/api/classificacoes_estagio",
        "/api/contrato_estagio",
        "/api/estagiarios",
        "/api/valores_bolsa_estagio",
        "/api/servidores",
        "/api/lotacoes"
    ],
    
    "operador": [ 
        "/web/dashboard",        
        "/web/participacoes",        
        "/web/certificados",
        "/web/relatorio_servidor",
        "/api/dashboard",       
        "/api/participacoes",        
        "/api/certificados",
        "/api/relatorio_servidor",
        "/api/formacoes",
        "/api/servidores",
        "/api/lotacoes"
    ],
    
    "operadorII": [ 
        "/web/dashboard",
        "/web/servidores",
        "/web/formacoes",       
        "/web/lotacoes",        
        "/api/dashboard",
        "/web/facilitadores",
        "/web/relatorio_facilitador",
        "/api/servidores",
        "/api/formacoes",        
        "/api/lotacoes",       
        "/api/planos_anual",
        "/api/enums",
        "/api/facilitador",
        "/api/relatorios/facilitadores"
        
    ],
    "custom": [ 
        "/web/dashboard",
        "/web/plano_anual",
        "/web/cronograma",        
        "/api/dashboard",
        "/api/plano_anual",
        "/api/cronograma"
    ]
    
}

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
# MIDDLEWARE PROFISSIONAL
# ======================


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        path = request.url.path

        # 1. rotas públicas
        if is_public(path):
            return await call_next(request)

        # 2. sessão segura
        session = getattr(request, "session", None)
        user = session.get("user") if session else None

        # 3. não autenticado
        if not user:

            if path.startswith("/web"):
                return RedirectResponse(url="/")

            return JSONResponse(
                status_code=401,
                content={"erro": "Não autenticado"}
            )

        perfil = user.get("perfil")

        # 4. sem permissão
        if not tem_permissao(perfil, path):

            if path.startswith("/web"):
                return RedirectResponse(url="/")

            return JSONResponse(
                status_code=403,
                content={"erro": "Sem permissão"}
            )

        # 5. continua request
        return await call_next(request)
