# Importamos FastAPI para crear nuestra API
from fastapi import FastAPI

# Creamos la aplicación
app = FastAPI(
    title="Twilight AI",
    description="Agente inteligente sobre la saga Crepúsculo",
    version="1.0.0"
)

# Endpoint principal para verificar que la API funciona
@app.get("/")
def home():
    return {
        "mensaje": "Bienvenido a Twilight AI",
        "estado": "Backend funcionando correctamente"
    }