
# Importamos herramientas para crear rutas y manejar errores
from fastapi import APIRouter, Depends, HTTPException, status

# Importamos la sesión de SQLAlchemy
from sqlalchemy.orm import Session

# Importamos select para consultar la base de datos
from sqlalchemy import select

# Importamos nuestra conexión y el modelo de usuario
from backend.database.database import get_db
from backend.database.models import User

# Importamos los esquemas de autenticación
from backend.auth.schemas import (
    UserRegister,
    UserResponse,
    UserLogin,
    TokenResponse
)

# Importamos las funciones de seguridad
from backend.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

from backend.auth.dependencies import get_current_user


# Creamos las rutas de autenticación
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# REGISTRO DE USUARIOS
# ==========================================

# Endpoint para registrar usuarios
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    request: UserRegister,
    db: Session = Depends(get_db)
):

    # Verificamos si el nombre de usuario ya existe
    existing_username = db.scalar(
        select(User).where(User.username == request.username)
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already registered."
        )

    # Verificamos si el correo electrónico ya está registrado
    existing_email = db.scalar(
        select(User).where(User.email == request.email)
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered."
        )

    # Creamos el usuario con su contraseña protegida
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password)
    )

    # Guardamos el usuario en la base de datos
    db.add(new_user)
    db.commit()

    # Actualizamos el objeto con su identificador generado
    db.refresh(new_user)

    # Devolvemos los datos públicos del usuario
    return new_user


# ==========================================
# INICIO DE SESIÓN
# ==========================================

# Endpoint para iniciar sesión
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login_user(
    request: UserLogin,
    db: Session = Depends(get_db)
):

    # Buscamos al usuario mediante su correo electrónico
    user = db.scalar(
        select(User).where(User.email == request.email)
    )

    # Verificamos que el usuario exista
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Verificamos que la contraseña sea correcta
    if not verify_password(
        request.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Verificamos que la cuenta esté activa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    # Generamos un token JWT asociado al usuario
    access_token = create_access_token(user.id)

    # Devolvemos el token para futuras solicitudes
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

# ==========================================
# PERFIL DEL USUARIO AUTENTICADO
# ==========================================

# Devolvemos los datos del usuario que inició sesión
@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user