
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Obtenemos el token del usuario autenticado
function getAuthHeaders() {
  const token = sessionStorage.getItem("twilight_token");

  if (!token) {
    throw new Error("Please sign in to access the document library.");
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

// Consultamos los documentos registrados en FastAPI
export async function getDocuments() {
  const response = await fetch(`${API_URL}/documents/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  const data = await response.json();

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error("Administrator access is required.");
    }

    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to load documents."
    );
  }

  return data;
}

// Subimos un documento al sistema RAG
export async function uploadDocument(file) {
  const formData = new FormData();

  // El campo debe coincidir con el definido en FastAPI
  formData.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to upload document."
    );
  }

  return data;
}

// Eliminamos un documento por su identificador
export async function deleteDocument(documentId) {
  const response = await fetch(
    `${API_URL}/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  if (!response.ok) {
    const data = await response.json();

    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to delete document."
    );
  }

  // Algunos endpoints DELETE no devuelven contenido
  if (response.status === 204) {
    return null;
  }

  return response.json();
}
