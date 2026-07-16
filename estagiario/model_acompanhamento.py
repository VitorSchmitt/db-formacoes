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

    horas_realizadas = Column(
        Numeric(4, 2),
        nullable=False
    )

    observacao = Column(Text)

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


class PagamentoEstagio(Base):
    __tablename__ = "pagamentos_estagio"

    id = Column(Integer, primary_key=True)
    frequencia_id = Column(
        Integer,
        ForeignKey("frequencias_estagio.id"),
        nullable=False,
        unique=True
    )

    data_fechamento = Column(
        Date,
        nullable=False
    )

    valor_hora_aplicado = Column(
        Numeric(10,2),
        nullable=False
    )

    valor_vale_alimentacao = Column(
        Numeric(10,2),
        nullable=False,
        default=0
    )

    valor_vale_transporte = Column(
        Numeric(10,2),
        nullable=False,
        default=0
    )

    valor_total = Column(
        Numeric(10,2),
        nullable=False
    )

    frequencia = relationship(
        "FrequenciaEstagio",
        back_populates="pagamento"
    )
