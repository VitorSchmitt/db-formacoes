import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ===============================
# DATABASE CONNECTION
# ===============================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.pvmlhnqrnhciuqyzwnuj:fcsllessVEooGkbu@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
)

# 🔐 Engine com configurações seguras
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,      # Evita conexão morta
    pool_recycle=3600,       # Recicla conexões a cada 1 hora (Supabase)
    echo=os.getenv("DB_ECHO", "false").lower() == "true"  # Debug
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ===============================
# DEPENDENCY INJECTION
# ===============================
def get_db():
    """
    Dependency para injetar session do banco em endpoints FastAPI
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(Usuario).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===============================
# DATABASE INITIALIZATION
# ===============================
def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas
    
    Usage:
        python -c "from database import init_db; init_db()"
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {str(e)}")
        raise


def check_database_connection() -> bool:
    """
    Verifica se a conexão com o banco está funcionando
    
    Returns:
        bool: True se conectado, False caso contrário
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception:
        return False
