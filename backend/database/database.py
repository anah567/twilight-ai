
# Importamos las herramientas necesarias de SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Definimos la ubicación de nuestra base de datos SQLite
DATABASE_URL = "sqlite:///./twilight.db"


# Creamos el motor que conecta Python con SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Configuramos las sesiones para consultar y modificar datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Clase base de la que heredarán nuestras tablas
class Base(DeclarativeBase):
    pass


# Función para obtener una sesión de base de datos
def get_db():

    # Creamos una nueva sesión
    db = SessionLocal()

    try:
        # Entregamos la sesión al endpoint que la necesite
        yield db

    finally:
        # Cerramos la sesión para liberar recursos
        db.close()
