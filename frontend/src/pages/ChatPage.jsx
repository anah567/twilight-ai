
import { useEffect, useState } from "react";

import { sendMessage } from "../services/chatService";

import {
  getConversations,
  getConversationById,
} from "../services/conversationService";

import DocumentLibrary from "./DocumentLibrary";

import "../styles/ChatPage.css";

// Preguntas sugeridas en la pantalla de bienvenida
const suggestedQuestions = [
  "Who is Edward Cullen?",
  "What makes the Cullen family different?",
  "Tell me about Bella Swan.",
  "What is the history of the Volturi?",
];

export default function ChatPage({ onLogout }) {
  // Guardamos el texto que escribe el usuario
  const [message, setMessage] = useState("");

  // Guardamos los mensajes de la conversación actual
  const [messages, setMessages] = useState([]);

  // Identificador de la conversación actual
  const [conversationId, setConversationId] = useState(null);

  // Indicamos si el agente está generando una respuesta
  const [isLoading, setIsLoading] = useState(false);

  // Guardamos posibles errores del chat
  const [chatError, setChatError] = useState("");

  // Guardamos las conversaciones del usuario
  const [conversations, setConversations] = useState([]);

  // Controlamos la carga del historial
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  // Guardamos posibles errores del historial
  const [historyError, setHistoryError] = useState("");

  // Controlamos si mostramos el chat o la biblioteca
  const [activeView, setActiveView] = useState("chat");

  // Consultamos el historial al abrir el chat
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const data = await getConversations();

        setConversations(data);
        setHistoryError("");
      } catch (error) {
        setHistoryError(
          error.message || "Unable to load conversations."
        );
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadConversations();
  }, []);

  // Abrimos una conversación guardada
  const handleOpenConversation = async (id) => {
    // Evitamos cambiar de conversación mientras el agente responde
    if (isLoading || isLoadingHistory) return;

    setIsLoadingHistory(true);
    setChatError("");

    try {
      // Recuperamos la conversación desde FastAPI
      const data = await getConversationById(id);

      // Mostramos sus mensajes guardados
      setMessages(data.messages);

      // Establecemos la conversación activa
      setConversationId(data.id);

      // Limpiamos el campo de texto
      setMessage("");

      // Regresamos al chat si estábamos en Document Library
      setActiveView("chat");
    } catch (error) {
      setChatError(
        error.message || "Unable to open conversation."
      );
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Preparamos una conversación completamente nueva
  const handleNewChat = () => {
    if (isLoading || isLoadingHistory) return;

    // Regresamos a la pantalla principal del chat
    setActiveView("chat");

    // Limpiamos los mensajes visibles
    setMessages([]);

    // El backend creará otra conversación
    setConversationId(null);

    // Limpiamos el campo de texto y los errores
    setMessage("");
    setChatError("");
  };

  // Enviamos una pregunta al agente de Twilight AI
  const handleSubmit = async (event) => {
    event.preventDefault();

    const question = message.trim();

    if (!question || isLoading) return;

    // Mostramos inmediatamente la pregunta
    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: question,
      },
    ]);

    setMessage("");
    setChatError("");
    setIsLoading(true);

    try {
      // Enviamos la pregunta a FastAPI
      const data = await sendMessage(
        question,
        conversationId
      );

      // Guardamos el identificador de la conversación
      setConversationId(data.conversation_id);

      // Mostramos la respuesta del agente
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);

      // Actualizamos el historial sin afectar la respuesta
      try {
        const updatedConversations = await getConversations();

        setConversations(updatedConversations);
        setHistoryError("");
      } catch (historyLoadError) {
        setHistoryError(
          historyLoadError.message ||
            "Unable to refresh conversations."
        );
      }
    } catch (error) {
      // Mostramos el error si falla el envío
      setChatError(
        error.message || "Unable to get a response."
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Colocamos una pregunta sugerida en el campo de texto
  const selectQuestion = (question) => {
    setMessage(question);
  };

  return (
    <main className="chat-page">

      {/* =====================================
          MENÚ LATERAL
          ===================================== */}
      <aside className="chat-sidebar">

        {/* Logo de Twilight AI */}
        <div className="chat-brand">
          <h2>
            Twilight <span>AI</span>
          </h2>

          <div className="chat-brand-decoration">
            <span>☾</span>
          </div>
        </div>

        {/* Botón para comenzar una nueva conversación */}
        <button
          className="new-chat-button"
          type="button"
          onClick={handleNewChat}
          disabled={isLoading || isLoadingHistory}
        >
          <span className="chat-plus">＋</span>
          New Chat
        </button>

        {/* Navegación entre las pantallas */}
        <nav className="chat-navigation">

          <button
            type="button"
            onClick={() => setActiveView("chat")}
          >
            <span>☷</span>
            Chat History
          </button>

          <button
            type="button"
            onClick={() => setActiveView("documents")}
          >
            <span>▤</span>
            Document Library
          </button>

        </nav>

        <div className="chat-sidebar-divider" />

        {/* =====================================
            HISTORIAL DE CONVERSACIONES
            ===================================== */}
        <div className="chat-history-section">

          <p className="chat-section-title">
            RECENT CONVERSATIONS
          </p>

          {/* Estado de carga */}
          {isLoadingHistory && (
            <p className="chat-empty-history">
              Loading conversations...
            </p>
          )}

          {/* Errores del historial */}
          {!isLoadingHistory && historyError && (
            <p className="chat-empty-history">
              {historyError}
            </p>
          )}

          {/* Historial vacío */}
          {!isLoadingHistory &&
            !historyError &&
            conversations.length === 0 && (
              <p className="chat-empty-history">
                Your conversations will appear here.
              </p>
            )}

          {/* Conversaciones guardadas */}
          {!isLoadingHistory && !historyError && (
            <div className="chat-conversation-list">

              {conversations.map((conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  className={`chat-conversation-item ${
                    conversationId === conversation.id
                      ? "chat-conversation-active"
                      : ""
                  }`}
                  onClick={() =>
                    handleOpenConversation(conversation.id)
                  }
                  disabled={isLoading || isLoadingHistory}
                >
                  <span className="chat-conversation-icon">
                    ☾
                  </span>

                  <span className="chat-conversation-title">
                    {conversation.title}
                  </span>
                </button>
              ))}

            </div>
          )}

        </div>

        {/* =====================================
            PERFIL Y CIERRE DE SESIÓN
            ===================================== */}
        <div className="chat-sidebar-bottom">

          <div className="chat-profile">
            <div className="chat-avatar">☾</div>

            <div className="chat-profile-info">
              <strong>Twilight Explorer</strong>
              <span>Your account</span>
            </div>
          </div>

          <button
            className="chat-logout"
            type="button"
            onClick={onLogout}
          >
            <span>↪</span>
            Log out
          </button>

        </div>

      </aside>

      {/* =====================================
          CONTENIDO PRINCIPAL
          ===================================== */}
      <section className="chat-main">

        {activeView === "documents" ? (

          // Mostramos Document Library
          <DocumentLibrary
            onBack={() => setActiveView("chat")}
          />

        ) : (

          // Mostramos el contenido del chat
          <>

            {/* Mensajes de la conversación */}
            {messages.length > 0 && (
              <div className="chat-messages">

                {messages.map((item, index) => (
                  <div
                    key={item.id ?? index}
                    className={`chat-message ${
                      item.role === "user"
                        ? "chat-message-user"
                        : "chat-message-assistant"
                    }`}
                  >
                    <span className="chat-message-role">
                      {item.role === "user"
                        ? "You"
                        : "Twilight AI"}
                    </span>

                    <p>{item.content}</p>
                  </div>
                ))}

                {/* Indicador mientras el agente responde */}
                {isLoading && (
                  <div className="chat-message chat-message-assistant">
                    <span className="chat-message-role">
                      Twilight AI
                    </span>
                    <p>Thinking...</p>
                  </div>
                )}

              </div>
            )}

            {/* Errores del chat */}
            {chatError && (
              <p className="chat-error" role="alert">
                {chatError}
              </p>
            )}

            {/* Pantalla de bienvenida */}
            {messages.length === 0 && (
              <div className="chat-welcome">

                <div className="chat-welcome-decoration">
                  <span>☾</span>
                </div>

                <h1>
                  Welcome to the
                  <br />
                  Twilight <span>universe</span>
                </h1>

                <p className="chat-welcome-description">
                  Explore the mysteries of Forks, discover
                  unforgettable characters, and uncover
                  the secrets of Twilight.
                </p>

                {/* Preguntas sugeridas */}
                <div className="chat-suggestions">

                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={question}
                      type="button"
                      className="chat-suggestion"
                      onClick={() => selectQuestion(question)}
                    >
                      <span className="chat-suggestion-icon">
                        {["✧", "♧", "▤", "♛"][index]}
                      </span>

                      <span>{question}</span>
                    </button>
                  ))}

                </div>

              </div>
            )}

            {/* Barra para escribir mensajes */}
            <form
              className="chat-input-container"
              onSubmit={handleSubmit}
            >
              <input
                type="text"
                placeholder="Ask anything about Twilight..."
                value={message}
                onChange={(event) =>
                  setMessage(event.target.value)
                }
                aria-label="Your message"
              />

              <button
                type="submit"
                className="chat-send-button"
                aria-label="Send message"
                disabled={!message.trim() || isLoading}
              >
                ➤
              </button>
            </form>

          </>

        )}

      </section>

    </main>
  );
}
