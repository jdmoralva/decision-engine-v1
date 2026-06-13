import { FormEvent, useEffect, useState } from "react";

import { ParametersPage } from "./features/engine-admin/ParametersPage";
import { PipelinePage } from "./features/engine-admin/PipelinePage";
import { ProductsPage } from "./features/engine-admin/ProductsPage";
import { RulesPage } from "./features/engine-admin/RulesPage";
import { VariablesPage } from "./features/engine-admin/VariablesPage";
import { WorkflowsPage } from "./features/engine-admin/WorkflowsPage";
import {
  emptyEngineAdminWorkspaceState,
  EngineAdminApiClient,
  type EngineAdminWorkspaceState,
} from "./services/engine-admin-api";
import {
  clearStoredSession,
  loadStoredSession,
  saveStoredSession,
  type SessionMe,
} from "./session-storage";


type LoginResult = {
  access_token: string;
  token_type: string;
};

type MeResult = {
  id: string;
  username: string;
  display_name: string | null;
  roles: string[];
};


function toSessionMe(me: MeResult): SessionMe {
  return {
    id: me.id,
    username: me.username,
    displayName: me.display_name,
    roles: me.roles,
  };
}


function App() {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [token, setToken] = useState<string | null>(null);
  const [me, setMe] = useState<SessionMe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);
  const [workspace, setWorkspace] = useState<EngineAdminWorkspaceState>(
    emptyEngineAdminWorkspaceState,
  );
  const [notice, setNotice] = useState<string | null>(null);
  const [activeAdminTab, setActiveAdminTab] = useState<
    "products" | "variables" | "parameters" | "pipeline" | "rules" | "workflows"
  >("products");

  useEffect(() => {
    let isMounted = true;

    async function restoreSession() {
      const storedSession = loadStoredSession();
      if (storedSession === null) {
        if (isMounted) {
          setIsRestoring(false);
        }
        return;
      }

      try {
        const meResponse = await fetch("/api/v1/me", {
          headers: {
            Authorization: `Bearer ${storedSession.accessToken}`,
          },
        });

        if (!meResponse.ok) {
          throw new Error("La sesion guardada ya no es valida.");
        }

        const mePayload = (await meResponse.json()) as MeResult;
        const normalizedMe = toSessionMe(mePayload);

        if (isMounted) {
          setToken(storedSession.accessToken);
          setMe(normalizedMe);
          saveStoredSession({ accessToken: storedSession.accessToken, me: normalizedMe });
        }
      } catch {
        clearStoredSession();
        if (isMounted) {
          setToken(null);
          setMe(null);
        }
      } finally {
        if (isMounted) {
          setIsRestoring(false);
        }
      }
    }

    void restoreSession();

    return () => {
      isMounted = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const loginResponse = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!loginResponse.ok) {
        throw new Error("Credenciales invalidas. Verifica usuario y password.");
      }

      const loginPayload = (await loginResponse.json()) as LoginResult;
      const meResponse = await fetch("/api/v1/me", {
        headers: {
          Authorization: `Bearer ${loginPayload.access_token}`,
        },
      });

      if (!meResponse.ok) {
        throw new Error("Login correcto, pero no se pudo recuperar la sesion.");
      }

      const mePayload = (await meResponse.json()) as MeResult;
      const normalizedMe = toSessionMe(mePayload);
      setToken(loginPayload.access_token);
      setMe(normalizedMe);
      saveStoredSession({ accessToken: loginPayload.access_token, me: normalizedMe });
    } catch (caughtError) {
      setToken(null);
      setMe(null);
      clearStoredSession();
      setError(
        caughtError instanceof Error ? caughtError.message : "Ocurrio un error inesperado.",
      );
      setNotice(null);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleResetSession() {
    clearStoredSession();
    setToken(null);
    setMe(null);
    setError(null);
    setNotice(null);
    setPassword("admin123");
  }

  const adminClient = token ? new EngineAdminApiClient(token) : null;
  const canManageEngine = me !== null && me.roles.some((role) => role.startsWith("admin"));

  function renderAdminTab() {
    if (adminClient === null) {
      return null;
    }

    const sharedProps = {
      client: adminClient,
      workspace,
      onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) =>
        setWorkspace((current) => ({ ...current, ...patch })),
      onNotice: setNotice,
    };

    switch (activeAdminTab) {
      case "products":
        return <ProductsPage {...sharedProps} />;
      case "variables":
        return <VariablesPage {...sharedProps} />;
      case "parameters":
        return <ParametersPage {...sharedProps} />;
      case "pipeline":
        return <PipelinePage {...sharedProps} />;
      case "rules":
        return <RulesPage {...sharedProps} />;
      case "workflows":
        return <WorkflowsPage {...sharedProps} />;
    }
  }

  return (
    <main className="shell">
      <section className="card auth-card">
        <div className="auth-hero">
          <p className="eyebrow">Decision Engine</p>
          <h1>Inicio de sesion</h1>
          <p className="lead">
            Prueba el acceso real con el usuario administrador sembrado en la base local.
          </p>
        </div>

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

          <aside className="session-panel">
            <h2>Estado de sesion</h2>

            {isRestoring ? <p className="session-empty">Restaurando sesion...</p> : null}

            {!isRestoring && me ? (
              <>
                <p className="success-banner">Acceso correcto.</p>
                <dl className="session-grid">
                  <div>
                    <dt>Usuario</dt>
                    <dd>{me.username}</dd>
                  </div>
                  <div>
                    <dt>Nombre</dt>
                    <dd>{me.displayName ?? "Sin nombre"}</dd>
                  </div>
                  <div>
                    <dt>Roles</dt>
                    <dd>{me.roles.join(", ")}</dd>
                  </div>
                  <div>
                    <dt>Token</dt>
                    <dd className="token-preview">{token}</dd>
                  </div>
                </dl>
                <button className="secondary-button" type="button" onClick={handleResetSession}>
                  Limpiar sesion
                </button>
              </>
            ) : null}

            {!isRestoring && !me ? (
              <p className="session-empty">
                Aun no hay una sesion activa. Usa el formulario para autenticarte.
              </p>
            ) : null}
          </aside>
        </div>

        <ul className="feature-list">
          <li>Consulta y evaluacion PLD</li>
          <li>Bandeja y solicitudes</li>
          <li>Adjuntos ZIP</li>
          <li>Paneles AI asistivos</li>
        </ul>

        {canManageEngine ? (
          <section className="admin-shell">
            <div className="admin-shell-header">
              <div>
                <p className="eyebrow">Motor administrable</p>
                <h2>Phase 3</h2>
              </div>
              <p className="workspace-hint">
                Producto: {workspace.productCode} | Workflow: {workspace.workflowCode}
              </p>
            </div>

            <div className="tab-strip">
              <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("products")}>Productos</button>
              <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("variables")}>Variables</button>
              <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("parameters")}>Parametros</button>
              <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("pipeline")}>Pipeline</button>
              <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("rules")}>Reglas</button>
              <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("workflows")}>Versionado</button>
            </div>

            {notice ? <p className="success-banner">{notice}</p> : null}
            {renderAdminTab()}
          </section>
        ) : null}
      </section>
    </main>
  );
}

export default App;
