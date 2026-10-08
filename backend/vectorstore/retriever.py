
# Importamos la conexión con nuestra base vectorial
from backend.vectorstore.vectorstore import get_vectorstore


# Función para buscar documentos relacionados con una pregunta
def search_documents(question: str):

    # Obtenemos nuestra base de datos vectorial
    vectorstore = get_vectorstore()

    # Buscamos los documentos más relacionados con la pregunta
    # k=3 significa que podemos recuperar hasta 3 fragmentos
    results = vectorstore.similarity_search(
        query=question,
        k=3
    )

    # Devolvemos los documentos encontrados
    return results
