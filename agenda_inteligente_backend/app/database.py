from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Creación del motor de persistencia relacional
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Generador de sesiones transaccionales
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán nuestros modelos ORM
Base = declarative_base()

# Dependencia para inyectar la sesión en las rutas API de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()