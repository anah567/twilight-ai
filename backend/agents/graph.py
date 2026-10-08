
# Importamos las herramientas para construir nuestro grafo
from langgraph.graph import StateGraph, START, END

# TypedDict nos permite definir qué información guarda el agente
from typing import TypedDict

# Importamos la función que conecta con nuestro modelo Qwen
from backend.agents.model import ask_model


# Definimos el estado de nuestro agente
# Aquí guardaremos la pregunta y la respuesta
class AgentState(TypedDict):
    question: str
    answer: str


# Creamos el nodo encargado de responder preguntas
def answer_question(state: AgentState) -> dict:

    # Obtenemos la pregunta guardada en el estado
    question = state["question"]

    # Enviamos la pregunta a nuestro modelo de Ollama
    answer = ask_model(question)

    # Guardamos la respuesta en el estado
    return {"answer": answer}


# Creamos el grafo que organizará nuestro agente
graph_builder = StateGraph(AgentState)

# Agregamos el nodo que genera las respuestas
graph_builder.add_node("answer_question", answer_question)

# Indicamos que el grafo comienza en este nodo
graph_builder.add_edge(START, "answer_question")

# Indicamos que el grafo termina después de responder
graph_builder.add_edge("answer_question", END)

# Compilamos el grafo para poder ejecutarlo
agent_graph = graph_builder.compile()


# Función para ejecutar nuestro agente desde otros archivos
def ask_agent(question: str) -> str:

    # Ejecutamos el grafo enviándole la pregunta
    result = agent_graph.invoke({
        "question": question,
        "answer": ""
    })

    # Devolvemos la respuesta generada por el agente
    return result["answer"]
