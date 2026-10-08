# Importamos ChatOllama para conectar LangChain con Ollama
from langchain_ollama import ChatOllama

# Configuramos nuestro modelo de inteligencia artificial
model = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# Función para enviar preguntas al modelo
def ask_model(question: str) -> str:

    # Enviamos la pregunta al modelo
    response = model.invoke(question)

    # Devolvemos únicamente el contenido de la respuesta
    return str(response.content)