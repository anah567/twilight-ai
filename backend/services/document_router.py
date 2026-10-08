
# Importamos herramientas para trabajar con archivos y rutas
from pathlib import Path
from uuid import uuid4

# Importamos herramientas de FastAPI
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

# Importamos herramientas para procesar documentos
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importamos la base vectorial de Twilight AI
from backend.vectorstore.vectorstore import get_vectorstore

# Importamos el modelo de usuario y la autenticación
from backend.database.models import User
from backend.auth.dependencies import get_current_user


# Creamos las rutas de documentos
router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# Definimos la carpeta donde guardaremos los archivos
UPLOAD_DIRECTORY = Path("documents/uploads")

# Definimos el tamaño máximo permitido: 1 MB
MAX_FILE_SIZE = 1024 * 1024


# Endpoint protegido para cargar documentos
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    # Verificamos que el archivo tenga un nombre
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required."
        )

    # Aceptamos únicamente archivos TXT
    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only TXT files are allowed."
        )

    # Leemos el archivo respetando el límite de tamaño
    content = await file.read(MAX_FILE_SIZE + 1)

    # Rechazamos archivos demasiado grandes
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 1 MB limit."
        )

    # Rechazamos archivos vacíos
    if not content:
        raise HTTPException(
            status_code=400,
            detail="File cannot be empty."
        )

    # Verificamos que el contenido sea texto UTF-8
    try:
        text_content = content.decode("utf-8")

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must contain valid UTF-8 text."
        )

    # Rechazamos documentos sin contenido útil
    if not text_content.strip():
        raise HTTPException(
            status_code=400,
            detail="File cannot contain only whitespace."
        )

    # Creamos la carpeta de archivos si todavía no existe
    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generamos un nombre único para evitar sobrescribir archivos
    document_id = uuid4().hex
    original_filename = Path(file.filename).name
    saved_filename = f"{document_id}.txt"

    # Definimos la ubicación del archivo
    file_path = UPLOAD_DIRECTORY / saved_filename

    # Creamos el documento con información de su origen
    document = Document(
        page_content=text_content,
        metadata={
            "source": file_path.as_posix(),
            "filename": original_filename,
            "uploaded_by": current_user.id,
            "document_id": document_id
        }
    )

    # Configuramos cómo dividiremos el texto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    # Dividimos el documento en fragmentos
    chunks = text_splitter.split_documents([document])

    # Generamos identificadores únicos para los fragmentos
    chunk_ids = [
        f"{document_id}:{index}"
        for index in range(len(chunks))
    ]

    # Guardamos el archivo original
    file_path.write_bytes(content)

    try:

        # Obtenemos nuestra base vectorial
        vectorstore = get_vectorstore()

        # Almacenamos los fragmentos y sus embeddings
        vectorstore.add_documents(
            documents=chunks,
            ids=chunk_ids
        )

    except Exception:

        # Eliminamos el archivo si falla la indexación
        file_path.unlink(missing_ok=True)

        # Informamos que no fue posible procesar el documento
        raise HTTPException(
            status_code=500,
            detail="Document indexing failed."
        )

    # Devolvemos la información del documento procesado
    return {
        "message": "Document uploaded and indexed successfully.",
        "document_id": document_id,
        "filename": original_filename,
        "chunks_created": len(chunks),
        "uploaded_by": current_user.username
    }
