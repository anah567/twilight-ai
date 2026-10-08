
# Importamos las herramientas para construir nuestro grafo
from langgraph.graph import StateGraph, START, END

# Importamos TypedDict para definir el estado del agente
from typing import TypedDict

# Importamos nuestro modelo de Ollama
from backend.agents.model import model

# Importamos la búsqueda de documentos
from backend.vectorstore.retriever import search_documents


# Mensaje que utilizaremos cuando no exista información suficiente
FALLBACK_ANSWER = (
    "I don't have enough information to answer that question."
)


# Definimos la información que guarda nuestro agente
class AgentState(TypedDict):
    question: str
    context: str
    is_answerable: bool
    answer: str


# Primer nodo: recuperar documentos relevantes
def retrieve_documents(state: AgentState) -> dict:

    # Buscamos documentos relacionados con la pregunta
    documents = search_documents(state["question"])

    # Unimos los fragmentos recuperados
    context = "\n\n".join(
        document.page_content for document in documents
    )

    return {"context": context}


# Segundo nodo: verificar si los documentos contienen la respuesta
def validate_context(state: AgentState) -> dict:

    # Si no encontramos documentos, rechazamos la pregunta
    if not state["context"].strip():
        return {"is_answerable": False}

    # Pedimos al modelo evaluar la información disponible
    prompt = f"""
You are a strict evidence validator.

Determine whether the context contains enough information
to answer the question.

Rules:
- Use ONLY the provided context.
- Do not use outside knowledge.
- Do not guess or infer missing facts.
- Reply with exactly YES or NO.
- Reply YES only when the answer is explicitly supported.

Context:
{state["context"]}

Question:
{state["question"]}

Decision:
"""

    # Consultamos al modelo
    response = model.invoke(prompt)

    # Normalizamos la respuesta para evitar problemas con espacios
    decision = str(response.content).strip().upper()

    # Solo aceptamos una respuesta exactamente igual a YES
    return {"is_answerable": decision == "YES"}


# Decidimos qué camino seguirá el agente
def route_after_validation(state: AgentState) -> str:

    # Si existe evidencia, podemos generar la respuesta
    if state["is_answerable"]:
        return "answer_question"

    # Si falta evidencia, rechazamos la pregunta
    return "reject_question"


# Tercer nodo: generar una respuesta basada en documentos
def answer_question(state: AgentState) -> dict:

    # Construimos instrucciones para responder únicamente con evidencia
    prompt = f"""
You are Twilight AI, an assistant specialized in the Twilight saga.

Answer the question using ONLY the provided context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- Do not add unsupported details.
- If the answer is not supported, reply exactly:
  "{FALLBACK_ANSWER}"
- Answer in English.

Context:
{state["context"]}

Question:
{state["question"]}
"""

    # Generamos la respuesta
    response = model.invoke(prompt)

    return {"answer": str(response.content)}


# Nodo encargado de rechazar preguntas sin información suficiente
def reject_question(state: AgentState) -> dict:

    # Devolvemos el mensaje de rechazo
    return {"answer": FALLBACK_ANSWER}


# Creamos nuestro grafo
graph_builder = StateGraph(AgentState)

# Registramos los nodos
graph_builder.add_node("retrieve_documents", retrieve_documents)
graph_builder.add_node("validate_context", validate_context)
graph_builder.add_node("answer_question", answer_question)
graph_builder.add_node("reject_question", reject_question)

# Definimos el inicio del flujo
graph_builder.add_edge(START, "retrieve_documents")
graph_builder.add_edge("retrieve_documents", "validate_context")

# Elegimos el siguiente nodo según la validación
graph_builder.add_conditional_edges(
    "validate_context",
    route_after_validation,
    {
        "answer_question": "answer_question",
        "reject_question": "reject_question"
    }
)

# Ambos caminos terminan el proceso
graph_builder.add_edge("answer_question", END)
graph_builder.add_edge("reject_question", END)

# Compilamos el grafo
agent_graph = graph_builder.compile()


# Función principal para consultar nuestro agente
def ask_agent(question: str) -> str:

    # Ejecutamos el grafo con su estado inicial
    result = agent_graph.invoke({
        "question": question,
        "context": "",
        "is_answerable": False,
        "answer": ""
    })

    # Devolvemos la respuesta final
    return result["answer"]
