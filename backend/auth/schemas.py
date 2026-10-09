
# Importamos herramientas para validar los datos de entrada
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Datos necesarios para registrar un usuario
class UserRegister(BaseModel):

    # Nombre de usuario
    username: str = Field(min_length=3, max_length=50)

    # Correo electrónico válido
    email: EmailStr

    # Contraseña con una longitud mínima
    password: str = Field(min_length=8, max_length=128)


# Datos que podemos devolver públicamente
class UserResponse(BaseModel):

    # Identificador del usuario
    id: int

    # Nombre del usuario
    username: str

    # Correo electrónico
    email: EmailStr

    # Indica si la cuenta está activa
    is_active: bool

    # Indica si el usuario tiene permisos de administrador
    is_admin: bool

    # Permite convertir modelos de SQLAlchemy en respuestas
    model_config = ConfigDict(from_attributes=True)


# Datos necesarios para iniciar sesión
class UserLogin(BaseModel):

    # Correo electrónico del usuario
    email: EmailStr

    # Contraseña ingresada
    password: str


# Respuesta que contiene el token de acceso
class TokenResponse(BaseModel):

    # Token JWT generado después del inicio de sesión
    access_token: str

    # Tipo de autenticación utilizado
    token_type: str = "bearer"
