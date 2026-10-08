
# Importamos las herramientas de autenticación de FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Importamos las herramientas para consultar la base de datos
from sqlalchemy.orm import Session
from sqlalchemy import select

# Importamos nuestra conexión y el modelo de usuario
from backend.database.database import get_db
from backend.database.models import User

# Importamos la función que verifica los tokens JWT
from backend.auth.security import decode_access_token


# Configuramos la autenticación mediante tokens Bearer
bearer_scheme = HTTPBearer()


# Función para obtener el usuario autenticado
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:

    # Extraemos el token enviado por el usuario
    token = credentials.credentials

    # Verificamos y decodificamos el token
    payload = decode_access_token(token)

    # Rechazamos los tokens inválidos o vencidos
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Obtenemos el identificador del usuario
    user_id = payload.get("sub")

    # Verificamos que el identificador sea válido
    if not isinstance(user_id, str) or not user_id.isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Buscamos al usuario en nuestra base de datos
    user = db.scalar(
        select(User).where(User.id == int(user_id))
    )

    # Verificamos que el usuario exista y esté activo
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Devolvemos el usuario autenticado
    return user
