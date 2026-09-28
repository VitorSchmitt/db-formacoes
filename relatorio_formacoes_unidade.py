from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
from io import BytesIO

from database import SessionLocal
from models import Servidor, Lotacao, Participacao, Formacao


router = APIRouter(
    prefix="/relatorio-formacoes-unidade",
    tags=["Relatório de Formações por Unidade"]
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# LISTAR LOTAÇÕES
# =========================================================

@router.get("/lotacoes")
def listar_lotacoes(
    db: Session = Depends(get_db)
):
    lotacoes = (
        db.query(Lotacao)
        .filter(Lotacao.ativo == True)
        .order_by(Lotacao.descricao)
        .all()
    )

    return [
        {
            "id": lotacao.id,
            "descricao": lotacao.descricao
        }
        for lotacao in lotacoes
    ]


# =========================================================
# CONSULTAR RELATÓRIO
# =========================================================

@router.get("/")
def relatorio_formacoes_unidade(
    lotacao_id: int = Query(...),
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # UNIDADE
    # -----------------------------------------------------

    lotacao = (
        db.query(Lotacao)
        .filter(Lotacao.id == lotacao_id)
        .first()
    )

    if not lotacao:
        return {
            "erro": "Lotação não encontrada."
        }

    # -----------------------------------------------------
    # SERVIDORES ATIVOS DA UNIDADE
    # -----------------------------------------------------

    servidores = (
        db.query(Servidor)
        .filter(
            Servidor.lotacao_id == lotacao_id,
            Servidor.ativo == True
        )
        .order_by(Servidor.nome)
        .all()
    )

    resultado = []

    total_servidores = len(servidores)
    total_com_formacao = 0
    total_sem_formacao = 0
    total_participacoes = 0

    # -----------------------------------------------------
    # FORMAÇÕES DE CADA SERVIDOR
    # -----------------------------------------------------

    for servidor in servidores:

        participacoes = (
            db.query(Participacao)
            .join(
                Formacao,
                Formacao.id == Participacao.formacao_id
            )
            .filter(
                Participacao.matricula == servidor.matricula,

                Formacao.data_inicio >= data_inicio,
                Formacao.data_inicio <= data_fim
            )
            .order_by(Formacao.data_inicio)
            .all()
        )

        formacoes = []

        for participacao in participacoes:

            formacao = participacao.formacao
        
            aproveitamento = (
                (participacao.aproveitamento / formacao.carga_horaria) * 100
                if formacao.carga_horaria
                else 0
            )
        
            formacoes.append({
                "id": formacao.id,
                "descricao": formacao.descricao,
                "data_inicio": formacao.data_inicio,
                "data_termino": formacao.data_termino,
                "carga_horaria": formacao.carga_horaria or 0,
                "aproveitamento": aproveitamento
            })

        if formacoes:
            total_com_formacao += 1
            total_participacoes += len(formacoes)
        else:
            total_sem_formacao += 1

        resultado.append({
            "matricula": servidor.matricula,
            "nome": servidor.nome,
            "formacoes": formacoes,
            "realizou": bool(formacoes)
        })

    # -----------------------------------------------------
    # TOTAL DE CARGA HORÁRIA
    # -----------------------------------------------------

    total_carga_horaria = sum(
        formacao["carga_horaria"]
        for servidor in resultado
        for formacao in servidor["formacoes"]
    )

    # -----------------------------------------------------
    # RETORNO
    # -----------------------------------------------------

    return {
        "lotacao": {
            "id": lotacao.id,
            "descricao": lotacao.descricao
        },

        "periodo": {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        },

        "totais": {
            "servidores": total_servidores,
            "com_formacao": total_com_formacao,
            "sem_formacao": total_sem_formacao,
            "participacoes": total_participacoes,
            "carga_horaria": total_carga_horaria
        },

        "servidores": resultado
    }



# =========================================================
# PDF
# =========================================================

@router.get("/pdf")
def relatorio_formacoes_unidade_pdf(
    lotacao_id: int = Query(...),
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # UNIDADE
    # -----------------------------------------------------

    lotacao = (
        db.query(Lotacao)
        .filter(Lotacao.id == lotacao_id)
        .first()
    )

    if not lotacao:
        return {
            "erro": "Lotação não encontrada."
        }

    # -----------------------------------------------------
    # SERVIDORES
    # -----------------------------------------------------

    servidores = (
        db.query(Servidor)
        .filter(
            Servidor.lotacao_id == lotacao_id,
            Servidor.ativo == True
        )
        .order_by(Servidor.nome)
        .all()
    )

    dados = []

    total_com_formacao = 0
    total_sem_formacao = 0
    total_participacoes = 0
    total_carga_horaria = 0

    for servidor in servidores:

        participacoes = (
            db.query(Participacao)
            .join(
                Formacao,
                Formacao.id == Participacao.formacao_id
            )
            .filter(
                Participacao.matricula == servidor.matricula,
                Formacao.data_inicio >= data_inicio,
                Formacao.data_inicio <= data_fim
            )
            .order_by(Formacao.data_inicio)
            .all()
        )

        if participacoes:
            total_com_formacao += 1
        else:
            total_sem_formacao += 1

        total_participacoes += len(participacoes)

        formacoes = []

        for participacao in participacoes:

            formacao = participacao.formacao

            carga = formacao.carga_horaria or 0
            total_carga_horaria += carga

            formacoes.append({
                "descricao": formacao.descricao,
                "data_inicio": formacao.data_inicio,
                "data_termino": formacao.data_termino,
                "carga_horaria": carga,
                "aproveitamento": participacao.aproveitamento
            })

        dados.append({
            "matricula": servidor.matricula,
            "nome": servidor.nome,
            "formacoes": formacoes
        })

    # -----------------------------------------------------
    # GERAR PDF
    # -----------------------------------------------------

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )
    from reportlab.lib.units import cm

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()

    titulo = styles["Title"]
    titulo.alignment = TA_CENTER

    elementos = []

    elementos.append(
        Paragraph(
            "RELATÓRIO DE FORMAÇÕES POR UNIDADE",
            titulo
        )
    )

    elementos.append(Spacer(1, 10))

    elementos.append(
        Paragraph(
            f"<b>Unidade:</b> {lotacao.descricao}",
            styles["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"<b>Período:</b> "
            f"{data_inicio.strftime('%d/%m/%Y')} "
            f"a "
            f"{data_fim.strftime('%d/%m/%Y')}",
            styles["Normal"]
        )
    )

    elementos.append(Spacer(1, 10))

    # -----------------------------------------------------
    # RESUMO
    # -----------------------------------------------------

    resumo = [
        ["Total de servidores", len(servidores)],
        ["Com formação", total_com_formacao],
        ["Sem formação", total_sem_formacao],
        ["Total de participações", total_participacoes],
        ["Carga horária realizada", f"{total_carga_horaria} h"]
    ]

    tabela_resumo = Table(
        resumo,
        colWidths=[9 * cm, 5 * cm]
    )

    tabela_resumo.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    elementos.append(tabela_resumo)
    elementos.append(Spacer(1, 15))

    # -----------------------------------------------------
    # SERVIDORES
    # -----------------------------------------------------

    for servidor in dados:

        elementos.append(
            Paragraph(
                f"<b>{servidor['matricula']} - "
                f"{servidor['nome']}</b>",
                styles["Heading4"]
            )
        )

        if not servidor["formacoes"]:

            elementos.append(
                Paragraph(
                    "<b>Não realizou formação no período.</b>",
                    styles["Normal"]
                )
            )

        else:

            estilo_tabela = styles["Normal"]
            estilo_tabela.fontName = "Helvetica"
            estilo_tabela.fontSize = 7.5
            estilo_tabela.leading = 9
            
            estilo_cabecalho = styles["Normal"]
            estilo_cabecalho.fontName = "Helvetica-Bold"
            estilo_cabecalho.fontSize = 7.5
            estilo_cabecalho.leading = 9
            
            tabela = [
                [
                    Paragraph("Formação", estilo_cabecalho),
                    Paragraph("Início", estilo_cabecalho),
                    Paragraph("Término", estilo_cabecalho),
                    Paragraph("Carga", estilo_cabecalho)
                ]
            ]
            
            for formacao in servidor["formacoes"]:
            
                tabela.append([
                    Paragraph(
                        str(formacao["descricao"]),
                        estilo_tabela
                    ),
                    Paragraph(
                        formacao["data_inicio"].strftime("%d/%m/%Y")
                        if formacao["data_inicio"] else "",
                        estilo_tabela
                    ),
                    Paragraph(
                        formacao["data_termino"].strftime("%d/%m/%Y")
                        if formacao["data_termino"] else "",
                        estilo_tabela
                    ),
                    Paragraph(
                        f"{formacao['carga_horaria']} h",
                        estilo_tabela
                    )
                ])

            tabela_formacoes = Table(
                tabela,
                colWidths=[
                    10.5 * cm,
                    2.3 * cm,
                    2.3 * cm,
                    1.8 * cm
                ],
                repeatRows=1
            )

            tabela_formacoes.setStyle(
                TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ])
            )

            elementos.append(tabela_formacoes)

        elementos.append(Spacer(1, 10))

    doc.build(elementos)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "inline; filename=relatorio_formacoes_unidade.pdf"
        }
    )
