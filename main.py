from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Participacao, Formacao, Lotacao
from routes_formacao import router as formacao_router
from routes_servidor import router as servidor_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.include_router(formacao_router)
app.include_router(servidor_router)


# ===============================
# WEB
# ===============================
@app.get("/")
def home():
    return {"ok": True}



@app.get("/web/servidores")
def tela_servidores(request: Request):
    return templates.TemplateResponse("servidores.html", {"request": request})

@app.get("/web/formacoes")
def tela_formacoes(request: Request):
    return templates.TemplateResponse("formacoes.html", {"request": request})
    
@app.get("/web/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/web/participacoes")
def tela_participacoes(request: Request):
    return templates.TemplateResponse("participacoes.html", {"request": request})


# ===============================
# API
# ===============================
@app.get("/api/dashboard")
def api_dashboard(
    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
):
    db: Session = SessionLocal()

    try:
        query = db.query(Participacao).join(Formacao).join(Lotacao)

        # 🔎 FILTROS
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

        # 📊 POR LOTAÇÃO
        lotacao_data = (
            query.with_entities(
                func.trim(Lotacao.tipo),
                func.count()
            )
            .group_by(Lotacao.tipo)
            .all()
        )

        # 📊 POR CURSO
        curso_data = (
            query.with_entities(
                func.trim(Formacao.descricao),
                func.count()
            )
            .group_by(Formacao.descricao)
            .all()
        )

        # 📊 POR PERÍODO
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
