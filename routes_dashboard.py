from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import Participacao, Servidor, Formacao, Lotacao

router = APIRouter()

@router.get("/dashboard")
def dashboard(
    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
):
    db = SessionLocal()

    try:
        query = db.query(Participacao)\
            .join(Formacao, Participacao.formacao_id == Formacao.id)\
            .join(Lotacao, Participacao.lotacao_id == Lotacao.id)

        if mes_inicio:
            query = query.filter(
                func.strftime('%Y-%m', Formacao.data_termino) >= mes_inicio
            )

        if mes_fim:
            query = query.filter(
                func.strftime('%Y-%m', Formacao.data_termino) <= mes_fim
            )

        total = query.count()

        lotacao_data = db.query(
            Lotacao.tipo,
            func.count()
        ).join(Participacao).join(Formacao).group_by(Lotacao.tipo).all()

        curso_data = db.query(
            Formacao.descricao,
            func.count()
        ).join(Participacao).join(Lotacao).group_by(Formacao.descricao).all()

        periodo_data = db.query(
            func.strftime('%Y-%m', Formacao.data_termino),
            func.count()
        ).join(Participacao).join(Lotacao).group_by(
            func.strftime('%Y-%m', Formacao.data_termino)
        ).all()

        return {
            "total": total,
            "lotacao": [{"nome": l[0], "qtd": l[1]} for l in lotacao_data],
            "curso": [{"nome": c[0], "qtd": c[1]} for c in curso_data],
            "periodo": [{"mes": p[0], "qtd": p[1]} for p in periodo_data],
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"erro": str(e)}

    finally:
        db.close()
