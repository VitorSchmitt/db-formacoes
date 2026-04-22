from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import get_db

import pandas as pd

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# =========================
# PÁGINA DASHBOARD
# =========================
@app.get("/web/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# =========================
# API DADOS DASHBOARD
# =========================
@app.get("/api/dashboard")
def api_dashboard(db: Session = Depends(get_db)):

    dados = db.query(models.Participacao).all()

    lista = []
    for p in dados:
        lista.append({
            "formacao": p.formacao.descricao if p.formacao else "",
            "lotacao": p.lotacao.descricao if p.lotacao else "",
            "data": p.formacao.data_inicio if p.formacao else None
        })

    df = pd.DataFrame(lista)

    if df.empty:
        return {"lotacao": [], "curso": [], "periodo": [], "total": 0}

    df["data"] = pd.to_datetime(df["data"])
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    return {
        "lotacao": df.groupby("lotacao").size().reset_index(name="qtd").to_dict("records"),
        "curso": df.groupby("formacao").size().reset_index(name="qtd").to_dict("records"),
        "periodo": df.groupby("mes").size().reset_index(name="qtd").to_dict("records"),
        "total": len(df)
    }
