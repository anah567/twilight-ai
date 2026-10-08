
# Importamos pytest para crear configuraciones reutilizables
import pytest

# Importamos herramientas para crear una base de datos temporal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importamos nuestro backend y sus modelos
from backend.main import app
from backend.database.database import Base, get_db
from backend.database import models

# Importamos TestClient para probar las rutas de FastAPI
from fastapi.testclient import TestClient


# Creamos un cliente de prueba con una base de datos independiente
@pytest.fixture
def client():

    # Creamos una base SQLite temporal en memoria
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Creamos las tablas de usuarios, conversaciones y mensajes
    Base.metadata.create_all(bind=test_engine)

    # Configuramos sesiones para la base de datos temporal
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    # Reemplazamos la conexión real por la conexión de prueba
    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    # Aplicamos la conexión temporal a FastAPI
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Entregamos el cliente a las pruebas
        with TestClient(app) as test_client:
            yield test_client

    finally:
        # Restauramos las dependencias originales
        app.dependency_overrides.pop(get_db, None)

        # Eliminamos las tablas temporales
        Base.metadata.drop_all(bind=test_engine)

        # Cerramos la conexión temporal
        test_engine.dispose()
