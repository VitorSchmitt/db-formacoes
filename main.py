from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from database import SessionLocal
from models import Usuario
from typing import Optional
from fastapi import Query

from routes_formacao import router as formacao_router
from routes_servidor import router as servidor_router
from routes_login import router as login_router
from routes_participacao import router as participacao_router
from routes_usuario import router as usuario_router

# ===============================
# APP
# ===============================
app = FastAPI()

# 🔐 SESSION MIDDLEWARE (OBRIGATÓRIO)
app.add_middleware(
    SessionMiddleware,
    secret_key="minha_chave_fixa_super_segura_147"
)
# =========================
# "BANCO" FAKE
# =========================
USUARIOS = {
    "admin": {"senha": "147", "perfil": "admin"},
    "user": {"senha": "147", "perfil": "operador"}
}

# =========================
# PERMISSÕES
# =========================
PERMISSOES = {
    "admin": ["*"],
    "operador": ["/api/dados"]
}
# ===============================
# TEMPLATES
# ===============================
templates = Jinja2Templates(directory="templates")

# ===============================
# ROTAS PÚBLICAS
# ===============================
PUBLIC_PATHS = [
    "/",
    "/login",
    "/static",
    "/docs",
    "/openapi.json"
]

# ===============================
# AUTH MIDDLEWARE (SEGURO)
# ===============================
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if is_public_route(path):
        return await call_next(request)

    user = request.session.get("user")

    if not user:
        return JSONResponse(status_code=401, content={"erro": "Não autenticado"})

    perfil = user.get("perfil")

    if not tem_permissao(perfil, path):
        return JSONResponse(status_code=403, content={"erro": "Sem permissão"})

    return await call_next(request)
    

# ===============================
# ROUTERS
# ===============================
app.include_router(formacao_router)
app.include_router(servidor_router)
app.include_router(participacao_router)
app.include_router(usuario_router)
app.include_router(login_router)

# ===============================
# DB DEPENDENCY (PADRÃO CORRETO)
# ===============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================
# WEB PAGES
# ===============================
@app.get("/")
def home(request: Request):
    db = SessionLocal()
    try:
        tem_usuario = db.query(Usuario).first()

        if not tem_usuario:
            return templates.TemplateResponse("usuarios.html", {"request": request})

        return templates.TemplateResponse("login.html", {"request": request})
    finally:
        db.close()


@app.get("/web/dashboard")
def dashboard(request: Request):

    user = request.session.get("user")

    if not user:
        return JSONResponse(status_code=401, content={"erro": "Não autenticado"})

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user}
    )


@app.get("/web/servidores")
def tela_servidores(request: Request):
    return templates.TemplateResponse("servidores.html", {"request": request})


@app.get("/web/formacoes")
def tela_formacoes(request: Request):
    return templates.TemplateResponse("formacoes.html", {"request": request})


@app.get("/web/participacoes")
def tela_participacoes(request: Request):
    return templates.TemplateResponse("participacoes.html", {"request": request})


@app.get("/web/usuarios")
def tela_usuarios(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})

# ===============================
# API
# ===============================
@app.get("/api/lotacoes")
def listar_lotacoes():
    db = SessionLocal()
    try:
        dados = db.query(Lotacao).order_by(Lotacao.descricao).all()
        return [{"id": l.id, "descricao": l.descricao} for l in dados]
    finally:
        db.close()


@app.get("/api/dashboard")
def api_dashboard(
    mes_inicio: Optional[str] = Query(default=None),
    mes_fim: Optional[str] = Query(default=None),
    lotacao: Optional[str] = Query(default=None),
    curso: Optional[str] = Query(default=None),
):
    db: Session = SessionLocal()

    try:
        query = db.query(Participacao).join(Formacao).join(Lotacao)

        if mes_inicio:
            query = query.filter(
                func.to_char(Formacao.data_termino, "YYYY-MM") >= mes_inicio
            )

        if mes_fim:
            query = query.filter(
                func.to_char(Formacao.data_termino, "YYYY-MM") <= mes_fim
            )

        if lotacao:
            query = query.filter(Lotacao.tipo == lotacao)

        if curso:
            query = query.filter(Formacao.descricao == curso)

        total = query.count()

        lotacao_data = (
            query.with_entities(func.trim(Lotacao.tipo), func.count())
            .group_by(Lotacao.tipo)
            .all()
        )

        curso_data = (
            query.with_entities(func.trim(Formacao.descricao), func.count())
            .group_by(Formacao.descricao)
            .all()
        )

        periodo_data = (
            query.with_entities(
                func.to_char(Formacao.data_termino, "YYYY-MM"),
                func.count()
            )
            .group_by(func.to_char(Formacao.data_termino, "YYYY-MM"))
            .order_by(func.to_char(Formacao.data_termino, "YYYY-MM"))
            .all()
        )

        return {
            "total": total,
            "lotacao": [{"lotacao": l[0], "qtd": l[1]} for l in lotacao_data],
            "curso": [{"formacao": c[0], "qtd": c[1]} for c in curso_data],
            "periodo": [{"mes": p[0], "qtd": p[1]} for p in periodo_data],
        }

    except Exception as e:
        return {"erro": str(e)}

    finally:
        db.close()
