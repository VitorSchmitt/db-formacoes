from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import get_db
import os
import pandas as pd

print("DIR ATUAL:", os.getcwd())
print("ARQUIVOS:", os.listdir())
print("TEMPLATES EXISTE?", os.path.exists("templates"))

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# =========================
# ROTA INICIAL (NOVA)
# =========================
@app.get("/")
def home():
    return RedirectResponse(url="/web/dashboard")


# =========================
# PÁGINA DASHBOARD
# =========================
@app.get("/web/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# =========================
# NOVA PÁGINA (MENU)
# =========================
@app.get("/web/formacoes", response_class=HTMLResponse)
def formacoes(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# =========================
# API DADOS DASHBOARD (NÃO MUDOU)
# =========================
from fastapi import Query

@app.get("/api/dashboard")
def api_dashboard(
    db: Session = Depends(get_db),
    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None)
):

    dados = db.query(models.Participacao).all()

    lista = []
    for p in dados:
        lista.append({
            "formacao": p.formacao.descricao if p.formacao else "",
            "lotacao": p.lotacao.descricao if p.lotacao else "",
            "data": p.formacao.data_termino if p.formacao else None
        })

    df = pd.DataFrame(lista)

    if df.empty:
        return {"lotacao": [], "curso": [], "periodo": [], "total": 0}

    # 🔹 tratar data
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    # 🔹 criar ANO-MÊS (padrão BI)
    df["mes"] = df["data"].dt.strftime("%Y-%m")

    # 🔹 FILTROS POR MÊS
    if mes_inicio:
        df = df[df["mes"] >= mes_inicio]

    if mes_fim:
        df = df[df["mes"] <= mes_fim]

    if lotacao:
        df = df[df["lotacao"] == lotacao]

    if curso:
        df = df[df["formacao"] == curso]

    return {
        "lotacao": df.groupby("lotacao")["lotacao"].count().reset_index(name="qtd").to_dict(orient="records"),
        "curso": df.groupby("formacao")["formacao"].count().reset_index(name="qtd").to_dict(orient="records"),
        "periodo": df.groupby("mes")["mes"].count().reset_index(name="qtd").to_dict(orient="records"),
        "total": int(len(df)),
        "lista_lotacao": sorted(df["lotacao"].unique().tolist()),
        "lista_curso": sorted(df["formacao"].unique().tolist()),
        "lista_meses": sorted(df["mes"].unique().tolist())
    }
