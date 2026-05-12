from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import Participacao, Formacao, Lotacao

router = APIRouter()


@router.get("/api/dashboard")
def dashboard(
    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
):

    db = SessionLocal()

    try:

        # =====================================
        # QUERY BASE
        # =====================================
        base = db.query(
            Participacao,
            Formacao,
            Lotacao
        )\
        .join(Formacao, Participacao.formacao_id == Formacao.id)\
        .join(Lotacao, Participacao.lotacao_id == Lotacao.id)

        # =====================================
        # FILTROS
        # =====================================
        if mes_inicio:
            base = base.filter(
                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ) >= mes_inicio
            )

        if mes_fim:
            base = base.filter(
                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ) <= mes_fim
            )

        if lotacao:
            base = base.filter(
                Lotacao.tipo == lotacao
            )

        if curso:
            base = base.filter(
                Formacao.descricao == curso
            )

        # =====================================
        # TOTAL
        # =====================================
        total = base.count()

        # =====================================
        # LOTAÇÕES
        # =====================================
        lotacao_data = base.with_entities(
            Lotacao.tipo,
            func.count()
        )\
        .group_by(Lotacao.tipo)\
        .order_by(func.count().desc())\
        .all()

        # =====================================
        # CURSOS
        # =====================================
        curso_data = base.with_entities(
            Formacao.descricao,
            func.count()
        )\
        .group_by(Formacao.descricao)\
        .order_by(func.count().desc())\
        .all()

        # =====================================
        # PERÍODO
        # =====================================
        periodo_data = base.with_entities(
            func.to_char(
                Formacao.data_termino,
                'YYYY-MM'
            ),
            func.count()
        )\
        .group_by(
            func.to_char(
                Formacao.data_termino,
                'YYYY-MM'
            )
        )\
        .order_by(
            func.to_char(
                Formacao.data_termino,
                'YYYY-MM'
            )
        )\
        .all()

        # =====================================
        # RESPONSE
        # =====================================
        return {

            "total": total,

            "lotacao": [
                {
                    "lotacao": l[0],
                    "qtd": l[1]
                }
                for l in lotacao_data
            ],

            "curso": [
                {
                    "formacao": c[0],
                    "qtd": c[1]
                }
                for c in curso_data
            ],

            "periodo": [
                {
                    "mes": p[0],
                    "qtd": p[1]
                }
                for p in periodo_data
            ]
        }

    except Exception as e:

        import traceback
        traceback.print_exc()

        return {
            "erro": str(e)
        }

    finally:
        db.close()
