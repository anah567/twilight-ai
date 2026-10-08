
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


# Definimos la información que utiliza nuestro agente
class AgentState(TypedDict):
    question: str
    chat_history: str
    context: str
    is_answerable: bool
    answer: str


# Función para convertir preguntas de seguimiento en preguntas completas
def rewrite_question(state: AgentState) -> dict:

    # Obtenemos la pregunta actual
    question = state["question"]

    # Obtenemos el historial de la conversación
    chat_history = state["chat_history"]

    # Si no hay historial, conservamos la pregunta original
    if not chat_history.strip():
        return {"question": question}

    # Pedimos al modelo que interprete la pregunta usando el historial
    prompt = f"""
You are a question rewriting assistant.

Your task is to rewrite the current question so it can be
understood without reading the conversation history.

RULES:
1. Use the conversation history only to resolve references.
2. Do not answer the question.
3. Do not invent facts or introduce new information.
4. Keep the original meaning of the question.
5. If the question is already clear, return it unchanged.
6. Return only the rewritten question.
7. Write in English.

Conversation history:
{chat_history}

Current question:
{question}

Rewritten question:
"""

    # Enviamos las instrucciones al modelo
    response = model.invoke(prompt)

    # Obtenemos la pregunta reformulada
    rewritten_question = str(response.content).strip()

    # Si el modelo no devuelve texto, usamos la pregunta original
    if not rewritten_question:
        rewritten_question = question

    # Devolvemos la pregunta que utilizaremos para buscar documentos
    return {"question": rewritten_question}



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

    
    # Creamos instrucciones para verificar si existe evidencia suficiente
    prompt = f"""
You are a strict evidence verification assistant.

Your task is to decide whether the provided context contains
enough information to answer the user's question.

RULES:
1. Use ONLY the provided context.
2. Do not use outside knowledge.
3. Do not invent missing information.
4. For "Who is..." questions, a description of the person is sufficient.
5. For questions about specific facts, those facts must appear in the context.
6. Information may be spread across multiple sentences.
7. Do not require the exact wording of the question to appear.
8. Reply with exactly one word: YES or NO.

EXAMPLE 1:
Context:
Emma Smith is a doctor who lives in London.
She works at a hospital.

Question:
Who is Emma Smith?

Decision:
YES

EXAMPLE 2:
Context:
Emma lives with her father, John Smith.
Her mother is Mary Smith.

Question:
Who are Emma's parents?

Decision:
YES

EXAMPLE 3:
Context:
Emma Smith is a doctor who lives in London.

Question:
What is Emma Smith's exact date of birth?

Decision:
NO

NOW EVALUATE:

Context:
{state["context"]}

Question:
{state["question"]}

Decision:
"""

    # Consultamos al modelo
    response = model.invoke(prompt)

        # Normalizamos la respuesta del modelo
    decision = str(response.content).strip().upper()


    # Solo aceptamos respuestas exactamente iguales a YES
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



# Creamos nuestro grafo utilizando el estado del agente
graph_builder = StateGraph(AgentState)

# Registramos todos los nodos del agente
graph_builder.add_node("rewrite_question", rewrite_question)
graph_builder.add_node("retrieve_documents", retrieve_documents)
graph_builder.add_node("validate_context", validate_context)
graph_builder.add_node("answer_question", answer_question)
graph_builder.add_node("reject_question", reject_question)

# Primero interpretamos la pregunta usando el historial
graph_builder.add_edge(START, "rewrite_question")

# Después buscamos documentos relacionados con la pregunta
graph_builder.add_edge("rewrite_question", "retrieve_documents")

# Verificamos si los documentos contienen información suficiente
graph_builder.add_edge("retrieve_documents", "validate_context")

# Elegimos si podemos responder o debemos rechazar la pregunta
graph_builder.add_conditional_edges(
    "validate_context",
    route_after_validation,
    {
        "answer_question": "answer_question",
        "reject_question": "reject_question"
    }
)

# Finalizamos después de responder
graph_builder.add_edge("answer_question", END)

# Finalizamos después de rechazar una pregunta
graph_builder.add_edge("reject_question", END)

# Compilamos nuestro agente
agent_graph = graph_builder.compile()


# Función principal para ejecutar nuestro agente
def ask_agent(question: str, chat_history: str = "") -> str:

    # Ejecutamos el grafo con la pregunta y el historial
    result = agent_graph.invoke({
        "question": question,
        "chat_history": chat_history,
        "context": "",
        "is_answerable": False,
        "answer": ""
    })

    # Devolvemos la respuesta del agente
    return result["answer"]