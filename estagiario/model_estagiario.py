from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    Enum as SqlEnum
)

from sqlalchemy.orm import relationship

from database import Base

from estagiario.enums import (
    MotivoDesligamentoEnum,
    SexoEnum
)

from models import (
    Servidor,
    Lotacao
)

from estagiario.model_acompanhamento import (
    AvaliacaoSupervisor,
    FrequenciaEstagio,
    PagamentoEstagio
)


class Estagiario(Base):
    __tablename__ = "estagiarios"

    id = Column(Integer, primary_key=True)

    nome = Column(String(200), nullable=False)

    sexo = Column(
        SqlEnum(
            SexoEnum,
            native_enum=False
        ),
        nullable=False,
        default=SexoEnum.NAO_INFORMADO
    )

    cpf = Column(
        String(14),
        unique=True,
        nullable=False
    )

    data_nascimento = Column(Date)

    email = Column(String(200))

    telefone = Column(String(30))

    endereco = Column(Text)

    instituicao_ensino = Column(String(200))

    curso = Column(String(200))

    semestre = Column(String(20))

    ativo = Column(
        Boolean,
        default=True,
        nullable=False
    )

    observacoes = Column(Text)

    # Responsável
    nome_responsavel = Column(String(200))

    cpf_responsavel =  Column(
        String(14),        
        nullable=False
    )

    parentesco_responsavel = Column(String(50))

    telefone_responsavel = Column(String(30))

    email_responsavel = Column(String(200))

    contratos = relationship(
        "ContratoEstagio",
        back_populates="estagiario",
        cascade="all, delete-orphan"
    )

class ClassificacaoEstagio(Base):

    __tablename__ = "classificacoes_estagio"

    id = Column(
        Integer,
        primary_key=True
    )

    codigo = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True
    )

    descricao = Column(
        String(100),
        nullable=False
    )

    ativo = Column(
        Boolean,
        default=True,
        nullable=False
    )


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

    valor_hora = Column(
        Numeric(10, 2),
        nullable=False
    )

    data_inicio_vigencia = Column(
        Date,
        nullable=False
    )

    classificacao = relationship(
        "ClassificacaoEstagio",
        back_populates="valores"
    )

class BeneficioEstagiario(Base):
    __tablename__ = "beneficios_estagiario"

    id = Column(Integer, primary_key=True)

    valor_vale_alimentacao = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    valor_vale_transporte = Column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    data_inicio_vigencia = Column(
        Date,
        nullable=False,
        unique=True
    )    


class ContratoEstagio(Base):
    __tablename__ = "contratos_estagio"

    id = Column(Integer, primary_key=True)

    # Relacionamentos
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

    # Dados do contrato
    numero_contrato = Column(
        String(30),
        unique=True,
        nullable=False
    )

    data_assinatura = Column(
        Date,
        nullable=False
    )

    data_inicio = Column(
        Date,
        nullable=False
    )

    data_fim = Column(
        Date,
        nullable=False
    )

    carga_horaria_diaria = Column(
        Integer,
        nullable=False
    )

    horario = Column(
        String(100),
        nullable=False
    )
    
    # Benefícios
    vale_alimentacao = Column(
        Boolean,
        nullable=False,
        default=False
    )
    
    quantidade_vale_transporte = Column(
        Integer,
        nullable=False,
        default=0
    )


    # Encerramento
    data_desligamento = Column(Date)

    motivo_desligamento = Column(
        SqlEnum(
            MotivoDesligamentoEnum,
            native_enum=False
        )
    )

    observacao_desligamento = Column(Text)

    # Observações gerais
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

@router.post("/fechar")
def fechar_folha(
    competencia: date,
    request: Request,
    db: Session = Depends(get_db)
):

    usuario = request.session.get("user")

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuário não autenticado."
        )

    usuario_id = usuario.get("id")


    # =========================================
    # Define fim da competência
    # =========================================

    if competencia.month == 12:

        fim_competencia = date(
            competencia.year,
            12,
            31
        )

    else:

        fim_competencia = date(
            competencia.year,
            competencia.month + 1,
            1
        ) - timedelta(days=1)


    # =========================================
    # Busca frequências da competência
    # =========================================

    frequencias = (
        db.query(FrequenciaEstagio)
        .join(
            ContratoEstagio,
            FrequenciaEstagio.contrato_id ==
            ContratoEstagio.id
        )
        .filter(
            FrequenciaEstagio.competencia == competencia,
            ContratoEstagio.data_inicio <= fim_competencia,
            ContratoEstagio.data_fim >= competencia
        )
        .all()
    )


    if not frequencias:

        raise HTTPException(
            status_code=400,
            detail="Nenhuma frequência encontrada para esta competência."
        )


    # =========================================
    # Fecha a folha
    # =========================================

    for frequencia in frequencias:


        # -------------------------------
        # Evita fechar novamente
        # -------------------------------

        if frequencia.status == StatusFolhaEnum.FECHADA:

            raise HTTPException(
                status_code=400,
                detail=f"A frequência {frequencia.id} já está fechada."
            )


        # -------------------------------
        # Verifica se já existe pagamento
        # -------------------------------

        pagamento_existente = (
            db.query(PagamentoEstagio)
            .filter(
                PagamentoEstagio.frequencia_id ==
                frequencia.id
            )
            .first()
        )


        if pagamento_existente:

            raise HTTPException(
                status_code=400,
                detail="Já existe pagamento para esta frequência."
            )


        # =================================
        # Cálculo dos valores
        # =================================

        contrato = frequencia.contrato


        # Exemplo temporário
        valor_hora = 10.00

        vale_alimentacao = (
            0
            if not contrato.vale_alimentacao
            else 100
        )

        vale_transporte = (
            contrato.quantidade_vale_transporte * 5
        )


        valor_total = (
            float(frequencia.horas_realizadas)
            * valor_hora
            +
            vale_alimentacao
            +
            vale_transporte
        )


        # =================================
        # Cria pagamento
        # =================================

        pagamento = PagamentoEstagio(

            frequencia_id=frequencia.id,

            usuario_fechamento_id=usuario_id,

            data_fechamento=date.today(),

            valor_hora_aplicado=valor_hora,

            valor_vale_alimentacao=vale_alimentacao,

            valor_vale_transporte=vale_transporte,

            valor_total=valor_total

        )


        db.add(pagamento)


        # =================================
        # Fecha frequência
        # =================================

        frequencia.status = StatusFolhaEnum.FECHADA



    db.commit()


    return {

        "mensagem":
            "Folha fechada com sucesso.",

        "competencia":
            competencia.strftime("%m/%Y"),

        "quantidade":
            len(frequencias)

    }

    
