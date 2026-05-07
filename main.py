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
from middleware import AuthMiddleware


app = FastAPI()

# sessão
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key"
)

# middleware auth
app.middleware("http")(AuthMiddleware)

# templates
templates = Jinja2Templates(directory="templates")

# routers
app.include_router(login_router)
app.include_router(usuario_router)
app.include_router(servidor_router)
app.include_router(formacao_router)
app.include_router(participacao_router)
app.include_router(dashboard_router)

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
