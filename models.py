from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    Numeric,
    Float,
    CheckConstraint
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime

from database import Base

# ===============================
# ENUMS
# ===============================

tipo_modalidade = ENUM(
    "presencial",
    "online",
    "hibrido",
    name="tipo_modalidade",
    create_type=False
)

tipo_eixo = ENUM(
    "Ambientação Institucional/Formação Inicial",
    "Gestão do Trabalho/Saúde Mental e Bem Estar",
    "Qualificação da Prática Socioeducativa Temas Transversais",
    name="tipo_eixo",
    create_type=False
)

tipo_status_formacao = ENUM(
    "Planejada",    
    "Finalizada",
    "Cancelada",
    "Em construção",
    name="tipo_status_formacao",
    create_type=False
)

# ===============================
# CARGO
# ===============================

class Cargo(Base):

    __tablename__ = "cargo"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), unique=True, nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    servidores = relationship("Servidor", back_populates="cargo")


# ===============================
# SERVIDOR
# ===============================

class Servidor(Base):

    __tablename__ = "servidor"

    matricula = Column(String(20), primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    cargo_id = Column(Integer, ForeignKey("cargo.id"))
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    cargo = relationship("Cargo", back_populates="servidores", lazy="joined")
    participacoes = relationship("Participacao", back_populates="servidor")
    facilitacoes = relationship("Facilitador", back_populates="servidor")
    usuario = relationship("Usuario",back_populates="servidor",uselist=False)
    
# ===============================
# PLANO ANUAL
# ===============================

class PlanoAnual(Base):

    __tablename__ = "plano_anual"

    id = Column(Integer, primary_key=True, index=True)
    ano = Column(Integer, nullable=False, index=True)
    eixo = Column(tipo_eixo, nullable=False)
    objetivo = Column(Text)
    ementa = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    formacoes = relationship("Formacao", back_populates="plano")


# ===============================
# FORMAÇÃO
# ===============================

class Formacao(Base):

    __tablename__ = "formacao"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    data_inicio = Column(Date)
    data_termino = Column(Date, index=True)    
    carga_horaria = Column(Integer)
    modalidade = Column(tipo_modalidade)    
    publico_alvo = Column(String(300))
    investimento = Column(Numeric(12,2))
    meta_participantes = Column(Integer, nullable=False, default=0)
    status = Column(
        tipo_status_formacao,
        nullable=False,
        default="Planejada",
        index=True
    )
    plano_id = Column(Integer, ForeignKey("plano_anual.id"), index=True)
    plano = relationship("PlanoAnual", back_populates="formacoes")
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True, index=True)
    participacoes = relationship("Participacao", back_populates="formacao")
    facilitadores = relationship("Facilitador", back_populates="formacao")
    
    __table_args__ = (

        UniqueConstraint(
            "descricao",
            "plano_id",
            name="uq_formacao_plano"
        ),

        CheckConstraint(
            """
            data_termino IS NULL
            OR data_inicio IS NULL
            OR data_termino >= data_inicio
            """,
            name="ck_formacao_datas_validas"
        )
    )


# ===============================
# LOTAÇÃO
# ===============================

class Lotacao(Base):

    __tablename__ = "lotacao"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    tipo = Column(String(100), nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    participacoes = relationship("Participacao", back_populates="lotacao")


# ===============================
# PARTICIPAÇÃO
# ===============================

class Participacao(Base):

    __tablename__ = "participacao"

    id = Column(Integer, primary_key=True, index=True)

    matricula = Column(String(20), ForeignKey("servidor.matricula"), nullable=False)
    formacao_id = Column(Integer, ForeignKey("formacao.id"), nullable=False)
    lotacao_id = Column(Integer, ForeignKey("lotacao.id"), nullable=False)
    aproveitamento = Column(Float)
    criado_em = Column(DateTime, default=datetime.utcnow)
    servidor = relationship("Servidor", back_populates="participacoes", lazy="joined")
    formacao = relationship("Formacao", back_populates="participacoes", lazy="joined")
    lotacao = relationship("Lotacao", back_populates="participacoes", lazy="joined")
    __table_args__ = (
        UniqueConstraint(
            "matricula",
            "formacao_id",
            name="uq_participacao"
        ),
    )


# ===============================
# FACILITADOR
# ===============================
class Facilitador(Base):

    __tablename__ = "facilitador"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    matricula = Column(
        String(20),
        ForeignKey("servidor.matricula"),
        nullable=False
    )

    formacao_id = Column(
        Integer,
        ForeignKey("formacao.id"),
        nullable=False
    )

    criado_em = Column(
        DateTime,
        default=datetime.utcnow
    )

    servidor = relationship(
        "Servidor",
        back_populates="facilitacoes"
    )

    formacao = relationship(
        "Formacao",
        back_populates="facilitadores"
    )

    __table_args__ = (

        UniqueConstraint(
            "matricula",
            "formacao_id",
            name="uq_facilitador"
        ),

    )

    def __repr__(self):

        return (
            f"<Facilitador "
            f"{self.matricula} "
            f"-> "
            f"{self.formacao_id}>"
        )

# ===============================
# USUÁRIO
# ===============================

class Usuario(Base):

    __tablename__ = "usuario"

    __table_args__ = (
        UniqueConstraint(
            "matricula",
            name="uq_usuario_matricula"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    matricula = Column(String(20), ForeignKey("servidor.matricula"),unique=True,nullable=False,index=True)
    senha = Column(String(255), nullable=False)
    perfil = Column(String(50), nullable=False, default="custom")
    email = Column(String(255), unique=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime)

    # RELACIONAMENTO    
        servidor = relationship(
            "Servidor",
            back_populates="usuario"
        )
