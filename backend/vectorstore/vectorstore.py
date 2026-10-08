
# Importamos Chroma para almacenar y buscar documentos
from langchain_chroma import Chroma

# Importamos el modelo que convierte textos en vectores
from langchain_huggingface import HuggingFaceEmbeddings


# Definimos dónde se guardará nuestra base vectorial
DATABASE_PATH = "./chroma_db"

# Definimos el nombre de nuestra colección
COLLECTION_NAME = "twilight_knowledge"


# Configuramos el modelo de embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Función para obtener nuestra base vectorial
def get_vectorstore():

    # Creamos o abrimos nuestra colección de ChromaDB
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DATABASE_PATH
    )

    # Devolvemos la base vectorial
    return vectorstore
