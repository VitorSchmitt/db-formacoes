from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import ENUM

class Servidor(Base):
    __tablename__ = "servidor"

    matricula = Column(String, primary_key=True)
    nome = Column(String)
    cargo = Column(String)
    data_registro = Column(Date)
tipo_modalidade = ENUM(
    "presencial", "online", "hibrido",
    name="tipo_modalidade",
    create_type=False  # importante: já existe no banco
)

tipo_eixo = ENUM(
    "Ambientação Institucional/Formação Inicial", "Gestão do Trabalho/Saúde Mental e Bem Estar", "Qualificação da Prática Socioeducativa Temas Transversais",
    name="tipo_eixo",
    create_type=False
)

class Formacao(Base):
    __tablename__ = "formacao"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=True)
    data_termino = Column(Date, nullable=True)
    carga_horaria = Column(Integer, nullable=True)
    modalidade = Column(tipo_modalidade, nullable=True)
    eixo = Column(tipo_eixo, nullable=True)
    __table_args__ = (
        UniqueConstraint('descricao', 'data_termino', name='uq_formacao'),
    )

class Lotacao(Base):
    __tablename__ = "lotacao"
    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    tipo = Column(String)
    
class Participacao(Base):
    __tablename__ = "participacao"
    id = Column(Integer, primary_key=True, index=True)
    matricula = Column(String, ForeignKey("servidor.matricula"), nullable=True)
    formacao_id = Column(Integer, ForeignKey("formacao.id"), nullable=True)
    lotacao_id = Column(Integer, ForeignKey("lotacao.id"), nullable=True)
    aproveitamento = Column(String)
    servidor = relationship("Servidor", lazy="joined")
    formacao = relationship("Formacao", lazy="joined")
    lotacao = relationship("Lotacao", lazy="joined")
