
# Importamos ChatGroq para conectar LangChain con Groq
from langchain_groq import ChatGroq

# Configuramos nuestro modelo de inteligencia artificial
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# Función para enviar preguntas al modelo
def ask_model(question: str) -> str:

    # Enviamos la pregunta al modelo
    response = model.invoke(question)

    # Devolvemos únicamente el contenido de la respuesta
    return str(response.content)
