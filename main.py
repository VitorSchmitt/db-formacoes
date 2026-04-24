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
@app.get("/api/dashboard")
def api_dashboard(db: Session = Depends(get_db)):

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
    
    # garantir tipos simples
    df["formacao"] = df["formacao"].astype(str)
    df["lotacao"] = df["lotacao"].astype(str)
    
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["mes"] = df["data"].dt.strftime("%Y-%m")
    
    # remover linhas inválidas
    df = df.dropna(subset=["mes"])
    
    return {
        "lotacao": df.groupby("lotacao")["lotacao"].count().reset_index(name="qtd").to_dict(orient="records"),
        "curso": df.groupby("formacao")["formacao"].count().reset_index(name="qtd").to_dict(orient="records"),
        "periodo": df.groupby("mes")["mes"].count().reset_index(name="qtd").to_dict(orient="records"),
        "total": int(len(df))
    }
