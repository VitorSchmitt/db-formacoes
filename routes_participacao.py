from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Participacao, Servidor, Formacao, Lotacao

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
# CRIAR
# ===============================
@router.post("/api/participacao")
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

    # 🔎 validar existência
    servidor = db.get(Servidor, dados["matricula"])
    if not servidor:
        return {"erro": "Servidor não encontrado"}

    formacao = db.get(Formacao, dados["formacao_id"])
    if not formacao:
        return {"erro": "Formação não encontrada"}

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
@router.put("/api/participacao/{id}")
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
@router.delete("/api/participacao/{id}")
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
