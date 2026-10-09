
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";


// MANEJO DE LA SESIÓN

// Avisamos a React cuando la sesión ya no es válida
function handleExpiredSession() {

  // App.jsx recibirá este aviso y regresará al login
  window.dispatchEvent(new Event("twilight:session-expired"));
}


// Obtenemos el token del usuario autenticado
function getAuthHeaders() {

  // Recuperamos el token guardado al iniciar sesión
  const token = sessionStorage.getItem("twilight_token");

  // Si no existe un token, avisamos que la sesión terminó
  if (!token) {
    handleExpiredSession();

    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }

  // Enviamos el token para identificarnos ante FastAPI
  return {
    Authorization: `Bearer ${token}`,
  };
}


// Revisamos si una solicitud falló
async function checkResponse(response, errorMessage) {

  // Si el backend respondió correctamente, continuamos
  if (response.ok) {
    return;
  }

  // Si el token venció, avisamos para cerrar la sesión
  if (response.status === 401) {
    handleExpiredSession();

    throw new Error(
      "Your session has expired. Please sign in again."
    );
  }

  // Si el usuario no es administrador, mostramos el error
  if (response.status === 403) {
    throw new Error("Administrator access is required.");
  }

  // Intentamos leer el mensaje de error del backend
  const data = await response.json().catch(() => null);

  // Mostramos el error recibido o un mensaje general
  throw new Error(
    typeof data?.detail === "string"
      ? data.detail
      : errorMessage
  );
}


// CONSULTAR DOCUMENTOS

// Obtenemos los documentos registrados en FastAPI
export async function getDocuments() {

  // Consultamos la biblioteca de documentos
  const response = await fetch(`${API_URL}/documents/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  // Comprobamos si la solicitud funcionó
  await checkResponse(response, "Unable to load documents.");

  // Devolvemos la lista de documentos
  return response.json();
}


// SUBIR DOCUMENTOS

// Subimos un archivo de texto al sistema RAG
export async function uploadDocument(file) {

  // Preparamos el archivo para enviarlo al backend
  const formData = new FormData();

  // El nombre "file" debe coincidir con el que espera FastAPI
  formData.append("file", file);

  // Enviamos el archivo al servidor
  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  // Comprobamos si ocurrió algún error
  await checkResponse(response, "Unable to upload document.");

  // Devolvemos el resultado de la carga
  return response.json();
}


// ELIMINAR DOCUMENTOS

// Eliminamos un documento utilizando su identificador
export async function deleteDocument(documentId) {

  // Enviamos la solicitud para eliminar el documento
  const response = await fetch(
    `${API_URL}/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  // Comprobamos si la eliminación funcionó
  await checkResponse(response, "Unable to delete document.");

  // Algunos endpoints DELETE no devuelven información
  if (response.status === 204) {
    return null;
  }

  // Devolvemos la respuesta si el backend envió contenido
  return response.json();
}
