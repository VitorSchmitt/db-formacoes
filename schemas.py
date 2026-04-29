from pydantic import BaseModel
from datetime import date
from typing import Optional

class FormacaoBase(BaseModel):
    descricao: str
    data_termino: date
    carga_horaria: int
    modalidade: str
    eixo: str

class FormacaoCreate(FormacaoBase):
    pass

class FormacaoUpdate(BaseModel):
    descricao: Optional[str]
    data_termino: Optional[date]
    carga_horaria: Optional[int]
    modalidade: Optional[str]
    eixo: Optional[str]
# ===============================
# SERVIDOR
# ===============================
class ServidorCreate(BaseModel):
    matricula: str
    nome: str
    cargo_id: int

class ServidorUpdate(BaseModel):
    nome: str
    cargo_id: int
