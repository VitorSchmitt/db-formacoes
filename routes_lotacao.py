from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from database import get_db
from models import Lotacao

router = APIRouter(prefix="/api/lotacoes", tags=["Lotação"])


# 📌 LISTAR TODAS AS LOTAÇÕES ATIVAS
@router.get("/")
def listar_lotacoes(db: Session = Depends(get_db)):
    stmt = (
        select(Lotacao)
        .where(Lotacao.ativo == True)
        .order_by(Lotacao.tipo, Lotacao.descricao)
    )

    result = db.execute(stmt).scalars().all()

    return [
        {
            "id": l.id,
            "descricao": l.descricao,
            "tipo": l.tipo
        }
        for l in result
    ]


# 📌 LISTAR AGRUPADO POR TIPO (resolve seu problema de repetição)
@router.get("/agrupadas")
def lotacoes_agrupadas(db: Session = Depends(get_db)):
    stmt = (
        select(Lotacao.tipo, Lotacao.id, Lotacao.descricao)
        .where(Lotacao.ativo == True)
        .order_by(Lotacao.tipo, Lotacao.descricao)
    )

    result = db.execute(stmt).all()

    agrupado = {}

    for tipo, id_, descricao in result:
        if tipo not in agrupado:
            agrupado[tipo] = []

        agrupado[tipo].append({
            "id": id_,
            "descricao": descricao
        })

    return agrupado


# 📌 CRIAR LOTAÇÃO
@router.post("/")
def criar_lotacao(payload: dict, db: Session = Depends(get_db)):
    nova = Lotacao(
        descricao=payload["descricao"],
        tipo=payload["tipo"]
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return {
        "id": nova.id,
        "descricao": nova.descricao,
        "tipo": nova.tipo
    }


# 📌 ATUALIZAR LOTAÇÃO
@router.put("/{lotacao_id}")
def atualizar_lotacao(lotacao_id: int, payload: dict, db: Session = Depends(get_db)):
    lotacao = db.get(Lotacao, lotacao_id)

    if not lotacao or not lotacao.ativo:
        raise HTTPException(status_code=404, detail="Lotação não encontrada")

    if "descricao" in payload:
        lotacao.descricao = payload["descricao"]

    if "tipo" in payload:
        lotacao.tipo = payload["tipo"]

    db.commit()

    return {"message": "Lotação atualizada com sucesso"}


# 📌 DESATIVAR (soft delete)
@router.delete("/{lotacao_id}")
def desativar_lotacao(lotacao_id: int, db: Session = Depends(get_db)):
    lotacao = db.get(Lotacao, lotacao_id)

    if not lotacao:
        raise HTTPException(status_code=404, detail="Lotação não encontrada")

    lotacao.ativo = False

    db.commit()

    return {"message": "Lotação desativada com sucesso"}
