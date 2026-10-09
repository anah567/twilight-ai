
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Enviamos una pregunta al agente de Twilight AI
export async function sendMessage(message, conversationId = null) {

    // Recuperamos el token del usuario autenticado
    const token = sessionStorage.getItem("twilight_token");

    // Comprobamos que exista una sesión
    if (!token) {
        window.dispatchEvent(new Event("twilight:session-expired"));
        throw new Error("Your session has expired. Please sign in again.");
    }

    // Enviamos la pregunta al backend
    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },

        // Enviamos los datos con los nombres que espera FastAPI
        body: JSON.stringify({
            question: message,
            conversation_id: conversationId,
        }),
    });

    // Leemos la respuesta del servidor
    const data = await response.json();

    // Mostramos un error si la solicitud falla
    if (!response.ok) {

        // Si el token venció, avisamos a React
        if (response.status === 401) {
            window.dispatchEvent(new Event("twilight:session-expired"));

            throw new Error(
                "Your session has expired. Please sign in again."
            );
        }

        // Mostramos los demás errores del backend
        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Unable to send your message."
        );
    }

    // Devolvemos la respuesta del agente
    return data;
}
