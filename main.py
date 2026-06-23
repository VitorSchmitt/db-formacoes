from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse

from database import SessionLocal
from models import Usuario

# imports dos seus arquivos atuais
from routes_login import router as login_router
from routes_usuario import router as usuario_router
from routes_servidor import router as servidor_router
from routes_formacao import router as formacao_router
from routes_participacao import router as participacao_router
from routes_dashboard import router as dashboard_router
from routes_lotacao import router as lotacao_router
from routes_certificados import router as certificado_router
from routes_plano_anual import router as plano_anual_router
from routes_cronograma import router as cronograma_router
from routes_relatorio_servidor import router as relatorio_router
from routes_facilitador import router as facilitador_router
from routes_relatorio_facilitador import router as relatorio_facilitador_router

# ==========================================
# NOVO IMPORT: Rota de Classificações de Estágio
# ==========================================
from estagiario.routes.classificacoes_estagio import router as classificacoes_estagio_router
from estagiario.routes.valor_bolsa_estagio import router as valor_bolsa_router
from middleware import AuthMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# middleware auth
app.add_middleware(AuthMiddleware)

# sessão
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key"
)

# templates
# Altere a inicialização dos templates para aceitar múltiplos diretórios
templates = Jinja2Templates(directory=["templates", "estagiario/templates"])

# routers atuais
app.include_router(login_router)
app.include_router(usuario_router)
app.include_router(servidor_router)
app.include_router(formacao_router)
app.include_router(participacao_router)
app.include_router(dashboard_router)
app.include_router(lotacao_router)
app.include_router(certificado_router)
app.include_router(plano_anual_router)
app.include_router(cronograma_router)
app.include_router(relatorio_router)
app.include_router(facilitador_router)
app.include_router(relatorio_facilitador_router)

# ==========================================
# INCLUSÃO DO NOVO ROUTER DE ESTÁGIOS
# ==========================================
app.include_router(classificacoes_estagio_router)
app.include_router(valor_bolsa_router)

# ===============================
# WEB
# ===============================

@app.get("/")
def home(request: Request):
    db = SessionLocal()
    try:
        tem_usuario = db.query(Usuario).first()
        if not tem_usuario:
            return templates.TemplateResponse(
                "usuarios.html",
                {"request": request}
            )
        return templates.TemplateResponse(
            "login.html",
            {"request": request}
        )
    finally:
        db.close()


@app.get("/web/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/web/servidores")
def tela_servidores(request: Request):
    return templates.TemplateResponse(
        "servidores.html",
        {"request": request}
    )


@app.get("/web/formacoes")
def tela_formacoes(request: Request):
    return templates.TemplateResponse(
        "formacoes.html",
        {"request": request}
    )


@app.get("/web/participacoes")
def tela_participacoes(request: Request):
    return templates.TemplateResponse(
        "participacoes.html",
        {"request": request}
    )


@app.get("/web/usuarios")
def tela_usuarios(request: Request):
    return templates.TemplateResponse(
        "usuarios.html",
        {"request": request}
    )

@app.get("/web/lotacoes")
def tela_lotacoes(request: Request):
    return templates.TemplateResponse(
        "lotacao.html",
        {"request": request}
    )
    
@app.get("/web/plano_anual")
def tela_plano(request: Request):
    return templates.TemplateResponse(
        "plano_anual.html",
        {"request": request}
    )

@app.get("/web/cronograma")
def tela_cronograma(request: Request):
    return templates.TemplateResponse(
        "cronograma.html",
        {"request": request}
    )

@app.get("/web/relatorio_servidor")
def tela_relatorio_servidor(request: Request):  # Corrigido nome duplicado da função
    return templates.TemplateResponse(
        "relatorio_servidor.html",
        {"request": request}
    )

@app.get("/web/facilitadores")
def tela_facilitadores(request: Request):
    return templates.TemplateResponse(
        "facilitadores.html",
        {"request": request}
    )

@app.get("/web/relatorio_facilitador")
def tela_relatorio_facilitador(request: Request):  # Corrigido nome duplicado da função
    return templates.TemplateResponse(
        "relatorio_facilitador.html",
        {"request": request}
    )

# ==========================================
# NOVA ROTA WEB: Renderiza o HTML da Classificação
# ==========================================
@app.get("/web/estagiario/classificacoes")
def tela_classificacoes_estagio(request: Request):
    return templates.TemplateResponse(
        "classificacoes.html",  # <-- Agora ele acha direto, sem precisar de "../"
        {"request": request}
    )

@app.get("/web/estagiario/valores_bolsa_estagio")
def tela_valores_bolsa_estagio(request: Request):
    return templates.TemplateResponse(
        "valores_bolsa_estagio.html",  
        {"request": request}
    )
    
    
