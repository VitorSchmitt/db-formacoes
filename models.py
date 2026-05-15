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
    "presencial", "online", "hibrido",
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
    "Em andamento",
    "Finalizada",
    "Cancelada",
    "Em construção",
    name="tipo_status_formacao"
)

status = Column(
    tipo_status_formacao,
    nullable=False,
    default="Planejada"
)

# ===============================
# MODELS
# ===============================

class Cargo(Base):
    """
    Modelo de Cargo
    
    Representa os cargos disponíveis para servidores
    """
    __tablename__ = "cargo"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), unique=True, nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    servidores = relationship("Servidor", back_populates="cargo")
    
    def __repr__(self):
        return f"<Cargo {self.id}: {self.descricao}>"


class Servidor(Base):
    """
    Modelo de Servidor (Funcionário)
    
    Representa os servidores públicos do município
    """
    __tablename__ = "servidor"
    
    matricula = Column(String(20), primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)    
    cargo_id = Column(Integer, ForeignKey("cargo.id"), nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    # Relationships
    cargo = relationship("Cargo", back_populates="servidores", lazy="joined")
    participacoes = relationship("Participacao", back_populates="servidor")
    
    
    def __repr__(self):
        return f"<Servidor {self.matricula}: {self.nome}>"

class Formacao(Base):

    __tablename__ = "formacao"

    # =====================================
    # IDENTIFICAÇÃO
    # =====================================

    id = Column(Integer, primary_key=True, index=True)

    descricao = Column(String(255), nullable=False, index=True)

    # =====================================
    # DATAS
    # =====================================

    data_inicio = Column(Date, nullable=True)

    data_termino = Column(Date, nullable=True, index=True)

    periodo = Column(String(100), nullable=True)

    ano_planejamento = Column(Integer, nullable=True, index=True)

    # =====================================
    # DADOS DA FORMAÇÃO
    # =====================================

    carga_horaria = Column(Integer, nullable=True)

    modalidade = Column(tipo_modalidade, nullable=True)

    eixo = Column(tipo_eixo, nullable=True)

    publico_alvo = Column(String(300), nullable=True)

    investimento = Column(Numeric(12, 2), nullable=True)

    # =====================================
    # METAS
    # =====================================

    meta_participantes = Column(Integer, nullable=False, default=0)

    # =====================================
    # STATUS OPERACIONAL
    # =====================================

    status = Column(tipo_status_formacao, nullable=False, default="Planejada", index=True)

    # =====================================
    # PLANO ANUAL
    # =====================================

    plano_id = Column(Integer, ForeignKey("plano_anual.id"), nullable=True, index=True)

    plano = relationship("PlanoAnual", back_populates="formacoes")

    # =====================================
    # SISTEMA
    # =====================================

    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    ativo = Column(Boolean, nullable=False, default=True, index=True)

    # =====================================
    # RELACIONAMENTOS
    # =====================================

    participacoes = relationship(
        "Participacao",
        back_populates="formacao"
    )

    # =====================================
    # CONSTRAINTS
    # =====================================

    __table_args__ = (

        UniqueConstraint(
            "descricao",
            "data_termino",
            name="uq_formacao_ano"
        ),

        CheckConstraint(
            """
            data_termino IS NULL
            OR data_inicio IS NULL
            OR data_termino >= data_inicio
            """,
            name="ck_formacao_datas_validas"
        ),
    )

    # =====================================
    # REPRESENTAÇÃO
    # =====================================

    def __repr__(self):
        return f"<Formacao(id={self.id}, descricao='{self.descricao}', status='{self.status}')>"


class Lotacao(Base):
    """
    Modelo de Lotação (Departamento/Setor)
    
    Representa os setores/departamentos da fase
    """
    __tablename__ = "lotacao"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    tipo = Column(String(100), nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relationships
    participacoes = relationship("Participacao", back_populates="lotacao")
    
    def __repr__(self):
        return f"<Lotacao {self.id}: {self.descricao} ({self.tipo})>"


class Participacao(Base):
    """
    Modelo de Participação
    
    Representa a participação de servidores em formações
    """
    __tablename__ = "participacao"
    
    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(20), ForeignKey("servidor.matricula"), nullable=False)
    formacao_id = Column(Integer, ForeignKey("formacao.id"), nullable=False)
    lotacao_id = Column(Integer, ForeignKey("lotacao.id"), nullable=False)
    aproveitamento = Column(Float, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)    
    
    # Relationships
    servidor = relationship("Servidor", back_populates="participacoes", lazy="joined")
    formacao = relationship("Formacao", back_populates="participacoes", lazy="joined")
    lotacao = relationship("Lotacao", back_populates="participacoes", lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('matricula', 'formacao_id', name='uq_participacao'),
    )
    
    def __repr__(self):
        return f"<Participacao {self.id}: {self.matricula} -> {self.formacao_id}>"


class Usuario(Base):
    """
    Modelo de Usuário (Acesso ao Sistema)
    
    Representa os usuários que acessam o sistema web
    """
    __tablename__ = "usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)
    perfil = Column(String(50), nullable=False, default="custom")  # admin, operador, custom
    email = Column(String(255), unique=True, nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)    
    ultimo_login = Column(DateTime, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('username', name='usuario_username_key'),
        UniqueConstraint('email', name='usuario_email_key'),
    )
    
    def __repr__(self):
        return f"<Usuario {self.id}: {self.username} ({self.perfil})>"

class PlanoAnual(Base):

    __tablename__ = "plano_anual"

    id = Column(Integer,primary_key=True,index=True)
    ano = Column(Integer,nullable=False,index=True)
    eixo = Column(tipo_eixo,nullable=False)
    objetivo = Column(Text,nullable=True)
    ementa = Column(Text,nullable=True)
    criado_em = Column(DateTime,default=datetime.utcnow)
    ativo = Column(Boolean,default=True)
    formacoes = relationship("Formacao",back_populates="plano")
