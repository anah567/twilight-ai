
import "../styles/ChatHistory.css";

// Mostramos la fecha de cada conversación
function formatDate(value) {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

export default function ChatHistory({
  conversations,
  isLoading,
  error,
  onOpenConversation,
  onNewChat,
  activeConversationId,
}) {
  return (
    <div className="history-page">
      {/* Encabezado */}
      <div className="history-header">
        <span className="history-moon">☾</span>

        <h1>
          Your <span>Conversations</span>
        </h1>

        <p>
          Every story has a beginning. Revisit your
          conversations in the Twilight universe.
        </p>
      </div>

      {/* Cantidad de conversaciones */}
      <div className="history-summary">
        <span>✧ CONVERSATION HISTORY</span>

        <strong>
          {conversations.length}{" "}
          {conversations.length === 1
            ? "conversation"
            : "conversations"}
        </strong>
      </div>

      {/* Botón para iniciar una conversación */}
      <div className="history-actions">
        <button type="button" onClick={onNewChat}>
          <span>＋</span> New Conversation
        </button>
      </div>

      {/* Estado de carga */}
      {isLoading && (
        <p className="history-message">
          Loading conversations...
        </p>
      )}

      {/* Mensaje de error */}
      {!isLoading && error && (
        <p className="history-error" role="alert">
          {error}
        </p>
      )}

      {/* Cuando todavía no hay conversaciones */}
      {!isLoading && !error && conversations.length === 0 && (
        <div className="history-empty">
          <span>☾</span>

          <h2>Your story begins here</h2>

          <p>
            Start a conversation and explore the
            mysteries of Twilight.
          </p>

          <button type="button" onClick={onNewChat}>
            Start a Conversation
          </button>
        </div>
      )}

      {/* Conversaciones guardadas */}
      {!isLoading && !error && conversations.length > 0 && (
        <div className="history-grid">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              className={`history-card ${
                conversation.id === activeConversationId
                  ? "history-card-active"
                  : ""
              }`}
              onClick={() =>
                onOpenConversation(conversation.id)
              }
              title={conversation.title}
            >
              <div className="history-card-icon">
                <svg
                  width="22"
                  height="22"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H5l-2 2v-9.5A7.5 7.5 0 0 1 10.5 4h2A7.5 7.5 0 0 1 20 11.5Z" />
                </svg>
              </div>

              <div className="history-card-info">
                <h3>{conversation.title}</h3>

                <p>{formatDate(conversation.created_at)}</p>
              </div>

              <span className="history-card-arrow">→</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
