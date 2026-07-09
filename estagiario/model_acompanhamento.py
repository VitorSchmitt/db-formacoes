from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import relationship
from database import Base
from estagiario.enums import AvaliacaoSupervisorEnum
from sqlalchemy import Enum as SqlEnum



class AvaliacaoSupervisor(Base):
    __tablename__ = "avaliacoes_supervisor"

    id = Column(Integer, primary_key=True)

    contrato_id = Column(
        Integer,
        ForeignKey("contratos_estagio.id"),
        nullable=False
    )

    data_avaliacao = Column(
        Date,
        nullable=False
    )

    avaliacao = Column(
        SqlEnum(
            AvaliacaoSupervisorEnum,
            native_enum=False
        ),
        nullable=False
    )

    parecer = Column(Text)

    contrato = relationship(
        "ContratoEstagio",
        back_populates="avaliacoes"
    )

class FrequenciaEstagio(Base):
    __tablename__ = "frequencias_estagio"

    __table_args__ = (
        UniqueConstraint(
            "contrato_id",
            "competencia",
            name="uq_frequencia_contrato_data"
        ),
    )


    id = Column(Integer, primary_key=True)

    contrato_id = Column(
        Integer,
        ForeignKey("contratos_estagio.id"),
        nullable=False
    )

    competencia = Column(
        Date,
        nullable=False
    )

    dias = Column(
        Integer,
        nullable=False,
        default=0
    )

    horas_realizadas = Column(
        Numeric(4, 2),
        nullable=False
    )

    observacao = Column(Text)

    contrato = relationship(
        "ContratoEstagio",
        back_populates="frequencias"
    )


class PagamentoEstagio(Base):
    __tablename__ = "pagamentos_estagio"

    __table_args__ = (
        UniqueConstraint(
            "contrato_id",
            "competencia",
            name="uq_pagamento_competencia"
        ),
    )

    id = Column(Integer, primary_key=True)

    contrato_id = Column(
        Integer,
        ForeignKey("contratos_estagio.id"),
        nullable=False
    )

    competencia = Column(
        String(7),
        nullable=False
    )

    data_fechamento = Column(
        Date,
        nullable=False
    )

    horas_apuradas = Column(
        Numeric(6, 2),
        nullable=False
    )

    valor_hora_aplicado = Column(
        Numeric(10, 2),
        nullable=False
    )

    valor_vale_alimentacao = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    valor_vale_transporte = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    valor_total = Column(
        Numeric(10, 2),
        nullable=False
    )

    contrato = relationship(
        "ContratoEstagio",
        back_populates="pagamentos"
    )
