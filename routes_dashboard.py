from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models import Participacao, Formacao, Lotacao

router = APIRouter(prefix="/api")


@router.get("/dashboard")
def dashboard(
    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
):
    db: Session = SessionLocal()

    try:
        query = db.query(Participacao).join(Formacao).join(Lotacao)

        # 📅 filtro período (formato: 2025-01)
        if mes_inicio:
            query = query.filter(
                func.to_char(Formacao.data_termino, "YYYY-MM") >= mes_inicio
            )

        if mes_fim:
            query = query.filter(
                func.to_char(Formacao.data_termino, "YYYY-MM") <= mes_fim
            )

        # 🏢 filtro lotação
        if lotacao:
            query = query.filter(Lotacao.tipo == lotacao)

        # 📚 filtro curso
        if curso:
            query = query.filter(Formacao.descricao == curso)

        total = query.count()

        # 📊 por lotação
        lotacao_data = (
            query.with_entities(func.trim(Lotacao.tipo), func.count())
            .group_by(Lotacao.tipo)
            .all()
        )

        # 📊 por curso
        curso_data = (
            query.with_entities(func.trim(Formacao.descricao), func.count())
            .group_by(Formacao.descricao)
            .all()
        )

        # 📊 por período
        periodo_data = (
            query.with_entities(
                func.to_char(Formacao.data_termino, "YYYY-MM"),
                func.count()
            )
            .group_by(func.to_char(Formacao.data_termino, "YYYY-MM"))
            .order_by(func.to_char(Formacao.data_termino, "YYYY-MM"))
            .all()
        )

        return {
            "total": total,
            "lotacao": [{"nome": l[0], "qtd": l[1]} for l in lotacao_data],
            "curso": [{"nome": c[0], "qtd": c[1]} for c in curso_data],
            "periodo": [{"mes": p[0], "qtd": p[1]} for p in periodo_data],
        }

    except Exception as e:
        return {"erro": str(e)}

    finally:
        db.close()
