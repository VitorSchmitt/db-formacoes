from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import relationship

from database import Base
from estagiario.enums import MotivoDesligamentoEnum, SexoEnum
from models import Lotacao, Servidor


class Estagiario(Base):
    __tablename__ = "estagiarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    sexo = Column(
        SqlEnum(SexoEnum, native_enum=False),
        nullable=False,
        default=SexoEnum.NAO_INFORMADO
    )
    cpf = Column(String(14), unique=True, nullable=False)
    data_nascimento = Column(Date)
    email = Column(String(200))
    telefone = Column(String(30))
    endereco = Column(Text)
    instituicao_ensino = Column(String(200))
    curso = Column(String(200))
    semestre = Column(String(20))
    ativo = Column(Boolean, default=True, nullable=False)
    observacoes = Column(Text)

    # Dados do Responsável Legal (Apenas para menores de idade)
    nome_responsavel = Column(String(200), nullable=True)
    cpf_responsavel = Column(String(14), nullable=True)
    parentesco_responsavel = Column(String(50), nullable=True)
    telefone_responsavel = Column(String(30), nullable=True)
    email_responsavel = Column(String(200), nullable=True)

    # Relacionamentos
    contratos = relationship(
        "ContratoEstagio",
        back_populates="estagiario",
        cascade="all, delete-orphan"
    )


class ClassificacaoEstagio(Base):
    __tablename__ = "classificacoes_estagio"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), nullable=False, unique=True, index=True)
    descricao = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    valores = relationship(
        "ValorBolsaEstagio",
        back_populates="classificacao",
        cascade="all, delete-orphan"
    )
    contratos = relationship(
        "ContratoEstagio",
        back_populates="classificacao"
    )

    def __repr__(self):
        return f"<ClassificacaoEstagio {self.codigo} - {self.descricao}>"


class ValorBolsaEstagio(Base):
    __tablename__ = "valores_bolsa_estagio"

    __table_args__ = (
        UniqueConstraint(
            "classificacao_id",
            "data_inicio_vigencia",
            name="uq_valor_bolsa_vigencia"
        ),
    )

    id = Column(Integer, primary_key=True)
    classificacao_id = Column(
        Integer,
        ForeignKey("classificacoes_estagio.id"),
        nullable=False
    )
    valor_hora = Column(Numeric(10, 2), nullable=False)
    data_inicio_vigencia = Column(Date, nullable=False)

    # Relacionamentos
    classificacao = relationship(
        "ClassificacaoEstagio",
        back_populates="valores"
    )


class BeneficioEstagiario(Base):
    __tablename__ = "beneficios_estagiario"

    id = Column(Integer, primary_key=True)
    valor_vale_alimentacao = Column(Numeric(10, 2), nullable=False, default=0)
    valor_vale_transporte = Column(Numeric(10, 2), nullable=False, default=0)
    data_inicio_vigencia = Column(Date, nullable=False, unique=True)


class ContratoEstagio(Base):
    __tablename__ = "contratos_estagio"

    id = Column(Integer, primary_key=True)

    # Chaves Estrangeiras
    estagiario_id = Column(
        Integer,
        ForeignKey("estagiarios.id"),
        nullable=False
    )
    lotacao_id = Column(
        Integer,
        ForeignKey("lotacao.id"),
        nullable=False
    )
    supervisor_matricula = Column(
        String(20),
        ForeignKey("servidor.matricula"),
        nullable=False
    )
    classificacao_id = Column(
        Integer,
        ForeignKey("classificacoes_estagio.id"),
        nullable=False
    )

    # Dados do Contrato
    numero_contrato = Column(String(30), unique=True, nullable=False)
    data_assinatura = Column(Date, nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    carga_horaria_diaria = Column(Integer, nullable=False)
    horario = Column(String(100), nullable=False)

    # Benefícios
    vale_alimentacao = Column(Boolean, nullable=False, default=False)
    quantidade_vale_transporte = Column(Integer, nullable=False, default=0)

    # Encerramento
    data_desligamento = Column(Date)
    motivo_desligamento = Column(
        SqlEnum(MotivoDesligamentoEnum, native_enum=False)
    )
    observacao_desligamento = Column(Text)
    observacoes = Column(Text)

    # Relacionamentos ORM
    estagiario = relationship(
        "Estagiario",
        back_populates="contratos"
    )
    frequencias = relationship(
        "FrequenciaEstagio",
        back_populates="contrato",
        cascade="all, delete-orphan"
    )
    lotacao = relationship(Lotacao)
    supervisor = relationship(Servidor)
    classificacao = relationship(
        "ClassificacaoEstagio",
        back_populates="contratos"
    )
