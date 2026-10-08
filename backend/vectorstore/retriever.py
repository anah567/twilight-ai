
# Importamos la conexión con nuestra base vectorial
from backend.vectorstore.vectorstore import get_vectorstore


# Definimos la distancia máxima permitida
# Este valor es inicial y deberá ajustarse con pruebas reales
MAX_DISTANCE = 1.0


# Función para buscar documentos relacionados con una pregunta
def search_documents(question: str):

    # Obtenemos nuestra base de datos vectorial
    vectorstore = get_vectorstore()

    # Buscamos los tres fragmentos más cercanos
    # También recuperamos la distancia de cada resultado
    results = vectorstore.similarity_search_with_score(
        query=question,
        k=3
    )

    # Creamos una lista para guardar documentos relevantes
    relevant_documents = []

    # Revisamos la distancia de cada fragmento
    for document, distance in results:

        # Una distancia menor indica mayor similitud
        if distance <= MAX_DISTANCE:

            # Conservamos únicamente los fragmentos relevantes
            relevant_documents.append(document)

    # Devolvemos los documentos que superaron el filtro
    return relevant_documents
