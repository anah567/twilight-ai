import { useEffect, useRef, useState } from "react";

import { sendMessage } from "../services/chatService";
import {
    getConversations,
    getConversationById,
} from "../services/conversationService";

import DocumentLibrary from "./DocumentLibrary";
import ChatHistory from "./ChatHistory";
import "../styles/ChatPage.css";

// Preguntas que aparecen al iniciar el chat
const suggestedQuestions = [
    "Who is Edward Cullen?",
    "What makes the Cullen family different?",
    "Tell me about Bella Swan.",
    "What is the history of the Volturi?",
];

// Iconos que usamos en el chat
function Icon({ name, size = 19, ...props }) {
    const paths = {
        plus: <path d="M12 5v14M5 12h14" />,

        history: (
            <>
                <path d="M3 12a9 9 0 1 0 3-6.7" />
                <path d="M3 4v4h4M12 7v5l3 2" />
            </>
        ),

        document: (
            <>
                <path d="M7 3h7l5 5v13H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
                <path d="M14 3v6h5M9 13h6M9 17h6" />
            </>
        ),

        conversation: (
            <path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H5l-2 2v-9.5A7.5 7.5 0 0 1 10.5 4h2A7.5 7.5 0 0 1 20 11.5Z" />
        ),

        logout: (
            <>
                <path d="M9 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3" />
                <path d="M13 8l4 4-4 4M8 12h9" />
            </>
        ),

        arrow: (
            <>
                <path d="M5 12h14M13 6l6 6-6 6" />
            </>
        ),

        send: (
            <>
                <path d="m4 12 16-8-5 16-3-7-8-1Z" />
                <path d="m12 13 8-9" />
            </>
        ),
    };

    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.7"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            {...props}
        >
            {paths[name]}
        </svg>
    );
}

// Muestra la fecha de cada conversación
function formatConversationDate(value) {
    if (!value) return "";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "";

    return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(date);
}

// Muestra las fuentes si el backend las envía
function Sources({ sources }) {
    if (!Array.isArray(sources) || sources.length === 0) {
        return null;
    }

    return (
        <div className="chat-sources">
            <span className="chat-sources-label">Sources</span>

            <div className="chat-sources-list">
                {sources.map((source, index) => {
                    const label =
                        typeof source === "string"
                            ? source
                            : source?.filename ||
                            source?.title ||
                            source?.name ||
                            source?.document_id;

                    if (!label) return null;

                    return (
                        <span
                            className="chat-source"
                            key={`${label}-${index}`}
                        >
                            {label}
                        </span>
                    );
                })}
            </div>
        </div>
    );
}

export default function ChatPage({ onLogout, user = null }) {
    // Texto que escribe el usuario
    const [message, setMessage] = useState("");

    // Mensajes de la conversación
    const [messages, setMessages] = useState([]);

    // Conversación que está abierta
    const [conversationId, setConversationId] = useState(null);

    // Indica si la IA está respondiendo
    const [isLoading, setIsLoading] = useState(false);

    // Errores del chat
    const [chatError, setChatError] = useState("");

    // Conversaciones guardadas
    const [conversations, setConversations] = useState([]);

    // Indica si se está cargando el historial
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);

    // Errores del historial
    const [historyError, setHistoryError] = useState("");

    // Pantalla que estamos mostrando
    const [activeView, setActiveView] = useState("chat");

    // Referencias para el scroll y el campo de texto
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Nombre que aparece en el perfil
    const displayName =
        typeof user?.username === "string" && user.username.trim()
            ? user.username.trim()
            : typeof user?.name === "string" && user.name.trim()
                ? user.name.trim()
                : "Twilight Explorer";

    // Cargamos las conversaciones al entrar
    useEffect(() => {
        let mounted = true;

        getConversations()
            .then((data) => {
                if (!mounted) return;

                setConversations(data);
                setHistoryError("");
            })
            .catch((error) => {
                if (!mounted) return;

                setHistoryError(
                    error.message || "Unable to load conversations."
                );
            })
            .finally(() => {
                if (mounted) {
                    setIsLoadingHistory(false);
                }
            });

        return () => {
            mounted = false;
        };
    }, []);

    // Bajamos hasta el último mensaje
    useEffect(() => {
        if (activeView === "chat" && messages.length > 0) {
            messagesEndRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "end",
            });
        }
    }, [messages, isLoading, activeView]);

    // Abrimos una conversación del historial
    const handleOpenConversation = async (id) => {
        if (isLoading || isLoadingHistory) return;

        setIsLoadingHistory(true);
        setChatError("");

        try {
            const data = await getConversationById(id);

            setMessages(data.messages);
            setConversationId(data.id);
            setMessage("");
            setActiveView("chat");
        } catch (error) {
            setChatError(
                error.message || "Unable to open conversation."
            );

            setActiveView("chat");
        } finally {
            setIsLoadingHistory(false);
        }
    };

    // Empezamos una conversación nueva
    const handleNewChat = () => {
        if (isLoading || isLoadingHistory) return;

        setActiveView("chat");
        setMessages([]);
        setConversationId(null);
        setMessage("");
        setChatError("");

        inputRef.current?.focus();
    };

    // Enviamos la pregunta a FastAPI
    const handleSubmit = async (event) => {
        event.preventDefault();

        const question = message.trim();

        if (!question || isLoading || isLoadingHistory) {
            return;
        }

        // Mostramos la pregunta del usuario
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
            // Pedimos la respuesta al agente
            const data = await sendMessage(question, conversationId);

            setConversationId(data.conversation_id);

            // Agregamos la respuesta al chat
            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: data.answer,
                    ...(Array.isArray(data.sources)
                        ? { sources: data.sources }
                        : {}),
                },
            ]);

            // Actualizamos las conversaciones recientes
            try {
                const updated = await getConversations();

                setConversations(updated);
                setHistoryError("");
            } catch (error) {
                setHistoryError(
                    error.message || "Unable to refresh conversations."
                );
            }
        } catch (error) {
            setChatError(
                error.message || "Unable to get a response."
            );
        } finally {
            setIsLoading(false);
        }
    };

    // Ponemos una pregunta sugerida en el campo de texto
    const selectQuestion = (question) => {
        setMessage(question);
        inputRef.current?.focus();
    };

    return (
        <main className="chat-page">
            {/* Menú lateral */}
            <aside className="chat-sidebar">
                {/* Logo */}
                <div className="chat-brand">
                    <h2>
                        Twilight <span>AI</span>
                    </h2>

                    <div className="chat-brand-decoration">
                        <span>☾</span>
                    </div>
                </div>

                {/* Nueva conversación */}
                <button
                    className="new-chat-button"
                    type="button"
                    onClick={handleNewChat}
                    disabled={isLoading || isLoadingHistory}
                >
                    <Icon name="plus" size={19} />
                    <span>New Chat</span>
                </button>

                {/* Opciones del menú */}
                <nav
                    className="chat-navigation"
                    aria-label="Main navigation"
                >
                    <button
                        type="button"
                        className={
                            activeView === "history" ? "chat-nav-active" : ""
                        }
                        aria-current={
                            activeView === "history" ? "page" : undefined
                        }
                        onClick={() => setActiveView("history")}
                    >
                        <Icon name="history" size={18} />
                        <span>Chat History</span>
                    </button>

                    <button
                        type="button"
                        className={
                            activeView === "documents" ? "chat-nav-active" : ""
                        }
                        aria-current={
                            activeView === "documents" ? "page" : undefined
                        }
                        onClick={() => setActiveView("documents")}
                    >
                        <Icon name="document" size={18} />
                        <span>Document Library</span>
                    </button>
                </nav>

                <div className="chat-sidebar-divider" />

                {/* Historial de conversaciones */}
                <div className="chat-history-section">
                    <p className="chat-section-title">
                        RECENT CONVERSATIONS
                    </p>

                    {/* Mensaje mientras carga el historial */}
                    {isLoadingHistory && (
                        <p className="chat-empty-history">
                            Loading conversations...
                        </p>
                    )}

                    {/* Error al cargar el historial */}
                    {!isLoadingHistory && historyError && (
                        <p
                            className="chat-empty-history"
                            role="alert"
                        >
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
                            {conversations.map((conversation) => {
                                const isActive =
                                    conversationId === conversation.id;

                                const formattedDate =
                                    formatConversationDate(
                                        conversation.created_at
                                    );

                                return (
                                    <button
                                        key={conversation.id}
                                        type="button"
                                        className={`chat-conversation-item ${isActive
                                            ? "chat-conversation-active"
                                            : ""
                                            }`}
                                        onClick={() =>
                                            handleOpenConversation(conversation.id)
                                        }
                                        disabled={
                                            isLoading || isLoadingHistory
                                        }
                                        title={conversation.title}
                                        aria-current={
                                            isActive ? "true" : undefined
                                        }
                                    >
                                        {/* Icono de conversación */}
                                        <span className="chat-conversation-icon">
                                            <Icon
                                                name="conversation"
                                                size={16}
                                            />
                                        </span>

                                        {/* Título y fecha */}
                                        <span className="chat-conversation-details">
                                            <span className="chat-conversation-title">
                                                {conversation.title}
                                            </span>

                                            {formattedDate && (
                                                <span className="chat-conversation-date">
                                                    {formattedDate}
                                                </span>
                                            )}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Perfil del usuario */}
                <div className="chat-sidebar-bottom">
                    <div className="chat-profile">
                        <div className="chat-avatar">☾</div>

                        <div className="chat-profile-info">
                            <strong title={displayName}>
                                {displayName}
                            </strong>

                            <span>Your account</span>
                        </div>
                    </div>

                    {/* Cerrar sesión */}
                    <button
                        className="chat-logout"
                        type="button"
                        onClick={onLogout}
                    >
                        <Icon name="logout" size={18} />
                        <span>Log out</span>
                    </button>
                </div>
            </aside>

            {/* Contenido principal */}
            <section className="chat-main">
                {activeView === "documents" ? (
                    <DocumentLibrary
                        onBack={() => setActiveView("chat")}
                    />
                ) : activeView === "history" ? (
                    <ChatHistory
                        conversations={conversations}
                        isLoading={isLoadingHistory}
                        error={historyError}
                        onOpenConversation={handleOpenConversation}
                        onNewChat={handleNewChat}
                        activeConversationId={conversationId}
                    />
                ) : (
                    <>
                        {/* Mensajes del chat */}
                        {messages.length > 0 && (
                            <div
                                className="chat-messages"
                                aria-label="Conversation messages"
                                aria-live="polite"
                            >
                                {messages.map((item, index) => (
                                    <div
                                        key={item.id ?? index}
                                        className={`chat-message ${item.role === "user"
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

                                        {/* Fuentes de la respuesta */}
                                        {item.role === "assistant" && (
                                            <Sources sources={item.sources} />
                                        )}
                                    </div>
                                ))}

                                {/* Animación mientras responde la IA */}
                                {isLoading && (
                                    <div
                                        className="chat-message chat-message-assistant"
                                        role="status"
                                        aria-label="Twilight AI is thinking"
                                    >
                                        <span className="chat-message-role">
                                            Twilight AI
                                        </span>

                                        <div className="chat-thinking">
                                            <span />
                                            <span />
                                            <span />
                                            <span className="chat-thinking-text">
                                                Thinking...
                                            </span>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
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
                                    {suggestedQuestions.map((question) => (
                                        <button
                                            key={question}
                                            type="button"
                                            className="chat-suggestion"
                                            onClick={() =>
                                                selectQuestion(question)
                                            }
                                        >
                                            <span className="chat-suggestion-text">
                                                {question}
                                            </span>

                                            <Icon
                                                name="arrow"
                                                size={17}
                                                className="chat-suggestion-arrow"
                                            />
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Campo para escribir mensajes */}
                        <form
                            className="chat-input-container"
                            onSubmit={handleSubmit}
                        >
                            <input
                                ref={inputRef}
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
                                disabled={
                                    !message.trim() ||
                                    isLoading ||
                                    isLoadingHistory
                                }
                            >
                                <Icon name="send" size={21} />
                            </button>
                        </form>
                    </>
                )}
            </section>
        </main>
    );
}