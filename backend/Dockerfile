
# Utilizamos Python 3.13 como base
FROM python:3.13-slim

# Definimos la carpeta principal del proyecto
WORKDIR /app

# Instalamos uv para manejar las dependencias
RUN pip install --no-cache-dir uv

# Copiamos los archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalamos las dependencias del proyecto
RUN uv sync --frozen --no-dev

# Copiamos el código del backend
COPY backend/ ./backend/

# Indicamos el puerto que utilizará FastAPI
EXPOSE 8000

# Iniciamos el servidor para aceptar conexiones externas
CMD ["uv", "run", "--no-sync", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
