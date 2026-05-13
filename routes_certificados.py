from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Participacao, Formacao
from reportlab.lib.units import cm
from tempfile import NamedTemporaryFile
from datetime import datetime
import os

ASSINANTE = "Jamille de Freitas Serres"

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# =========================
# DATABASE
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def gerar_pdf_certificado(
    dados,
    caminho_pdf
):

    styles = getSampleStyleSheet()


    # =========================
    # ESTILOS
    # =========================

    estilo_titulo = ParagraphStyle(
        "titulo",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=6
    )

    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=20
    )

    estilo_texto = ParagraphStyle(
        "texto",
        parent=styles["BodyText"],
        alignment=TA_JUSTIFY,
        fontSize=12,
        leading=18
    )

    estilo_lista = ParagraphStyle(
        "lista",
        parent=styles["BodyText"],
        fontSize=12,
        leftIndent=20
    )

    estilo_assinatura = ParagraphStyle(
        "assinatura",
        parent=styles["BodyText"],
        fontSize=12,
        spaceBefore=40
    )


    # =========================
    # DOCUMENTO
    # =========================

    doc = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elementos = []


    # =========================
    # TÍTULO
    # =========================

    elementos.append(
        Paragraph(
            "Declaração de Participação em Formação",
            estilo_titulo
        )
    )

    elementos.append(
        Paragraph(
            "Declaração Curricular",
            estilo_subtitulo
        )
    )

    elementos.append(
        Spacer(1, 12)
    )


    # =========================
    # TEXTO
    # =========================

    texto = (
        f"Para efeito de comprovação curricular, "
        f"certificamos que "
        f"<b>{dados['nome']}</b> "
        f"participou da formação intitulada "
        f"<b>{dados['formacao']}</b>. "
        f"Esta iniciativa foi promovida pela "
        f"Coordenação de Formação Permanente, "
        f"por meio do Núcleo de Treinamento, "
        f"Estágios e Voluntários."
    )

    elementos.append(
        Paragraph(texto, estilo_texto)
    )

    elementos.append(
        Spacer(1, 16)
    )


    # =========================
    # DETALHES
    # =========================

    elementos.append(
        Paragraph(
            "<b>Detalhes da Formação</b>",
            estilo_texto
        )
    )

    lista = ListFlowable(
        [

            ListItem(
                Paragraph(
                    f"Data de conclusão: {dados['fim']}",
                    estilo_lista
                )
            ),

            ListItem(
                Paragraph(
                    "Modalidade: Híbrido",
                    estilo_lista
                )
            ),

            ListItem(
                Paragraph(
                    f"Carga horária total: "
                    f"{dados['carga_total']}h",
                    estilo_lista
                )
            ),

            ListItem(
                Paragraph(
                    f"Carga horária realizada: "
                    f"{dados['carga_realizada']}h",
                    estilo_lista
                )
            ),

            ListItem(
                Paragraph(
                    f"Aproveitamento: "
                    f"{dados['percentual']}%",
                    estilo_lista
                )
            )

        ],
        bulletType="bullet",
        start="•"
    )

    elementos.append(lista)

    elementos.append(
        Spacer(1, 20)
    )


    # =========================
    # DATA
    # =========================

    elementos.append(
        Paragraph(
            f"Porto Alegre, "
            f"{dados['data_emissao']}",
            estilo_texto
        )
    )

    elementos.append(
        Spacer(1, 30)
    )


    # =========================
    # ASSINATURA
    # =========================

    elementos.append(
        Paragraph(
            "_" * 40,
            estilo_texto
        )
    )

    elementos.append(
        Paragraph(
            ASSINANTE,
            estilo_assinatura
        )
    )

    elementos.append(
        Spacer(1, 40)
    )


    # =========================
    # CÓDIGO
    # =========================

    elementos.append(
        Paragraph(
            f"Código: {dados['codigo']}",
            estilo_texto
        )
    )


    doc.build(elementos)
# =========================
# TELA
# =========================
@router.get("/web/certificados")
def tela_certificados(
    request: Request
):
    return templates.TemplateResponse(
        "certificados.html",
        {
            "request": request
        }
    )


# =========================
# FORMAÇÕES
# =========================
@router.get("/api/certificados/formacoes")
def listar_formacoes(
    db: Session = Depends(get_db)
):

    dados = (
        db.query(Formacao)
        .filter(Formacao.ativo == True)
        .order_by(Formacao.descricao)
        .all()
    )

    return [
        {
            "id": f.id,
            "descricao": f.descricao
        }
        for f in dados
    ]


# =========================
# APTOS AO CERTIFICADO
# =========================
@router.get("/api/certificados/{formacao_id}")
def listar_aptos(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    participacoes = (
        db.query(Participacao)
        .join(Formacao)
        .filter(
            Participacao.formacao_id == formacao_id
        )
        .all()
    )

    resultado = []

    for p in participacoes:

        carga_total = p.formacao.carga_horaria or 0
        carga_realizada = p.aproveitamento or 0

        percentual = 0

        if carga_total > 0:

            percentual = round(
                (carga_realizada / carga_total) * 100,
                2
            )

        if percentual >= 75:

            resultado.append({
                "participacao_id": p.id,
                "matricula": p.matricula,
                "servidor": p.servidor.nome,
                "formacao": p.formacao.descricao,
                "carga_total": carga_total,
                "carga_realizada": carga_realizada,
                "percentual": percentual
            })

    return resultado

@router.get("/api/certificados/pdf/{participacao_id}")
def gerar_certificado_pdf(
    participacao_id: int,
    db: Session = Depends(get_db)
):

    participacao = (
        db.query(Participacao)
        .filter(
            Participacao.id == participacao_id
        )
        .first()
    )

    if not participacao:

        return {
            "erro": "Participação não encontrada"
        }


    # =========================
    # DADOS
    # =========================

    carga_total = (
        participacao.formacao.carga_horaria or 0
    )

    carga_realizada = (
        participacao.aproveitamento or 0
    )

    percentual = 0

    if carga_total > 0:

        percentual = round(
            (carga_realizada / carga_total) * 100,
            2
        )


    codigo = (
        f"CERT-"
        f"{participacao.id:06d}"
    )


    dados = {

        "nome":
            participacao.servidor.nome,

        "formacao":
            participacao.formacao.descricao,

        "fim":
            participacao.formacao.data_fim.strftime("%d/%m/%Y")
            if participacao.formacao.data_fim
            else "",

        "carga_total":
            carga_total,

        "carga_realizada":
            carga_realizada,

        "percentual":
            percentual,

        "codigo":
            codigo,

        "data_emissao":
            datetime.now().strftime("%d/%m/%Y")
    }


    # =========================
    # ARQUIVO TEMPORÁRIO
    # =========================

    nome_arquivo = (
        participacao.servidor.nome
        .replace(" ", "_")
    )

    temp = NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    caminho_pdf = temp.name

    temp.close()


    # =========================
    # GERAR PDF
    # =========================

    gerar_pdf_certificado(
        dados,
        caminho_pdf
    )


    # =========================
    # DOWNLOAD
    # =========================

    return FileResponse(
        caminho_pdf,
        media_type="application/pdf",
        filename=(
            f"certificado_"
            f"{nome_arquivo}.pdf"
        )
    )
