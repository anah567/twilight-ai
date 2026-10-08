
# Importamos herramientas para trabajar con fechas
from datetime import datetime, timedelta, timezone

# Importamos herramientas para leer variables de entorno
import os
from dotenv import load_dotenv

# Importamos JWT para crear y verificar tokens
import jwt

# Importamos Argon2 para proteger contraseñas
from pwdlib import PasswordHash


# Cargamos las variables del archivo .env
load_dotenv()

# Obtenemos la clave secreta de nuestras variables de entorno
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Verificamos que exista una clave secreta configurada
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not configured.")

# Definimos el algoritmo de firma
ALGORITHM = "HS256"

# Tiempo de duración de los tokens en minutos
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuramos el sistema de hashing de contraseñas
password_hash = PasswordHash.recommended()


# Función para proteger una contraseña
def hash_password(password: str) -> str:

    # Convertimos la contraseña en un hash seguro
    return password_hash.hash(password)


# Función para verificar una contraseña
def verify_password(password: str, hashed_password: str) -> bool:

    # Comparamos la contraseña ingresada con el hash almacenado
    return password_hash.verify(password, hashed_password)


# Función para generar un token JWT
def create_access_token(user_id: int) -> str:

    # Calculamos cuándo vencerá el token
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Creamos los datos que guardará el token
    payload = {
        "sub": str(user_id),
        "exp": expiration
    }

    # Firmamos el token con nuestra clave secreta
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # Devolvemos el token generado
    return token


# Función para verificar y decodificar un token
def decode_access_token(token: str) -> dict | None:

    try:
        # Verificamos la firma y la fecha de vencimiento
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]}
        )

        # Devolvemos la información del token válido
        return payload

    except jwt.InvalidTokenError:

        # Si el token no es válido, devolvemos None
        return None
