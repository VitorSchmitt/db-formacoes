from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔴 IMPORTANTE: usar pooler (IPv4)
DATABASE_URL = "postgresql://postgres.pvmlhnqrnhciuqyzwnuj:fcsllessVEooGkbu@aws-1-us-west-2.pooler.supabase.com:6543/postgres"

# 🔐 SSL obrigatório no Supabase
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True  # evita conexão morta (bom no Render)
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# 📌 Dependency do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
