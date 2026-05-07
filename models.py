from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint, DateTime, Boolean
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
    create_type=False  # ⚠️ Importante: já existe no banco
)

tipo_eixo = ENUM(
    "Ambientação Institucional/Formação Inicial",
    "Gestão do Trabalho/Saúde Mental e Bem Estar",
    "Qualificação da Prática Socioeducativa Temas Transversais",
    name="tipo_eixo",
    create_type=False  # ⚠️ Importante: já existe no banco
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
    
    # Relationships
    cargo = relationship("Cargo", back_populates="servidores", lazy="joined")
    participacoes = relationship("Participacao", back_populates="servidor")
    
    __table_args__ = (
        UniqueConstraint('matricula', name='uq_servidor_matricula'),
    )
    
    def __repr__(self):
        return f"<Servidor {self.matricula}: {self.nome}>"


class Formacao(Base):
    """
    Modelo de Formação (Curso/Treinamento)
    
    Representa as formações oferecidas pela prefeitura
    """
    __tablename__ = "formacao"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(500), nullable=False, index=True)
    data_termino = Column(Date, nullable=True, index=True)
    carga_horaria = Column(Integer, nullable=True)
    modalidade = Column(tipo_modalidade, nullable=True)
    eixo = Column(tipo_eixo, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relationships
    participacoes = relationship("Participacao", back_populates="formacao")
    
    __table_args__ = (
        UniqueConstraint('descricao', 'data_termino', name='uq_formacao_descricao_data'),
    )
    
    def __repr__(self):
        return f"<Formacao {self.id}: {self.descricao}>"


class Lotacao(Base):
    """
    Modelo de Lotação (Departamento/Setor)
    
    Representa os setores/departamentos da prefeitura
    """
    __tablename__ = "lotacao"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False, index=True)
    tipo = Column(String(100), nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relationships
    participacoes = relationship("Participacao", back_populates="lotacao")
    
    __table_args__ = (
        UniqueConstraint('descricao', 'tipo', name='uq_lotacao_descricao_tipo'),
    )
    
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
    aproveitamento = Column(String(50), nullable=True)  # Ex: "Aprovado", "Reprovado", etc
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    servidor = relationship("Servidor", back_populates="participacoes", lazy="joined")
    formacao = relationship("Formacao", back_populates="participacoes", lazy="joined")
    lotacao = relationship("Lotacao", back_populates="participacoes", lazy="joined")
    
    __table_args__ = (
        UniqueConstraint('matricula', 'formacao_id', name='uq_participacao_matricula_formacao'),
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
        UniqueConstraint('username', name='uq_usuario_username'),
        UniqueConstraint('email', name='uq_usuario_email'),
    )
    
    def __repr__(self):
        return f"<Usuario {self.id}: {self.username} ({self.perfil})>"
