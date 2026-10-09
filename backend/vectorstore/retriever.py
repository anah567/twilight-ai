# Importamos la conexión con nuestra base vectorial
from backend.vectorstore.vectorstore import get_vectorstore


# Definimos cuántos fragmentos queremos recuperar
TOP_K = 3


# Función para buscar documentos relacionados con una pregunta
def search_documents(question: str):

    # Obtenemos nuestra base de datos vectorial
    vectorstore = get_vectorstore()

    # Buscamos los tres fragmentos más cercanos a la pregunta
    relevant_documents = vectorstore.similarity_search(
        query=question,
        k=TOP_K
    )

    # Devolvemos los documentos encontrados
    return relevant_documents