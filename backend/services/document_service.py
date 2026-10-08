
# Importamos Path para trabajar con rutas de archivos
from pathlib import Path

# Importamos Document para representar textos con sus datos de origen
from langchain_core.documents import Document

# Importamos la herramienta que divide textos en fragmentos
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importamos nuestra conexión con ChromaDB
from backend.vectorstore.vectorstore import get_vectorstore


# Definimos la carpeta donde están nuestros documentos
DOCUMENTS_PATH = Path("documents")


# Función para leer, procesar y guardar los documentos
def ingest_documents():

    # Obtenemos la conexión con nuestra base vectorial
    vectorstore = get_vectorstore()

    # Buscamos todos los archivos TXT dentro de documents
    files = list(DOCUMENTS_PATH.rglob("*.txt"))

    # Verificamos si encontramos documentos
    if not files:
        print("No documents found.")
        return

    # Creamos una lista para guardar los documentos leídos
    documents = []

    # Recorremos cada archivo encontrado
    for file in files:

        # Leemos el contenido del archivo
        content = file.read_text(encoding="utf-8")

        # Creamos un documento con su contenido y origen
        document = Document(
            page_content=content,
            metadata={"source": str(file)}
        )

        # Agregamos el documento a nuestra lista
        documents.append(document)

    # Configuramos cómo se dividirán los documentos
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # Máximo de caracteres por fragmento
        chunk_overlap=100    # Caracteres compartidos entre fragmentos
    )

    # Dividimos los documentos en fragmentos
    chunks = text_splitter.split_documents(documents)

    # Guardamos los fragmentos y generamos sus embeddings
    vectorstore.add_documents(chunks)

    # Mostramos cuántos fragmentos se almacenaron
    print(f"Successfully stored {len(chunks)} chunks.")
