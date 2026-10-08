
# Importamos las herramientas para construir nuestro grafo
from langgraph.graph import StateGraph, START, END

# Importamos TypedDict para definir el estado del agente
from typing import TypedDict

# Importamos nuestro modelo de inteligencia artificial
from backend.agents.model import model

# Importamos la función que busca información en ChromaDB
from backend.vectorstore.retriever import search_documents


# Definimos la información que guardará nuestro agente
class AgentState(TypedDict):
    question: str
    context: str
    answer: str


# Primer nodo: buscar información en nuestra base de conocimiento
def retrieve_documents(state: AgentState) -> dict:

    # Obtenemos la pregunta del usuario
    question = state["question"]

    # Buscamos documentos relacionados con la pregunta
    documents = search_documents(question)

    # Unimos el contenido de los documentos encontrados
    context = "\n\n".join(
        document.page_content for document in documents
    )

    # Guardamos el contexto para utilizarlo en el siguiente nodo
    return {"context": context}


# Segundo nodo: generar una respuesta utilizando los documentos
def answer_question(state: AgentState) -> dict:

    # Obtenemos la pregunta y la información recuperada
    question = state["question"]
    context = state["context"]

    # Verificamos si encontramos información
    if not context.strip():
        return {
            "answer": "I don't have enough information to answer that question."
        }

    # Creamos instrucciones para que el modelo utilice los documentos
    prompt = f"""
You are Twilight AI, an assistant specialized in the Twilight saga.

Answer the user's question using ONLY the information
provided in the context below.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the context does not contain the answer, say:
  "I don't have enough information to answer that question."
- Answer in English.

Context:
{context}

Question:
{question}
"""

    # Enviamos las instrucciones a nuestro modelo Qwen
    response = model.invoke(prompt)

    # Guardamos la respuesta generada
    return {"answer": str(response.content)}


# Creamos el grafo de nuestro agente
graph_builder = StateGraph(AgentState)

# Agregamos los dos nodos
graph_builder.add_node("retrieve_documents", retrieve_documents)
graph_builder.add_node("answer_question", answer_question)

# Definimos el orden de ejecución
graph_builder.add_edge(START, "retrieve_documents")
graph_builder.add_edge("retrieve_documents", "answer_question")
graph_builder.add_edge("answer_question", END)

# Compilamos el grafo
agent_graph = graph_builder.compile()


# Función para hacer preguntas a nuestro agente
def ask_agent(question: str) -> str:

    # Ejecutamos el grafo con la pregunta del usuario
    result = agent_graph.invoke({
        "question": question,
        "context": "",
        "answer": ""
    })

    # Devolvemos la respuesta final
    return result["answer"]
