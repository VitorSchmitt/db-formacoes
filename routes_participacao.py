from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Participacao, Servidor, Formacao, Lotacao
from io import BytesIO
from fastapi.responses import StreamingResponse
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (    
    Table,    
    Paragraph,
    Spacer
)

from pdf_utils import (
    adicionar_cabecalho,
    criar_documento_pdf,
    aplicar_estilo_tabela,
    adicionar_data_emissao,
    obter_estilo_tabela
)


router = APIRouter()

# ===============================
# DB
# ===============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from sqlalchemy import select


# ===============================
# LISTAR POR FORMAÇÃO
# ===============================
@router.get("/api/participacoes/{formacao_id}")
def listar(formacao_id: int, db: Session = Depends(get_db)):

    dados = db.query(Participacao)\
        .join(Servidor)\
        .join(Formacao)\
        .outerjoin(Lotacao)\
        .filter(Participacao.formacao_id == formacao_id)\
        .order_by(Servidor.nome)\
        .all()

    return [
    {
        "id": p.id,
        "matricula": p.matricula,
        "nome": p.servidor.nome if p.servidor else None,
        "lotacao": p.lotacao.descricao if p.lotacao else None,
        "aproveitamento": p.aproveitamento
    }
    for p in dados
]

# ===============================
# LISTAR POR FORMAÇÃO - PDF
# ===============================

@router.get("/api/participacoes/{formacao_id}/relatorio")
def relatorio_pdf(
    formacao_id: int,
    db: Session = Depends(get_db)
):

    formacao = db.get(Formacao, formacao_id)

    if not formacao:
        return {"erro": "Formação não encontrada"}

    carga_minima = formacao.carga_horaria * 0.75

    participantes = (
        db.query(Participacao)
        .join(Servidor)
        .outerjoin(Lotacao)
        .filter(
            Participacao.formacao_id == formacao_id,
            Participacao.aproveitamento >= carga_minima
        )
        .order_by(Servidor.nome)
        .all()
    )

    buffer = BytesIO()

    doc = criar_documento_pdf(buffer,orientacao="portrait")

    styles = getSampleStyleSheet()
    estilo_tabela = obter_estilo_tabela()
    elementos = []

    adicionar_cabecalho(
        elementos,       
        "RELATÓRIO DE PARTICIPAÇÃO EM FORMAÇÃO"
    )    
    
    elementos.append(
        Paragraph(
            f"<b>Formação:</b> {formacao.descricao}",
            styles["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"<b>Carga Horária:</b> {formacao.carga_horaria} horas",
            styles["Normal"]
        )
    )

    elementos.append(Spacer(1,0.5*cm))

    tabela = [[
        "Matrícula",
        "Nome",
        "Lotação",
        "Aproveitamento"
    ]]

    for p in participantes:

        tabela.append([
            Paragraph(str(p.matricula), estilo_tabela),
            Paragraph(p.servidor.nome, estilo_tabela),
            Paragraph(p.lotacao.descricao if p.lotacao else "", estilo_tabela),
            Paragraph(f"{p.aproveitamento} h", estilo_tabela),
        ])

    tabela_pdf = Table(
        tabela,
        colWidths=[2.2*cm,8.5*cm,6.2*cm,2.1*cm]
    )

    aplicar_estilo_tabela(
    tabela_pdf,
        estilos_extras=[
            ("WORDWRAP", (0,0), (-1,-1), "CJK"),
        ]
    )

    elementos.append(tabela_pdf)

    elementos.append(Spacer(1,0.5*cm))

    elementos.append(
        Paragraph(
            f"<b>Total de aprovados:</b> {len(participantes)}",
            styles["Normal"]
        )
    )

    doc.build(elementos)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'inline; filename="participacao_{formacao_id}.pdf"'
        }
    )

# ===============================
# CRIAR
# ===============================
@router.post("/api/participacoes")
def criar(dados: dict, db: Session = Depends(get_db)):

    # 🔴 VALIDAÇÃO BACKEND (obrigatório)
    if not dados.get("matricula"):
        return {"erro": "Matrícula obrigatória"}

    if not dados.get("formacao_id"):
        return {"erro": "Formação obrigatória"}

    if not dados.get("lotacao_id"):
        return {"erro": "Lotação obrigatória"}

    if not dados.get("aproveitamento"):
        return {"erro": "Aproveitamento obrigatório"}
        
    if dados.get("aproveitamento") is None:
        return {"erro": "Aproveitamento obrigatório"}

    formacao = db.get(Formacao, dados["formacao_id"])
    
    if not formacao:
        return {"erro": "Formação não encontrada"}
    
    if float(dados["aproveitamento"]) > formacao.carga_horaria:
        return {
            "erro": f"Aproveitamento maior que a carga horária da formação ({formacao.carga_horaria}h)"
        }

    # 🔎 validar existência
    servidor = db.get(Servidor, dados["matricula"])
    if not servidor:
        return {"erro": "Servidor não encontrado"}

    lotacao = db.get(Lotacao, dados["lotacao_id"])
    if not lotacao:
        return {"erro": "Lotação inválida"}

    # 🚫 evitar duplicidade
    existe = db.query(Participacao).filter_by(
        matricula=dados["matricula"],
        formacao_id=dados["formacao_id"]
    ).first()

    if existe:
        return {"erro": "Servidor já está nesta formação"}

    try:
        nova = Participacao(
            matricula=dados["matricula"],
            formacao_id=dados["formacao_id"],
            lotacao_id=dados["lotacao_id"],
            aproveitamento=dados["aproveitamento"]
        )

        db.add(nova)
        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}


# ===============================
# ATUALIZAR
# ===============================
@router.put("/api/participacoes/{id}")
def atualizar(id: int, dados: dict, db: Session = Depends(get_db)):

    p = db.get(Participacao, id)

    if not p:
        return {"erro": "Participação não encontrada"}

    # 🔴 VALIDAÇÃO
    if not dados.get("lotacao_id"):
        return {"erro": "Lotação obrigatória"}

    if not dados.get("aproveitamento"):
        return {"erro": "Aproveitamento obrigatório"}

    try:
        p.lotacao_id = dados["lotacao_id"]
        p.aproveitamento = dados["aproveitamento"]

        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}


# ===============================
# DELETAR
# ===============================
@router.delete("/api/participacoes/{id}")
def deletar(id: int, db: Session = Depends(get_db)):

    p = db.get(Participacao, id)

    if not p:
        return {"erro": "Participação não encontrada"}

    try:
        db.delete(p)
        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}

@router.get("/api/lotacoes/ativas")
def listar_lotacoes_ativas(db: Session = Depends(get_db)):

    stmt = (
        select(Lotacao)
        .where(Lotacao.ativo == True)
        .order_by(Lotacao.tipo, Lotacao.descricao)
    )

    lotacoes = db.execute(stmt).scalars().all()

    return [
        {
            "id": l.id,
            "descricao": l.descricao,
            "tipo": l.tipo
        }
        for l in lotacoes
    ]
@router.get("/api/servidores/ativos")
def listar_servidores_ativos(db: Session = Depends(get_db)):

    dados = (
        db.query(Servidor)
        .where(Servidor.ativo == True)
        .order_by(Servidor.nome)
        .all()
    )

    return [
        {
            "matricula": s.matricula,
            "nome": s.nome,
        }
        for s in dados
    ]

@router.get("/api/formacoes/ativas")
def listar_formacoes_ativas(db: Session = Depends(get_db)):

    dados = (
    db.query(Formacao)
    .filter(Formacao.ativo == True)
    .order_by(Formacao.data_termino.desc())
    .all()
)

    return [
        {
            "id": f.id,
            "descricao": f.descricao
        }
        for f in dados
    ]
    
@router.get("/api/servidores/matricula/{matricula}")
def buscar_servidor(matricula: str, db: Session = Depends(get_db)):

    servidor = db.query(Servidor).filter(
        Servidor.matricula == matricula
    ).first()

    if not servidor:
        return {"encontrado": False}

    return {
        "encontrado": True,
        "matricula": servidor.matricula,
        "nome": servidor.nome       
       
    }

@router.get("/lotacoes")
def buscar_lotacoes(termo: str):

    return (
        db.query(Lotacao)
        .filter(Lotacao.nome.ilike(f"%{termo}%"))
        .all()
    )
