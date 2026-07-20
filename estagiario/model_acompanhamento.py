from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    Text,
    UniqueConstraint,
    Enum as SqlEnum
)
from sqlalchemy.orm import relationship

from database import Base
from estagiario.enums import AvaliacaoSupervisorEnum, StatusPagamentoEstagioEnum


class AvaliacaoSupervisor(Base):
    __tablename__ = "avaliacoes_supervisor"

    __table_args__ = (
        UniqueConstraint(
            "frequencia_id",
            name="uq_avaliacao_frequencia"
        ),
    )

    id = Column(Integer, primary_key=True)

    frequencia_id = Column(
        Integer,
        ForeignKey(
            "frequencias_estagio.id",
            ondelete="CASCADE"
        ),
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

    frequencia = relationship(
        "FrequenciaEstagio",
        back_populates="avaliacao"
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

    # Alterado para (6, 2) para permitir mais de 99.99 horas sem estourar o banco
    horas_realizadas = Column(
        Numeric(6, 2),
        nullable=False
    )

    observacao = Column(Text)

    status = Column(
        SqlEnum(
            StatusFolhaEnum,
            native_enum=False
        ),
        nullable=False,
        default=StatusFolhaEnum.ABERTA
    )

    # Relacionamentos
    contrato = relationship(
        "ContratoEstagio",
        back_populates="frequencias"
    )

    avaliacao = relationship(
        "AvaliacaoSupervisor",
        back_populates="frequencia",
        uselist=False,
        cascade="all, delete-orphan"
    )

    pagamento = relationship(
        "PagamentoEstagio",
        back_populates="frequencia",
        uselist=False,
        cascade="all, delete-orphan"
    )


class PagamentoEstagio(Base):
    __tablename__ = "pagamentos_estagio"

    __table_args__ = (
        UniqueConstraint(
            "frequencia_id",
            name="uq_pagamento_frequencia"
        ),
    )

    id = Column(Integer, primary_key=True)

    frequencia_id = Column(
        Integer,
        ForeignKey(
            "frequencias_estagio.id",
            name="fk_pagamento_frequencia",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    usuario_fechamento_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id",
            name="fk_pagamento_usuario_fechamento"
        ),
        nullable=False
    )

    data_fechamento = Column(
        Date,
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

    dias_referencia = Column(
        Integer,
        nullable=False
    )

    valor_encargo = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    # Relacionamentos
    frequencia = relationship(
        "FrequenciaEstagio",
        back_populates="pagamento"
    )

    usuario_fechamento = relationship(
        "Usuario"
    )
