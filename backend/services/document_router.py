
# Importamos herramientas para identificar archivos y crear nombres únicos
import hashlib
from pathlib import Path
from uuid import UUID, uuid4

# Importamos herramientas de FastAPI
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

# Importamos herramientas para procesar documentos
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importamos la base vectorial de Twilight AI
from backend.vectorstore.vectorstore import get_vectorstore

# Importamos el modelo de usuario y la autenticación
from backend.database.models import User

# Importamos la dependencia que exige permisos de administrador
from backend.auth.dependencies import get_current_admin


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
    current_user: User = Depends(get_current_admin)
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

    # Generamos una huella digital basada en el contenido
    content_hash = hashlib.sha256(content).hexdigest()

    # Consultamos ChromaDB para buscar documentos idénticos
    vectorstore = get_vectorstore()

    existing_documents = vectorstore.get(
        where={"content_hash": content_hash}
    )

    # Rechazamos el documento si ya está indexado
    if existing_documents["ids"]:
        raise HTTPException(
            status_code=409,
            detail="This document has already been uploaded."
        )

    # Creamos la carpeta de archivos si todavía no existe
    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generamos un identificador único para el documento
    document_id = uuid4().hex

    # Conservamos el nombre original solo como información
    original_filename = Path(file.filename).name

    # Creamos un nombre seguro y único para guardarlo
    saved_filename = f"{document_id}.txt"

    # Definimos la ubicación del archivo
    file_path = UPLOAD_DIRECTORY / saved_filename

    # Creamos el documento con sus metadatos
    document = Document(
        page_content=text_content,
        metadata={
            "source": file_path.as_posix(),
            "filename": original_filename,
            "uploaded_by": current_user.id,
            "document_id": document_id,
            "content_hash": content_hash
        }
    )

    # Configuramos la división del texto en fragmentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    # Dividimos el documento
    chunks = text_splitter.split_documents([document])

    # Generamos identificadores únicos para cada fragmento
    chunk_ids = [
        f"{document_id}:{index}"
        for index in range(len(chunks))
    ]

    # Guardamos el archivo original
    file_path.write_bytes(content)

    try:

        # Almacenamos los fragmentos en ChromaDB
        vectorstore.add_documents(
            documents=chunks,
            ids=chunk_ids
        )

    except Exception:

        # Eliminamos el archivo si falla la indexación
        file_path.unlink(missing_ok=True)

        # Informamos que ocurrió un error
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


# Endpoint protegido para consultar los documentos cargados
@router.get("/")
def list_documents(
    current_user: User = Depends(get_current_admin)
):

    # Obtenemos la base vectorial
    vectorstore = get_vectorstore()

    # Consultamos los metadatos de los documentos
    results = vectorstore.get(
        include=["metadatas"]
    )

    # Creamos un diccionario para evitar repetir documentos
    documents = {}

    # Recorremos los metadatos de cada fragmento
    for metadata in results["metadatas"]:

        # Ignoramos fragmentos que no provienen de cargas
        if not metadata or "document_id" not in metadata:
            continue

        # Obtenemos el identificador del documento
        document_id = metadata["document_id"]

        # Guardamos una sola entrada por documento
        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get("filename"),
                "uploaded_by": metadata.get("uploaded_by")
            }

    # Devolvemos los documentos encontrados
    return {
        "total_documents": len(documents),
        "documents": list(documents.values())
    }




# Endpoint protegido para eliminar documentos cargados
@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_admin)
):

    # Verificamos que el identificador tenga un formato UUID válido
    try:
        normalized_id = UUID(document_id).hex

    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid document ID."
        )

    # Obtenemos nuestra base vectorial
    vectorstore = get_vectorstore()

    # Buscamos los fragmentos usando el identificador validado
    results = vectorstore.get(
        where={"document_id": normalized_id},
        include=["metadatas"]
    )

    # Verificamos que el documento exista
    if not results["ids"]:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # Construimos la ruta segura del archivo TXT
    file_path = UPLOAD_DIRECTORY / f"{normalized_id}.txt"

    # Eliminamos los fragmentos de ChromaDB
    vectorstore.delete(ids=results["ids"])

    # Eliminamos el archivo original si todavía existe
    file_path.unlink(missing_ok=True)

    # Confirmamos la eliminación
    return {
        "message": "Document deleted successfully.",
        "document_id": normalized_id,
        "chunks_deleted": len(results["ids"])
    }
