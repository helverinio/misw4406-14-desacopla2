"""
Configuración de base de datos para el módulo de sagas usando SQLAlchemy puro (FastAPI compatible)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# ✅ Base declarativa para nuestras tablas de saga
SagaBase = declarative_base()

# ✅ Configuración de conexión desde variables de entorno
DATABASE_URL = os.getenv(
    'DATABASE_URL_SYNC',
    f"postgresql://{os.getenv('POSTGRES_USER', 'postgres_user')}:"
    f"{os.getenv('POSTGRES_PASSWORD', '1234')}@"
    f"{os.getenv('POSTGRES_HOST', 'gestion-alianzas-db')}:"
    f"{os.getenv('POSTGRES_PORT', '5432')}/"
    f"{os.getenv('POSTGRES_DB', 'gestion_alianzas')}"
)

# ✅ Motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug SQL
    pool_pre_ping=True,
    pool_recycle=300
)

# ✅ Factory de sesiones
SagaSessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

def get_saga_session():
    """Obtiene una nueva sesión de base de datos para saga."""
    return SagaSessionFactory()

def create_saga_tables():
    """Crea todas las tablas de saga si no existen."""
    try:
        SagaBase.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Error creating saga tables: {e}")
        return False

def init_saga_db():
    """Inicializa la base de datos de saga."""
    return create_saga_tables()