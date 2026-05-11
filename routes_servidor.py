from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import Servidor, Cargo
from schemas import ServidorCreate, ServidorUpdate

router = APIRouter(
    prefix="/api/servidores",
    tags=["Servidor"]
)


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
# LISTAR SERVIDORES
# ===============================
@router.get("/")
def listar(db: Session = Depends(get_db)):

    dados = (
        db.query(Servidor)
        .options(joinedload(Servidor.cargo))
        .order_by(Servidor.nome)
        .all()
    )

    return [
        {
            "matricula": s.matricula,
            "nome": s.nome,
            "cargo": s.cargo.descricao if s.cargo else None,
            "cargo_id": s.cargo_id,
            "ativo": s.ativo,
        }
        for s in dados
    ]


# ===============================
# LISTAR CARGOS
# ===============================
@router.get("/cargos")
def listar_cargos(db: Session = Depends(get_db)):

    cargos = db.query(Cargo).order_by(Cargo.descricao).all()

    return [
        {
            "id": c.id,
            "descricao": c.descricao
        }
        for c in cargos
    ]


# ===============================
# CRIAR SERVIDOR
# ===============================
@router.post("/")
def criar(dados: ServidorCreate, db: Session = Depends(get_db)):

    if not dados.matricula or not dados.nome or not dados.cargo_id:
        return {"erro": "Preencha todos os campos"}

    cargo = db.get(Cargo, dados.cargo_id)

    if not cargo:
        return {"erro": "Cargo inválido"}

    try:

        novo = Servidor(
            matricula=dados.matricula,
            nome=dados.nome,
            cargo_id=dados.cargo_id,
            ativo=True
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)

        return {
            "ok": True,
            "matricula": novo.matricula,
            "nome": novo.nome,
            "cargo_id": novo.cargo_id,
            "ativo": novo.ativo
        }

    except IntegrityError:
        db.rollback()
        return {"erro": "Servidor já cadastrado"}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}


# ===============================
# ATUALIZAR SERVIDOR
# ===============================
@router.put("/{matricula}")
def atualizar(
    matricula: str,
    dados: ServidorUpdate,
    db: Session = Depends(get_db)
):

    s = db.get(Servidor, matricula)

    if not s:
        return {"erro": "Servidor não encontrado"}

    cargo = db.get(Cargo, dados.cargo_id)

    if not cargo:
        return {"erro": "Cargo inválido"}

    try:

        s.nome = dados.nome
        s.cargo_id = dados.cargo_id

        db.commit()

        return {"ok": True}

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}


# =====================================================
# TOGGLE ATIVO / INATIVO
# =====================================================
@router.patch("/toggle/{matricula}")
def toggle_servidor(
    matricula: str,
    db: Session = Depends(get_db)
):

    servidor = db.get(Servidor, matricula)

    if not servidor:
        raise HTTPException(
            status_code=404,
            detail="Servidor não encontrado"
        )

    servidor.ativo = not servidor.ativo

    db.commit()

    return {
        "ok": True,
        "ativo": servidor.ativo
    }


# ===============================
# DESATIVAR SERVIDOR
# ===============================
@router.delete("/{matricula}")
def deletar(
    matricula: str,
    db: Session = Depends(get_db)
):

    s = db.get(Servidor, matricula)

    if not s:
        return {"erro": "Servidor não encontrado"}

    try:

        s.ativo = False

        db.commit()

        return {
            "ok": True,
            "message": "Servidor desativado com sucesso"
        }

    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
