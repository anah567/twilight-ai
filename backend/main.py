
# Importamos FastAPI para crear nuestra API
from fastapi import FastAPI

# Importamos BaseModel para validar los datos recibidos
from pydantic import BaseModel, Field

# Importamos nuestro agente construido con LangGraph
from backend.agents.graph import ask_agent


# Creamos nuestra aplicación
app = FastAPI(
    title="Twilight AI",
    description="AI assistant specialized in the Twilight saga",
    version="1.0.0"
)


# Definimos cómo debe llegar una pregunta
class ChatRequest(BaseModel):

    # La pregunta debe contener al menos un carácter
    question: str = Field(min_length=1)


# Definimos cómo devolveremos la respuesta
class ChatResponse(BaseModel):

    # Respuesta generada por nuestro agente
    answer: str


# Endpoint principal para verificar el funcionamiento
@app.get("/")
def home():
    return {
        "message": "Welcome to Twilight AI",
        "status": "Backend running successfully"
    }


# Endpoint para enviar preguntas al agente
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # Enviamos la pregunta al agente RAG
    answer = ask_agent(request.question)

    # Devolvemos la respuesta en formato JSON
    return ChatResponse(answer=answer)
