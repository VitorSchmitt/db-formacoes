from fastapi import APIRouter, Query
from sqlalchemy import func

from database import SessionLocal

from models import (
    Participacao,
    Formacao,
    Lotacao,
    PlanoAnual
)

router = APIRouter()


@router.get("/api/dashboard")
def dashboard(

    mes_inicio: str = Query(None),
    mes_fim: str = Query(None),
    lotacao: str = Query(None),
    curso: str = Query(None),
    eixo: str = Query(None)

):

    db = SessionLocal()

    try:

        # =====================================
        # QUERY BASE
        # =====================================

        base = (

            db.query(
                Participacao,
                Formacao,
                Lotacao,
                PlanoAnual
            )

            .join(
                Formacao,
                Participacao.formacao_id == Formacao.id
            )

            .join(
                Lotacao,
                Participacao.lotacao_id == Lotacao.id
            )

            .outerjoin(
                PlanoAnual,
                Formacao.plano_id == PlanoAnual.id
            )

        )

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


        if eixo:

            base = base.filter(
                PlanoAnual.eixo.isnot(None),
                PlanoAnual.eixo == eixo
            )


        # =====================================
        # PARTICIPAÇÕES
        # =====================================

        participacoes = base.all()

        total = len(participacoes)

        certificados = 0
        carga_realizada_total = 0


        for p, f, l, pa in participacoes:

            carga_total = (
                f.carga_horaria or 0
            )

            carga_realizada = (
                p.aproveitamento or 0
            )

            carga_realizada_total += (
                carga_realizada
            )

            percentual = 0

            if carga_total > 0:

                percentual = round(

                    (
                        carga_realizada
                        /
                        carga_total
                    ) * 100,

                    2
                )


            if percentual >= 75:

                certificados += 1


        evasao = total - certificados

        taxa_evasao = (

            round(
                (evasao / total) * 100,
                2
            )

            if total > 0
            else 0

        )


        servidores_unicos = len(

            set(
                [
                    p.matricula
                    for p, f, l, pa in participacoes
                ]
            )

        )


        media_por_servidor = (

            round(
                total / servidores_unicos,
                2
            )

            if servidores_unicos > 0
            else 0

        )


        # =====================================
        # LOTAÇÕES
        # =====================================

        lotacao_data = (

            base.with_entities(

                Lotacao.tipo,

                func.count()

            )

            .group_by(
                Lotacao.tipo
            )

            .order_by(
                func.count().desc()
            )

            .all()

        )


        # =====================================
        # CURSOS
        # =====================================

        curso_data = (

            base.with_entities(

                Formacao.descricao,

                func.count()

            )

            .group_by(
                Formacao.descricao
            )

            .order_by(
                func.count().desc()
            )

            .all()

        )


        # =====================================
        # PERÍODO
        # =====================================

        periodo_data = (

            base.with_entities(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ),

                func.count()

            )

            .group_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                )

            )

            .order_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                )

            )

            .all()

        )


        # =====================================
        # EIXO
        # =====================================

        eixo_data = (

            base.with_entities(

                PlanoAnual.eixo,

                func.count()

            )

            .group_by(
                PlanoAnual.eixo
            )

            .order_by(
                func.count().desc()
            )

            .all()

        )


        # =====================================
        # PERÍODO X EIXO
        # =====================================

        periodo_eixo_data = (

            base.with_entities(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ),

                PlanoAnual.eixo,

                func.count()

            )

            .group_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                ),

                PlanoAnual.eixo

            )

            .order_by(

                func.to_char(
                    Formacao.data_termino,
                    'YYYY-MM'
                )

            )

            .all()

        )


        # =====================================
        # ANUAL
        # =====================================

        anual_data = (

            base.with_entities(

                func.extract(
                    'year',
                    Formacao.data_termino
                ),

                func.count()

            )

            .group_by(

                func.extract(
                    'year',
                    Formacao.data_termino
                )

            )

            .order_by(

                func.extract(
                    'year',
                    Formacao.data_termino
                )

            )

            .all()

        )


        # =====================================
        # RESPONSE
        # =====================================

        return {

            "cards": {

                "participacoes": total,

                "certificados": certificados,

                "servidores_unicos": servidores_unicos,

                "evasao": evasao,

                "taxa_evasao": taxa_evasao,

                "carga_realizada": carga_realizada_total,

                "media_por_servidor": media_por_servidor

            },


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
            ],


            "eixo": [

                {
                    "eixo":
                        str(e[0])
                        if e[0]
                        else "Sem plano",

                    "qtd":
                        e[1]
                }

                for e in eixo_data
            ],


            "periodo_eixo": [

                {
                    "mes": p[0],

                    "eixo":
                        str(p[1])
                        if p[1]
                        else "Sem plano",

                    "qtd": p[2]
                }

                for p in periodo_eixo_data
            ],


            "anual": [

                {
                    "ano":
                        int(a[0])
                        if a[0]
                        else 0,

                    "qtd":
                        a[1]
                }

                for a in anual_data
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
