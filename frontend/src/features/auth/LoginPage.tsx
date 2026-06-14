import { FormEvent, useState } from "react";

type LoginPageProps = {
  isSubmitting: boolean;
  error: string | null;
  onLogin: (username: string, password: string) => Promise<void>;
};

export function LoginPage({ isSubmitting, error, onLogin }: LoginPageProps) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onLogin(username, password);
  }

  return (
    <div className="auth-layout">
      <form className="login-form" onSubmit={handleSubmit}>
        <label className="field">
          <span>Usuario</span>
          <input
            autoComplete="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="admin"
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            autoComplete="current-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="admin123"
          />
        </label>

        <button className="primary-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Ingresando..." : "Ingresar"}
        </button>

        <p className="hint">Credenciales iniciales: admin / admin123</p>
        {error ? <p className="error-banner">{error}</p> : null}
      </form>
    </div>
  );
}
