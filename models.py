from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Servidor(Base):
    __tablename__ = "servidor"

    matricula = Column(String, primary_key=True)
    nome = Column(String)
    cargo = Column(String)
    data_registro = Column(Date)
class Formacao(Base):
    __tablename__ = "formacao"

    id = Column(Integer, primary_key=True)
    descricao = Column(String)    
    data_termino = Column(Date)
    tipo = Column(String)
    classificacao = Column(String)
    carga_horaria = Column(Integer)


class Lotacao(Base):
    __tablename__ = "lotacao"

    id = Column(Integer, primary_key=True)
    descricao = Column(String)
    tipo = Column(String)


class Participacao(Base):
    __tablename__ = "participacao"

    id = Column(Integer, primary_key=True)

    matricula = Column(String, ForeignKey("servidor.matricula"))
    formacao_id = Column(Integer, ForeignKey("formacao.id"))
    lotacao_id = Column(Integer, ForeignKey("lotacao.id"))

    aproveitamento = Column(String)

    servidor = relationship("Servidor")
    formacao = relationship("Formacao")
    lotacao = relationship("Lotacao")
