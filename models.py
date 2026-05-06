"""Modelos de dados para DB Formações"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import ENUM


class Servidor(Base):
    """
    Modelo de Servidor
    
    Attributes:
        matricula: Matrícula do servidor (chave primária)
        nome: Nome do servidor
        data_registro: Data de registro
        cargo_id: FK para Cargo
    """
    __tablename__ = "servidor"
    
    matricula = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    data_registro = Column(Date)
    cargo_id = Column(Integer, ForeignKey("cargo.id"), nullable=True)
    
    # Relacionamentos
    cargo = relationship("Cargo", lazy="joined")
    participacoes = relationship(
        "Participacao",
        back_populates="servidor",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Servidor(matricula={self.matricula}, nome={self.nome})>"


class Usuario(Base):
    """
    Modelo de Usuário para autenticação
    
    Attributes:
        id: ID do usuário
        username: Nome de usuário único
        senha: Senha criptografada
        perfil: Perfil de acesso (admin, operador, custom)
    """
    __tablename__ = "usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    senha = Column(String, nullable=False)
    perfil = Column(String, nullable=False, index=True)
    
    __table_args__ = (
        Index("ix_usuario_username_perfil", "username", "perfil"),
    )
    
    def __repr__(self):
        return f"<Usuario(username={self.username}, perfil={self.perfil})>"


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


class Formacao(Base):
    """
    Modelo de Formação/Curso
    
    Attributes:
        id: ID da formação
        descricao: Descrição do curso
        data_termino: Data de término
        carga_horaria: Carga horária em horas
        modalidade: Modalidade (presencial, online, hibrido)
        eixo: Eixo de formação
    """
    __tablename__ = "formacao"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=True, index=True)
    data_termino = Column(Date, nullable=True, index=True)
    carga_horaria = Column(Integer, nullable=True)
    modalidade = Column(tipo_modalidade, nullable=True)
    eixo = Column(tipo_eixo, nullable=True)
    
    # Relacionamentos
    participacoes = relationship(
        "Participacao",
        back_populates="formacao",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        UniqueConstraint('descricao', 'data_termino', name='uq_formacao'),
        Index("ix_formacao_data_termino", "data_termino"),
    )
    
    def __repr__(self):
        return f"<Formacao(id={self.id}, descricao={self.descricao})>"


class Lotacao(Base):
    """
    Modelo de Lotação
    
    Attributes:
        id: ID da lotação
        descricao: Descrição
        tipo: Tipo de lotação
    """
    __tablename__ = "lotacao"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False, index=True)
    tipo = Column(String, nullable=False, index=True)
    
    # Relacionamentos
    participacoes = relationship(
        "Participacao",
        back_populates="lotacao",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_lotacao_tipo", "tipo"),
    )
    
    def __repr__(self):
        return f"<Lotacao(id={self.id}, tipo={self.tipo})>"


class Cargo(Base):
    """
    Modelo de Cargo
    
    Attributes:
        id: ID do cargo
        descricao: Descrição do cargo
    """
    __tablename__ = "cargo"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, unique=True, nullable=False, index=True)
    
    # Relacionamentos
    servidores = relationship("Servidor", back_populates="cargo")
    
    def __repr__(self):
        return f"<Cargo(id={self.id}, descricao={self.descricao})>"


class Participacao(Base):
    """
    Modelo de Participação em Formação
    
    Attributes:
        id: ID da participação
        matricula: FK para Servidor
        formacao_id: FK para Formacao
        lotacao_id: FK para Lotacao
        aproveitamento: Aproveitamento (aprovado, reprovado, etc)
    """
    __tablename__ = "participacao"
    
    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String, ForeignKey("servidor.matricula"), nullable=True, index=True)
    formacao_id = Column(Integer, ForeignKey("formacao.id"), nullable=True, index=True)
    lotacao_id = Column(Integer, ForeignKey("lotacao.id"), nullable=True, index=True)
    aproveitamento = Column(String, nullable=True, index=True)
    
    # Relacionamentos
    servidor = relationship("Servidor", back_populates="participacoes", lazy="joined")
    formacao = relationship("Formacao", back_populates="participacoes", lazy="joined")
    lotacao = relationship("Lotacao", back_populates="participacoes", lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('matricula', 'formacao_id', name='uq_participacao'),
        Index("ix_participacao_aproveitamento", "aproveitamento"),
    )
    
    def __repr__(self):
        return f"<Participacao(matricula={self.matricula}, formacao_id={self.formacao_id})>"
