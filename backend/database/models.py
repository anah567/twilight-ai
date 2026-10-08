
# Importamos los tipos de datos para las columnas
from sqlalchemy import String, Integer

# Importamos las herramientas para definir las columnas
from sqlalchemy.orm import Mapped, mapped_column

# Importamos nuestra clase base de la base de datos
from backend.database.database import Base


# Modelo que representa a los usuarios de Twilight AI
class User(Base):

    # Nombre de la tabla dentro de SQLite
    __tablename__ = "users"

    # Identificador único de cada usuario
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # Nombre de usuario, obligatorio y único
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # Correo electrónico, obligatorio y único
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
