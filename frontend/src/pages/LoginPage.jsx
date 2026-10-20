import { useState } from "react";

import Notice from "../components/Notice.jsx";
import Wordmark from "../components/Wordmark.jsx";
import { useSession } from "../session.jsx";

// Solo se muestran en desarrollo (npm run dev), nunca en la imagen publicada.
const DEMO_USERS = [
  { label: "Alumna · Lucía", email: "alumno1@cafeteria.test", password: "alumno123" },
  { label: "Alumno · Martín", email: "alumno2@cafeteria.test", password: "alumno123" },
  { label: "Cafetería", email: "cafeteria@cafeteria.test", password: "cafeteria123" },
];

export default function LoginPage() {
  const { login } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [isSending, setIsSending] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSending(true);
    setError(null);

    try {
      await login(email.trim(), password);
    } catch (loginError) {
      setError(loginError.detail);
      setIsSending(false);
    }
  }

  return (
    <div className="login">
      <div className="login__intro">
        <Wordmark large />
        <p className="login__lede">
          Elegí lo que querés, decí en qué recreo lo pasás a buscar y <mark>salteate la fila</mark>.
        </p>
      </div>

      <form className="sheet login__form" onSubmit={handleSubmit}>
        <h1 className="sheet__title">Iniciar sesión</h1>

        <label className="field">
          <span className="field__label">Correo</span>
          <input
            type="email"
            autoComplete="username"
            inputMode="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>

        <label className="field">
          <span className="field__label">Contraseña</span>
          <input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>

        {error && <Notice tone="error">{error}</Notice>}

        <button type="submit" className="button button--ink button--block" disabled={isSending}>
          {isSending ? "Entrando…" : "Entrar"}
        </button>

        {import.meta.env.DEV && (
          <div className="demo-users">
            <p className="demo-users__title">Usuarios de prueba</p>
            {DEMO_USERS.map((demoUser) => (
              <button
                key={demoUser.email}
                type="button"
                className="chip"
                onClick={() => {
                  setEmail(demoUser.email);
                  setPassword(demoUser.password);
                }}
              >
                {demoUser.label}
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  );
}
