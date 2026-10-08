
# Importamos los tipos de datos para nuestras columnas
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime

# Importamos las herramientas para definir columnas y relaciones
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importamos nuestra clase base
from backend.database.database import Base



# USUARIOS

# Modelo que representa a los usuarios de Twilight AI
class User(Base):

    # Nombre de la tabla en SQLite
    __tablename__ = "users"

    # Identificador único del usuario
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Nombre de usuario único
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # Correo electrónico único
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Contraseña protegida mediante hashing
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Indica si la cuenta está activa
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )

    # Relación con las conversaciones del usuario
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )



# CONVERSACIONES

# Modelo que representa una conversación
class Conversation(Base):

    # Nombre de la tabla en SQLite
    __tablename__ = "conversations"

    # Identificador único de la conversación
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Título de la conversación
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    # Identificador del usuario propietario
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Fecha en que se creó la conversación
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación con el usuario propietario
    user: Mapped["User"] = relationship(
        back_populates="conversations"
    )

    # Relación con los mensajes de la conversación
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan"
    )



# MENSAJES

# Modelo que representa un mensaje del chat
class Message(Base):

    # Nombre de la tabla en SQLite
    __tablename__ = "messages"

    # Identificador único del mensaje
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Identificador de la conversación
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )

    # Indica quién envió el mensaje
    # Puede ser "user" o "assistant"
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Contenido del mensaje
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    # Fecha en que se creó el mensaje
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relación con la conversación a la que pertenece
    conversation: Mapped["Conversation"] = relationship(
        back_populates="messages"
    )
