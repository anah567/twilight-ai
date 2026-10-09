
import { useState } from "react";
import AuthPage from "./pages/AuthPage";
import ChatPage from "./pages/ChatPage";

export default function App() {

  // Comprobamos si existe una sesión guardada en esta pestaña
  const [token, setToken] = useState(() => {
    return sessionStorage.getItem("twilight_token");
  });

  // Guardamos la sesión cuando el usuario inicia sesión
  const handleLogin = (accessToken) => {
    sessionStorage.setItem("twilight_token", accessToken);
    setToken(accessToken);
  };

  // Eliminamos la sesión cuando el usuario cierra sesión
  const handleLogout = () => {
    sessionStorage.removeItem("twilight_token");
    setToken(null);
  };

  // Mostramos el chat cuando existe una sesión
  if (token) {
    return <ChatPage onLogout={handleLogout} />;
  }

  // Mostramos el login cuando no existe una sesión
  return <AuthPage onLogin={handleLogin} />;
}
