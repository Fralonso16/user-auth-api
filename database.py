# Importamos las herramientas de SQLAlchemy que necesitamos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexión: SQLite, guardado en un archivo llamado users.db
# en esta misma carpeta (se crea solo, no hace falta crearlo a mano)
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"

# Creamos el "motor" que conecta la aplicación con la base de datos
# connect_args es una configuración especial que necesita SQLite para
# funcionar bien junto con FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal es una "fábrica" de sesiones: cada vez que la API necesite
# leer o guardar datos, abrirá una sesión nueva usando esto
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase de la que heredarán nuestros modelos (las tablas)
Base = declarative_base()