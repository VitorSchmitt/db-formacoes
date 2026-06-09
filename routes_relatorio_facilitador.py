from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract

from database import SessionLocal
from models import Facilitador, Formacao

router = APIRouter(
    prefix="/api/relatorios",
    tags=["Relatórios"]
)

# ==========================
# DATABASE
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# RELATÓRIO ANUAL DE FACILITADORES
# =====================================================
@router.get("/facilitadores/{ano}")
def relatorio_facilitadores_anual(
    ano: int,
    db: Session = Depends(get_db)
):

    formacoes = (
        db.query(Formacao)
        .join(Facilitador)
        .filter(extract("year", Formacao.data_termino) == ano)
        .order_by(
            Facilitador.nome.asc(),
            Formacao.data_termino.asc()
        )
        .all()
    )

    resultado = {}

    for formacao in formacoes:

        nome_facilitador = (
            formacao.facilitador.nome
            if formacao.facilitador
            else "Sem Facilitador"
        )

        if nome_facilitador not in resultado:
            resultado[nome_facilitador] = []

        resultado[nome_facilitador].append({
            "id_formacao": formacao.id,
            "titulo": formacao.nome,
            "data_inicio": formacao.data_inicio,
            "data_termino": formacao.data_termino,
            "carga_horaria": formacao.carga_horaria
        })

    retorno = []

    for facilitador in sorted(resultado.keys()):

        total_formacoes = len(resultado[facilitador])

        total_horas = sum(
            f.get("carga_horaria", 0) or 0
            for f in resultado[facilitador]
        )

        retorno.append({
            "facilitador": facilitador,
            "quantidade_formacoes": total_formacoes,
            "total_horas": total_horas,
            "formacoes": resultado[facilitador]
        })

    return {
        "ano": ano,
        "total_facilitadores": len(retorno),
        "dados": retorno
    }
