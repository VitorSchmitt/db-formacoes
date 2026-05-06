from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from middleware import auth_middleware

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

# middleware
app.add_middleware(AuthMiddleware)

# templates
templates = Jinja2Templates(directory="templates")

# routers
app.include_router(login_router)
app.include_router(usuario_router)
app.include_router(servidor_router)
app.include_router(formacao_router)
app.include_router(participacao_router)
app.include_router(dashboard_router)

# =====================
# WEB
# =====================

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/web/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": request.session.get("user")
    })
