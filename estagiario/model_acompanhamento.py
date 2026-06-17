from sqlalchemy import (
    Column,
    Integer,
    Date,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship

from database import Base


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

    nota = Column(Integer)

    parecer = Column(Text)

    contrato = relationship(
        "ContratoEstagio",
        back_populates="avaliacoes"
    )

from sqlalchemy import (
    Column,
    Integer,
    Date,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship

from database import Base


class FrequenciaEstagio(Base):
    __tablename__ = "frequencias_estagio"

    id = Column(Integer, primary_key=True)

    contrato_id = Column(
        Integer,
        ForeignKey("contratos_estagio.id"),
        nullable=False
    )

    data = Column(
        Date,
        nullable=False
    )

    horas_realizadas = Column(
        Integer,
        nullable=False
    )

    observacao = Column(Text)

    contrato = relationship(
        "ContratoEstagio"
    )
