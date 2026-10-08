# Importamos herramientas para configurar variables de entorno
import os

# Importamos FastAPI y las herramientas para manejar errores
from fastapi import FastAPI, Depends, HTTPException

# Importamos CORS para permitir la comunicación con el frontend
from fastapi.middleware.cors import CORSMiddleware

# Importamos BaseModel para validar los datos recibidos
from pydantic import BaseModel, Field

# Importamos las herramientas para consultar la base de datos
from sqlalchemy import select
from sqlalchemy.orm import Session

# Importamos nuestro agente construido con LangGraph
from backend.agents.graph import ask_agent

# Importamos las rutas de autenticación
from backend.auth.router import router as auth_router

# Importamos la función para verificar al usuario autenticado
from backend.auth.dependencies import get_current_user

# Importamos nuestra conexión con la base de datos
from backend.database.database import get_db

# Importamos los modelos de usuarios, conversaciones y mensajes
from backend.database.models import User, Conversation, Message

# Importamos las rutas para administrar documentos
from backend.services.document_router import router as document_router


# ==========================================
# CONFIGURACIÓN DE FASTAPI
# ==========================================

# Creamos nuestra aplicación
app = FastAPI(
    title="Twilight AI",
    description="AI assistant specialized in the Twilight saga",
    version="1.0.0"
)

# Obtenemos los dominios autorizados desde las variables de entorno
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

# Permitimos solicitudes únicamente desde los dominios autorizados
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Registramos las rutas de autenticación
app.include_router(auth_router)

# Registramos las rutas para administrar documentos
app.include_router(document_router)


# ==========================================
# ESQUEMAS DEL CHAT
# ==========================================

# Definimos los datos que recibe nuestro chat
class ChatRequest(BaseModel):

    # Pregunta enviada por el usuario
    question: str = Field(min_length=1)

    # Identificador opcional de una conversación existente
    conversation_id: int | None = Field(
        default=None,
        ge=1
    )


# Definimos cómo devolveremos la respuesta
class ChatResponse(BaseModel):

    # Respuesta generada por nuestro agente
    answer: str

    # Identificador de la conversación
    conversation_id: int


# ==========================================
# ENDPOINT PRINCIPAL
# ==========================================

@app.get("/")
def home():

    # Devolvemos un mensaje para verificar que la API funciona
    return {
        "message": "Welcome to Twilight AI",
        "status": "Backend running successfully"
    }


# ==========================================
# CHAT CON MEMORIA CONVERSACIONAL
# ==========================================

@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Inicializamos el historial de la conversación
    chat_history = ""

    # Verificamos si el usuario quiere continuar una conversación
    if request.conversation_id is not None:

        # Buscamos la conversación y verificamos su propietario
        conversation = db.scalar(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )

        # Rechazamos conversaciones inexistentes o de otros usuarios
        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found."
            )

        # Consultamos los mensajes anteriores en orden
        previous_messages = db.scalars(
            select(Message)
            .where(
                Message.conversation_id == conversation.id
            )
            .order_by(Message.id.asc())
        ).all()

        # Preparamos el historial para nuestro agente
        history_lines = []

        for message in previous_messages:

            # Identificamos quién escribió el mensaje
            role = (
                "User"
                if message.role == "user"
                else "Assistant"
            )

            # Agregamos el mensaje al historial
            history_lines.append(
                f"{role}: {message.content}"
            )

        # Unimos los mensajes en un solo texto
        chat_history = "\n".join(history_lines)

    else:

        # Creamos una conversación nueva para el usuario
        conversation = Conversation(
            title=request.question[:200],
            user_id=current_user.id
        )

        # Agregamos la conversación a la sesión
        db.add(conversation)

    # ==========================================
    # GENERACIÓN DE RESPUESTA CON OLLAMA
    # ==========================================

    # Intentamos generar una respuesta utilizando nuestro agente RAG
    try:

        # El historial ayuda a interpretar preguntas de seguimiento
        answer = ask_agent(
            question=request.question,
            chat_history=chat_history
        )

    except Exception:

        # Descartamos cualquier cambio pendiente en la base de datos
        db.rollback()

        # Devolvemos un mensaje seguro sin exponer errores internos
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is temporarily unavailable. "
                "Please try again later."
            )
        )

    # ==========================================
    # GUARDAR CONVERSACIÓN Y MENSAJES
    # ==========================================

    # Obtenemos el identificador de la conversación
    db.flush()

    # Creamos el mensaje enviado por el usuario
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )

    # Creamos el mensaje generado por nuestro asistente
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    # Agregamos ambos mensajes a la base de datos
    db.add_all([
        user_message,
        assistant_message
    ])

    # Guardamos la conversación y sus mensajes
    db.commit()

    # Devolvemos la respuesta y el identificador del chat
    return ChatResponse(
        answer=answer,
        conversation_id=conversation.id
    )


# ==========================================
# CONSULTAR HISTORIAL DE CONVERSACIONES
# ==========================================

@app.get("/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Consultamos únicamente las conversaciones del usuario
    conversations = db.scalars(
        select(Conversation)
        .where(
            Conversation.user_id == current_user.id
        )
        .order_by(
            Conversation.created_at.desc()
        )
    ).all()

    # Preparamos el historial
    history = []

    for conversation in conversations:

        # Agregamos la información de cada conversación
        history.append({
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at
        })

    # Devolvemos las conversaciones del usuario
    return history


# ==========================================
# CONSULTAR MENSAJES DE UNA CONVERSACIÓN
# ==========================================

@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Buscamos la conversación y verificamos su propietario
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )

    # Rechazamos conversaciones inexistentes o de otros usuarios
    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    # Consultamos los mensajes de la conversación
    messages = db.scalars(
        select(Message)
        .where(
            Message.conversation_id == conversation.id
        )
        .order_by(
            Message.id.asc()
        )
    ).all()

    # Preparamos los mensajes para devolverlos
    message_history = []

    for message in messages:

        message_history.append({
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        })

    # Devolvemos la conversación con sus mensajes
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": message_history
    }
