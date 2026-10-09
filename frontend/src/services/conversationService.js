
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Avisamos a la aplicación cuando la sesión ya no es válida
function handleExpiredSession() {

  // Enviamos un aviso para que App.jsx regrese al login
  window.dispatchEvent(new Event("twilight:session-expired"));
}

// OBTENER TODAS LAS CONVERSACIONES

// Consultamos las conversaciones guardadas del usuario
export async function getConversations() {

  // Recuperamos el token que guardamos al iniciar sesión
  const token = sessionStorage.getItem("twilight_token");

  // Si no hay token, no podemos consultar las conversaciones
  if (!token) {
    handleExpiredSession();

    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }

  // Pedimos al backend las conversaciones del usuario
  const response = await fetch(`${API_URL}/conversations`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  // Convertimos la respuesta del backend a un objeto de JavaScript
  const data = await response.json();

  // Comprobamos si ocurrió algún error
  if (!response.ok) {

    // Si el token venció, avisamos para cerrar la sesión
    if (response.status === 401) {
      handleExpiredSession();

      throw new Error(
        "Your session has expired. Please sign in again."
      );
    }

    // Mostramos cualquier otro error del backend
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to load conversations."
    );
  }

  // Devolvemos las conversaciones para mostrarlas en React
  return data;
}


// OBTENER UNA CONVERSACIÓN ESPECÍFICA

// Consultamos los mensajes de una conversación guardada
export async function getConversationById(conversationId) {

  // Recuperamos el token del usuario autenticado
  const token = sessionStorage.getItem("twilight_token");

  // Comprobamos que exista una sesión
  if (!token) {
    handleExpiredSession();

    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }

  // Pedimos al backend la conversación que seleccionamos
  const response = await fetch(
    `${API_URL}/conversations/${conversationId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  // Convertimos la respuesta a un objeto de JavaScript
  const data = await response.json();

  // Comprobamos si la solicitud falló
  if (!response.ok) {

    // Si el token ya no es válido, cerramos la sesión
    if (response.status === 401) {
      handleExpiredSession();

      throw new Error(
        "Your session has expired. Please sign in again."
      );
    }

    // Mostramos los demás errores que pueda devolver el backend
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to load this conversation."
    );
  }

  // Devolvemos la conversación con todos sus mensajes
  return data;
}
