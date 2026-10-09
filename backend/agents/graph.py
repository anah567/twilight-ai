# Importamos las herramientas para construir nuestro grafo
from langgraph.graph import StateGraph, START, END

# Importamos TypedDict para definir el estado del agente
from typing import TypedDict

# Importamos nuestro modelo de Ollama
from backend.agents.model import model

# Importamos la búsqueda de documentos en ChromaDB
from backend.vectorstore.retriever import search_documents


# CONFIGURACIÓN DEL AGENTE

# Mensaje que utilizaremos cuando no exista información suficiente
FALLBACK_ANSWER = (
    "I don't have enough information to answer that question."
)



# ESTADO DEL AGENTE

# Definimos la información que utiliza nuestro agente
class AgentState(TypedDict):

    # Pregunta actual del usuario
    question: str

    # Mensajes anteriores de la conversación
    chat_history: str

    # Información recuperada de los documentos
    context: str

    # Respuesta final del agente
    answer: str


# NODO 1: INTERPRETAR LA PREGUNTA

# Convertimos preguntas de seguimiento en preguntas completas
def rewrite_question(state: AgentState) -> dict:

    # Obtenemos la pregunta actual
    question = state["question"]

    # Obtenemos el historial de la conversación
    chat_history = state["chat_history"]

    # Si no hay historial, conservamos la pregunta original
    if not chat_history.strip():
        return {"question": question}

    # Creamos instrucciones para interpretar preguntas de seguimiento
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


# NODO 2: RECUPERAR DOCUMENTOS

# Buscamos información relacionada con la pregunta
def retrieve_documents(state: AgentState) -> dict:

    # Consultamos los documentos almacenados en ChromaDB
    documents = search_documents(state["question"])

    # Unimos los fragmentos recuperados en un solo contexto
    context = "\n\n".join(
        document.page_content for document in documents
    )

    # Devolvemos la información encontrada
    return {"context": context}


# NODO 3: GENERAR LA RESPUESTA

# Respondemos utilizando únicamente los documentos recuperados
def answer_question(state: AgentState) -> dict:

    # Obtenemos el contexto recuperado de ChromaDB
    context = state["context"].strip()

    # Si no encontramos documentos, devolvemos el mensaje de rechazo
    if not context:
        return {"answer": FALLBACK_ANSWER}

    # Creamos instrucciones para responder solo con información documentada
    prompt = f"""
You are Twilight AI, an assistant specialized in the Twilight saga.

Answer the QUESTION using ONLY the provided CONTEXT.

IMPORTANT RULES:
1. Use only information explicitly stated or directly supported by the context.
2. Do not use outside knowledge.
3. Do not invent names, dates, numbers, relationships, or other facts.
4. You may combine information from different sentences in the context.
5. The question and context do not need to use identical wording.
6. If the context does not contain enough information to answer,
   reply EXACTLY:
   {FALLBACK_ANSWER}
7. Do not explain why information is missing.
8. Answer in English.
9. Give a clear, concise answer.

CONTEXT:
{context}

QUESTION:
{state["question"]}

ANSWER:
"""

    # Enviamos las instrucciones a Ollama
    response = model.invoke(prompt)

    # Obtenemos la respuesta generada
    answer = str(response.content).strip()

    # Si el modelo no devuelve texto, utilizamos el mensaje de rechazo
    if not answer:
        return {"answer": FALLBACK_ANSWER}

    # Devolvemos la respuesta final
    return {"answer": answer}



# CONSTRUCCIÓN DEL GRAFO

# Creamos nuestro grafo utilizando el estado del agente
graph_builder = StateGraph(AgentState)

# Registramos los tres nodos de nuestro agente
graph_builder.add_node("rewrite_question", rewrite_question)
graph_builder.add_node("retrieve_documents", retrieve_documents)
graph_builder.add_node("answer_question", answer_question)

# Primero interpretamos la pregunta utilizando el historial
graph_builder.add_edge(START, "rewrite_question")

# Después buscamos documentos relacionados con la pregunta
graph_builder.add_edge("rewrite_question", "retrieve_documents")

# Generamos la respuesta utilizando los documentos recuperados
graph_builder.add_edge("retrieve_documents", "answer_question")

# Finalizamos después de generar la respuesta
graph_builder.add_edge("answer_question", END)

# Compilamos nuestro agente
agent_graph = graph_builder.compile()


# FUNCIÓN PRINCIPAL DEL AGENTE

# Ejecutamos nuestro agente desde FastAPI
def ask_agent(question: str, chat_history: str = "") -> str:

    # Enviamos la pregunta y el historial al grafo
    result = agent_graph.invoke({
        "question": question,
        "chat_history": chat_history,
        "context": "",
        "answer": ""
    })

    # Devolvemos la respuesta generada por el agente
    return result["answer"]
