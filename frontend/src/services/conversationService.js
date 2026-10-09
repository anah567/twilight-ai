
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Obtenemos las conversaciones guardadas del usuario
export async function getConversations() {
  const token = sessionStorage.getItem("twilight_token");

  if (!token) {
    throw new Error("Please sign in to view your conversations.");
  }

  const response = await fetch(`${API_URL}/conversations`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to load conversations."
    );
  }

  return data;
}

// Obtenemos los mensajes de una conversación específica
export async function getConversationById(conversationId) {
  const token = sessionStorage.getItem("twilight_token");

  if (!token) {
    throw new Error("Please sign in to view this conversation.");
  }

  const response = await fetch(
    `${API_URL}/conversations/${conversationId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to load this conversation."
    );
  }

  return data;
}
