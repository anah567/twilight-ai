
// Dirección de nuestro backend FastAPI
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// Función para iniciar sesión
export async function loginUser(email, password) {

  // Enviamos los datos al backend
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  // Convertimos la respuesta a JSON
  const data = await response.json();

  // Verificamos si ocurrió un error
  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to sign in."
    );
  }

  // Devolvemos el token de autenticación
  return data;
}

// Función para registrar un usuario
export async function registerUser(username, email, password) {

  // Enviamos los datos del nuevo usuario al backend
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      email,
      password,
    }),
  });

  // Convertimos la respuesta a JSON
  const data = await response.json();

  // Verificamos si ocurrió un error
  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to create account."
    );
  }

  // Devolvemos los datos del usuario registrado
  return data;
}
