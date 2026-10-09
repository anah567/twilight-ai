
import { useState } from "react";
import { loginUser, registerUser } from "../services/authService";
import "../styles/AuthPage.css";

export default function AuthPage() {

  // Controlamos si el usuario está iniciando sesión o registrándose
  const [isRegistering, setIsRegistering] = useState(false);

  // Guardamos los datos escritos en el formulario
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  // Guardamos los mensajes de éxito o error
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  // Indicamos si estamos esperando la respuesta del backend
  const [isLoading, setIsLoading] = useState(false);

  // Actualizamos los campos del formulario
  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  // Cambiamos entre iniciar sesión y crear cuenta
  const changeTab = (registering) => {

    // Actualizamos la pestaña seleccionada
    setIsRegistering(registering);

    // Limpiamos los mensajes anteriores
    setMessage("");
    setIsError(false);

    // Limpiamos la contraseña al cambiar de pestaña
    setForm((previous) => ({
      ...previous,
      password: "",
    }));
  };

  // Enviamos los datos al backend
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Limpiamos los mensajes anteriores
    setMessage("");
    setIsError(false);
    setIsLoading(true);

    try {

      if (isRegistering) {

        // Registramos un usuario nuevo
        await registerUser(
          form.username,
          form.email,
          form.password
        );

        // Cambiamos al formulario de inicio de sesión
        setIsRegistering(false);

        // Limpiamos la contraseña
        setForm((previous) => ({
          ...previous,
          password: "",
        }));

        // Mostramos un mensaje de éxito
        setMessage(
          "Account created successfully. Please sign in."
        );

      } else {

        // Iniciamos sesión utilizando nuestro backend
        const data = await loginUser(
          form.email,
          form.password
        );

        // Guardamos el token para las siguientes solicitudes
        sessionStorage.setItem(
          "twilight_token",
          data.access_token
        );

        // Mostramos un mensaje de éxito
        setMessage("Signed in successfully.");

        // Después conectaremos la navegación hacia el chat
      }

    } catch (error) {

      // Mostramos el mensaje del error
      setIsError(true);
      setMessage(
        error.message || "Something went wrong."
      );

    } finally {

      // Finalizamos el estado de carga
      setIsLoading(false);
    }
  };

  return (
    <main className="auth-page">

      {/* Sección izquierda: presentación de Twilight AI */}
      <section className="auth-intro">

        <h1>
          Twilight <span>AI</span>
        </h1>

        <div className="auth-decoration">
          <span>☾</span>
        </div>

        <p className="auth-tagline">
          EXPLORE ✦ ASK ✦ DISCOVER
        </p>

        <p className="auth-description">
          Your guide to the world of Twilight.
          <br />
          Ask questions, discover stories,
          characters, places, and more.
        </p>

      </section>

      {/* Sección derecha: formulario de autenticación */}
      <section className="auth-card">

        {/* Pestañas para iniciar sesión o registrarse */}
        <div className="auth-tabs">

          <button
            type="button"
            className={!isRegistering ? "active" : ""}
            onClick={() => changeTab(false)}
            disabled={isLoading}
          >
            Sign in
          </button>

          <button
            type="button"
            className={isRegistering ? "active" : ""}
            onClick={() => changeTab(true)}
            disabled={isLoading}
          >
            Sign up
          </button>

        </div>

        <div className="auth-card-content">

          <h2>
            {isRegistering
              ? "Join Twilight AI"
              : "Welcome back"}
          </h2>

          <p className="auth-subtitle">
            {isRegistering
              ? "Begin your journey into the Twilight universe"
              : "Continue your journey into the Twilight universe"}
          </p>

          {/* Formulario conectado con FastAPI */}
          <form onSubmit={handleSubmit}>

            {/* El nombre de usuario solo aparece al registrarse */}
            {isRegistering && (
              <div className="auth-field">

                <label htmlFor="username">
                  Username
                </label>

                <input
                  id="username"
                  type="text"
                  name="username"
                  placeholder="Enter your username"
                  value={form.username}
                  onChange={handleChange}
                  minLength={3}
                  maxLength={50}
                  autoComplete="username"
                  required
                />

              </div>
            )}

            {/* Campo de correo electrónico */}
            <div className="auth-field">

              <label htmlFor="email">
                Email address
              </label>

              <input
                id="email"
                type="email"
                name="email"
                placeholder="Enter your email"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
                required
              />

            </div>

            {/* Campo de contraseña */}
            <div className="auth-field">

              <label htmlFor="password">
                Password
              </label>

              <input
                id="password"
                type="password"
                name="password"
                placeholder="Enter your password"
                value={form.password}
                onChange={handleChange}
                minLength={8}
                autoComplete={
                  isRegistering
                    ? "new-password"
                    : "current-password"
                }
                required
              />

            </div>

            {/* Botón para enviar los datos */}
            <button
              className="auth-submit"
              type="submit"
              disabled={isLoading}
            >

              {isLoading
                ? "Please wait..."
                : isRegistering
                  ? "Create account"
                  : "Sign in"}

              <span>→</span>

            </button>

          </form>

          {/* Mensajes de éxito o error */}
          {message && (
            <p
              className={`auth-message ${
                isError
                  ? "auth-message-error"
                  : "auth-message-success"
              }`}
              role="status"
            >
              {message}
            </p>
          )}

          <p className="auth-footer">
            A journey beyond the ordinary ✦
          </p>

        </div>

      </section>

    </main>
  );
}
