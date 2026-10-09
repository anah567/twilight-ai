
import { useState } from "react";
import { loginUser, registerUser } from "../services/authService";
import "../styles/AuthPage.css";

// Icono para el correo electrónico
function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"
      aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </svg>
  );
}

// Icono para la contraseña
function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"
      aria-hidden="true">
      <rect x="4" y="10" width="16" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  );
}

// Icono para el nombre de usuario
function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"
      aria-hidden="true">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </svg>
  );
}

// Icono para mostrar u ocultar la contraseña
function EyeIcon({ hidden }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"
      aria-hidden="true">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
      <circle cx="12" cy="12" r="3" />
      {hidden && <path d="M3 3 21 21" />}
    </svg>
  );
}

export default function AuthPage({ onLogin }) {

  // Controlamos si el usuario está iniciando sesión o registrándose
  const [isRegistering, setIsRegistering] = useState(false);

  // Guardamos los datos escritos en el formulario
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  // Controlamos si la contraseña es visible
  const [showPassword, setShowPassword] = useState(false);

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

    // Limpiamos los mensajes al escribir nuevamente
    if (message) {
      setMessage("");
      setIsError(false);
    }
  };

  // Cambiamos entre inicio de sesión y registro
  const changeTab = (registering) => {
    setIsRegistering(registering);
    setMessage("");
    setIsError(false);
    setShowPassword(false);

    // Limpiamos la contraseña al cambiar de pestaña
    setForm((previous) => ({
      ...previous,
      password: "",
    }));
  };

  // Enviamos los datos al backend
  const handleSubmit = async (event) => {
    event.preventDefault();

    // Evitamos enviar el formulario varias veces
    if (isLoading) return;

    setMessage("");
    setIsError(false);
    setIsLoading(true);

    try {

      if (isRegistering) {

        // Registramos el nuevo usuario
        await registerUser(
          form.username,
          form.email,
          form.password
        );

        // Mostramos el formulario de inicio de sesión
        setIsRegistering(false);
        setShowPassword(false);

        // Limpiamos la contraseña después del registro
        setForm((previous) => ({
          ...previous,
          password: "",
        }));

        setMessage(
          "Account created successfully. Please sign in."
        );

      } else {

        // Iniciamos sesión con FastAPI
        const data = await loginUser(
          form.email,
          form.password
        );

        // Avisamos a App que el usuario inició sesión correctamente
        onLogin(data.access_token);

        // Limpiamos la contraseña del formulario
        setForm((previous) => ({
          ...previous,
          password: "",
        }));

        setMessage("Signed in successfully.");

        // Después conectaremos la navegación al chat
      }

    } catch (error) {

      // Mostramos un mensaje si el backend devuelve un error
      setIsError(true);
      setMessage(
        error.message || "Something went wrong. Please try again."
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

        {/* Pestañas de inicio de sesión y registro */}
        <div className="auth-tabs">

          <button
            type="button"
            className={!isRegistering ? "active" : ""}
            onClick={() => changeTab(false)}
            disabled={isLoading}
            aria-pressed={!isRegistering}
          >
            Sign in
          </button>

          <button
            type="button"
            className={isRegistering ? "active" : ""}
            onClick={() => changeTab(true)}
            disabled={isLoading}
            aria-pressed={isRegistering}
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

          <form onSubmit={handleSubmit}>

            {/* El nombre de usuario aparece solamente al registrarse */}
            {isRegistering && (
              <div className="auth-field">

                <label htmlFor="username">
                  Username
                </label>

                <div className="auth-input-wrapper">
                  <span className="auth-input-icon">
                    <UserIcon />
                  </span>

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
                    disabled={isLoading}
                    required
                  />
                </div>

              </div>
            )}

            {/* Campo de correo electrónico */}
            <div className="auth-field">

              <label htmlFor="email">
                Email address
              </label>

              <div className="auth-input-wrapper">

                <span className="auth-input-icon">
                  <MailIcon />
                </span>

                <input
                  id="email"
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={form.email}
                  onChange={handleChange}
                  autoComplete="email"
                  disabled={isLoading}
                  required
                />

              </div>

            </div>

            {/* Campo de contraseña */}
            <div className="auth-field">

              <label htmlFor="password">
                Password
              </label>

              <div className="auth-input-wrapper">

                <span className="auth-input-icon">
                  <LockIcon />
                </span>

                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
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
                  disabled={isLoading}
                  required
                />

                {/* Botón para mostrar u ocultar la contraseña */}
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                  aria-pressed={showPassword}
                >
                  <EyeIcon hidden={showPassword} />
                </button>

              </div>

            </div>

            {/* Botón principal con indicador de carga */}
            <button
              className="auth-submit"
              type="submit"
              disabled={isLoading}
            >

              {isLoading ? (
                <>
                  <span className="auth-spinner" aria-hidden="true" />
                  <span>
                    {isRegistering
                      ? "Creating account..."
                      : "Signing in..."}
                  </span>
                </>
              ) : (
                <>
                  <span>
                    {isRegistering
                      ? "Create account"
                      : "Sign in"}
                  </span>
                  <span aria-hidden="true">→</span>
                </>
              )}

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
              role={isError ? "alert" : "status"}
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
