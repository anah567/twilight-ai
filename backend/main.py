
# Importamos FastAPI y sus herramientas de dependencias
from fastapi import FastAPI, Depends

# Importamos BaseModel para validar los datos recibidos
from pydantic import BaseModel, Field

# Importamos nuestro agente construido con LangGraph
from backend.agents.graph import ask_agent

# Importamos las rutas de autenticación
from backend.auth.router import router as auth_router

# Importamos la función para verificar al usuario autenticado
from backend.auth.dependencies import get_current_user

# Importamos el modelo de usuario
from backend.database.models import User


# Creamos nuestra aplicación
app = FastAPI(
    title="Twilight AI",
    description="AI assistant specialized in the Twilight saga",
    version="1.0.0"
)


# Registramos las rutas de autenticación
app.include_router(auth_router)


# Definimos cómo debe llegar una pregunta
class ChatRequest(BaseModel):

    # La pregunta debe contener al menos un carácter
    question: str = Field(min_length=1)


# Definimos cómo devolveremos la respuesta
class ChatResponse(BaseModel):

    # Respuesta generada por nuestro agente
    answer: str


# Endpoint principal de nuestra API
@app.get("/")
def home():

    return {
        "message": "Welcome to Twilight AI",
        "status": "Backend running successfully"
    }


# Endpoint protegido para conversar con nuestro agente
@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    # Solo llegamos aquí si el usuario está autenticado
    answer = ask_agent(request.question)

    # Devolvemos la respuesta generada por el agente
    return ChatResponse(answer=answer)
