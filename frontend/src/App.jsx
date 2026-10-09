
import { useEffect, useState } from "react";
import AuthPage from "./pages/AuthPage";
import ChatPage from "./pages/ChatPage";

export default function App() {

  // Comprobamos si existe una sesión guardada en esta pestaña
  const [token, setToken] = useState(() => {
    return sessionStorage.getItem("twilight_token");
  });

  // Guardamos la información del usuario autenticado
  const [user, setUser] = useState(null);

  // Indicamos si estamos consultando los datos del usuario
  const [isLoadingUser, setIsLoadingUser] = useState(false);

  // Consultamos el perfil cuando tenemos una sesión
  useEffect(() => {

    // Si no hay token, no necesitamos consultar el perfil
    if (!token) {
      setUser(null);
      setIsLoadingUser(false);
      return;
    }

    // Evitamos actualizar la pantalla si cambia la sesión
    const controller = new AbortController();

    const loadUser = async () => {
      setIsLoadingUser(true);
      setUser(null);

      try {

        // Pedimos los datos del usuario al backend
        const response = await fetch(
          "http://127.0.0.1:8000/auth/me",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            signal: controller.signal,
          }
        );

        // Si el token venció, cerramos la sesión
        if (response.status === 401 || response.status === 403) {
          sessionStorage.removeItem("twilight_token");
          setToken(null);
          return;
        }

        // Verificamos que la solicitud haya funcionado
        if (!response.ok) {
          throw new Error("Unable to load your profile.");
        }

        // Guardamos los datos del usuario
        const data = await response.json();
        setUser(data);

      } catch (error) {

        // Ignoramos las solicitudes que fueron canceladas
        if (error.name !== "AbortError") {
          console.error("Error loading user profile:", error);
        }

      } finally {

        // Terminamos la carga si la solicitud sigue activa
        if (!controller.signal.aborted) {
          setIsLoadingUser(false);
        }
      }
    };

    loadUser();

    // Cancelamos la solicitud si cambia la sesión
    return () => controller.abort();

  }, [token]);

  // Escuchamos cuando alguna solicitud detecta una sesión vencida
  useEffect(() => {

    const handleSessionExpired = () => {

      // Eliminamos el token y regresamos al login
      sessionStorage.removeItem("twilight_token");
      setToken(null);
      setUser(null);
    };

    window.addEventListener(
      "twilight:session-expired",
      handleSessionExpired
    );

    // Quitamos el evento cuando ya no se necesita
    return () => {
      window.removeEventListener(
        "twilight:session-expired",
        handleSessionExpired
      );
    };

  }, []);

  // Guardamos la sesión cuando el usuario inicia sesión
  const handleLogin = (accessToken) => {
    sessionStorage.setItem("twilight_token", accessToken);
    setToken(accessToken);
  };

  // Eliminamos la sesión cuando el usuario cierra sesión
  const handleLogout = () => {
    sessionStorage.removeItem("twilight_token");
    setToken(null);
    setUser(null);
  };

  // Mostramos una pantalla sencilla mientras carga el perfil
  if (token && isLoadingUser) {
    return (
      <main className="chat-page">
        <section className="chat-main">
          <p>Entering the Twilight universe...</p>
        </section>
      </main>
    );
  }

  // Mostramos el chat cuando existe una sesión
  if (token) {
    return (
      <ChatPage
        onLogout={handleLogout}
        user={user}
      />
    );
  }

  // Mostramos el login cuando no existe una sesión
  return <AuthPage onLogin={handleLogin} />;
}
