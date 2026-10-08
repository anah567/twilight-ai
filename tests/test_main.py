
# Importamos TestClient para probar FastAPI sin abrir el navegador
from fastapi.testclient import TestClient

# Importamos nuestra aplicación
from backend.main import app


# Creamos un cliente para enviar solicitudes de prueba
client = TestClient(app)


# Comprobamos que la página principal responda correctamente
def test_home():

    # Enviamos una solicitud GET a la ruta principal
    response = client.get("/")

    # Verificamos que el servidor responda con código 200
    assert response.status_code == 200

    # Verificamos que la respuesta tenga el mensaje esperado
    assert response.json()["message"] == "Welcome to Twilight AI"

    # Verificamos que el backend indique que está funcionando
    assert response.json()["status"] == "Backend running successfully"
