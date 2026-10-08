
# Importamos hashlib para generar identificadores únicos
import hashlib

# Importamos Path para trabajar con archivos y carpetas
from pathlib import Path

# Importamos Document para representar nuestros documentos
from langchain_core.documents import Document

# Importamos la herramienta para dividir textos
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importamos nuestra conexión con ChromaDB
from backend.vectorstore.vectorstore import get_vectorstore


# Definimos la carpeta de nuestros documentos
DOCUMENTS_PATH = Path("documents")


# Función para generar un identificador único por fragmento
def generate_chunk_id(source: str, index: int) -> str:

    # Combinamos la ruta del archivo con el número del fragmento
    identifier = f"{source}:{index}"

    # Convertimos el identificador en un hash
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()


# Función para procesar y almacenar documentos
def ingest_documents():

    # Obtenemos nuestra base vectorial
    vectorstore = get_vectorstore()

    # Buscamos todos los archivos TXT
    files = sorted(DOCUMENTS_PATH.rglob("*.txt"))

    # Verificamos que existan documentos
    if not files:
        print("No documents found.")
        return

    # Configuramos la división de los textos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    # Contador de fragmentos procesados
    total_chunks = 0

    # Recorremos cada archivo
    for file in files:

        # Leemos el contenido del documento
        content = file.read_text(encoding="utf-8")

        # Ignoramos archivos vacíos
        if not content.strip():
            continue

        # Creamos el documento con información de origen
        document = Document(
            page_content=content,
            metadata={"source": file.as_posix()}
        )

        # Dividimos el documento en fragmentos
        chunks = text_splitter.split_documents([document])

        # Generamos identificadores únicos para los fragmentos
        chunk_ids = [
            generate_chunk_id(file.as_posix(), index)
            for index in range(len(chunks))
        ]

        # Consultamos los fragmentos anteriores de este archivo
        existing = vectorstore.get(
            where={"source": file.as_posix()}
        )

        # Eliminamos versiones anteriores del documento
        if existing["ids"]:
            vectorstore.delete(ids=existing["ids"])

        # Guardamos los fragmentos actualizados
        vectorstore.add_documents(
            documents=chunks,
            ids=chunk_ids
        )

        # Actualizamos el contador
        total_chunks += len(chunks)

    # Mostramos el resultado del procesamiento
    print(f"Successfully processed {len(files)} documents.")
    print(f"Successfully stored {total_chunks} chunks.")
