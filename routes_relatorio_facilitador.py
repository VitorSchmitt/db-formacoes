from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract

from database import SessionLocal
from models import Facilitador, Formacao, Servidor

from io import BytesIO

from fastapi.responses import StreamingResponse

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

router = APIRouter(
    prefix="/api/relatorios",
    tags=["Relatórios"]
)

# ==========================================
# DATABASE
# ==========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# RELATÓRIO ANUAL DE FACILITADORES
# ==========================================

@router.get("/facilitadores/{ano}")
def relatorio_facilitadores_anual(
    ano: int,
    db: Session = Depends(get_db)
):
    try:

        facilitacoes = (
            db.query(Facilitador)
            .options(
                joinedload(Facilitador.servidor),
                joinedload(Facilitador.formacao)
            )
            .join(Facilitador.servidor)
            .join(Facilitador.formacao)
            .filter(                
                Formacao.data_termino.isnot(None),
                extract("year", Formacao.data_termino) == ano
            )
            .order_by(
                Servidor.nome.asc(),
                Formacao.data_termino.asc()
            )
            .all()
        )

        resultado = {}

        for item in facilitacoes:

            nome_facilitador = (
                item.servidor.nome
                if item.servidor
                else "Servidor não encontrado"
            )

            if nome_facilitador not in resultado:
                resultado[nome_facilitador] = []

            resultado[nome_facilitador].append({
                "id_formacao": item.formacao.id,
                "titulo": item.formacao.descricao,
                "data_inicio": (
                    item.formacao.data_inicio.strftime("%d/%m/%Y")
                    if item.formacao.data_inicio
                    else None
                ),
                "data_termino": (
                    item.formacao.data_termino.strftime("%d/%m/%Y")
                    if item.formacao.data_termino
                    else None
                ),
                "carga_horaria": item.formacao.carga_horaria or 0
            })

        retorno = []

        for facilitador in sorted(resultado.keys()):

            total_formacoes = len(resultado[facilitador])

            total_horas = sum(
                formacao["carga_horaria"]
                for formacao in resultado[facilitador]
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ==========================================
# RELATÓRIO ANUAL DE FACILITADORES - PDF
# ==========================================
@router.get("/facilitadores/{ano}/pdf")
def relatorio_facilitadores_pdf(
    ano: int,
    db: Session = Depends(get_db)
):

    facilitacoes = (
        db.query(Facilitador)
        .options(
            joinedload(Facilitador.servidor),
            joinedload(Facilitador.formacao)
        )
        .join(Facilitador.servidor)
        .join(Facilitador.formacao)
        .filter(
            Formacao.data_termino.isnot(None),
            extract("year", Formacao.data_termino) == ano
        )
        .order_by(
            Servidor.nome.asc(),
            Formacao.data_termino.asc()
        )
        .all()
    )

    resultado = {}

    for item in facilitacoes:

        nome = item.servidor.nome

        if nome not in resultado:
            resultado[nome] = []

        resultado[nome].append(item.formacao)

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elementos = []

    elementos.append(
        Paragraph(
            f"Relatório Anual de Facilitadores - {ano}",
            styles["Title"]
        )
    )

    elementos.append(Spacer(1, 20))

    for nome in sorted(resultado.keys()):

        formacoes = resultado[nome]

        total_horas = sum(
            f.carga_horaria or 0
            for f in formacoes
        )

        elementos.append(
            Paragraph(
                nome,
                styles["Heading2"]
            )
        )

        elementos.append(
            Paragraph(
                f"Formações: {len(formacoes)} | "
                f"Carga Horária Total: {total_horas}h",
                styles["Normal"]
            )
        )

        elementos.append(Spacer(1, 5))

        for formacao in formacoes:

            data_inicio = (
                formacao.data_inicio.strftime("%d/%m/%Y")
                if formacao.data_inicio
                else "-"
            )

            data_termino = (
                formacao.data_termino.strftime("%d/%m/%Y")
                if formacao.data_termino
                else "-"
            )

            elementos.append(
                Paragraph(
                    f"• {formacao.descricao} "
                    f"({data_inicio} a {data_termino}) "
                    f"- {formacao.carga_horaria or 0}h",
                    styles["Normal"]
                )
            )

        elementos.append(Spacer(1, 12))

    doc.build(elementos)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'inline; filename="relatorio_facilitadores_{ano}.pdf"'
        }
    )
