import { useEffect, useState } from "react";

import { AuthApiClient } from "./features/auth/auth-service";
import { LoginPage } from "./features/auth/LoginPage";
import { ParametersPage } from "./features/engine-admin/ParametersPage";
import { PipelinePage } from "./features/engine-admin/PipelinePage";
import { ProfilePermissionsPage } from "./features/engine-admin/ProfilePermissionsPage";
import { ProductsPage } from "./features/engine-admin/ProductsPage";
import { RulesPage } from "./features/engine-admin/RulesPage";
import { VariablesPage } from "./features/engine-admin/VariablesPage";
import { WorkflowsPage } from "./features/engine-admin/WorkflowsPage";
import { CreditRequestPage } from "./features/credit-requests/CreditRequestPage";
import { QueuePage } from "./features/credit-requests/QueuePage";
import { EvaluationPage } from "./features/evaluations/EvaluationPage";
import { ConsultationPage } from "./features/loan-consultations/ConsultationPage";
import { AttachmentsApiClient } from "./services/attachments-api";
import { AuditApiClient } from "./services/audit-api";
import { CreditRequestsApiClient } from "./services/credit-requests-api";
import {
  emptyEngineAdminWorkspaceState,
  EngineAdminApiClient,
  type EngineAdminWorkspaceState,
} from "./services/engine-admin-api";
import {
  RuntimeApiClient,
  type ConsultationResponse,
  type EvaluationResponse,
} from "./services/runtime-api";
import {
  clearStoredSession,
  loadStoredSession,
  saveStoredSession,
  type SessionMe,
} from "./session-storage";

type AppRoute = "consultas" | "evaluaciones" | "solicitudes" | "admin";

function readRoute(): AppRoute {
  const hash = window.location.hash.replace(/^#\/?/, "");
  if (hash === "evaluaciones") {
    return "evaluaciones";
  }
  if (hash === "admin") {
    return "admin";
  }
  if (hash === "solicitudes") {
    return "solicitudes";
  }
  return "consultas";
}

function App() {
  const [token, setToken] = useState<string | null>(null);
  const [me, setMe] = useState<SessionMe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRestoring, setIsRestoring] = useState(true);
  const [route, setRoute] = useState<AppRoute>(readRoute());
  const [lastConsultation, setLastConsultation] = useState<ConsultationResponse | null>(null);
  const [lastEvaluation, setLastEvaluation] = useState<EvaluationResponse | null>(null);
  const [workspace, setWorkspace] = useState<EngineAdminWorkspaceState>(
    emptyEngineAdminWorkspaceState,
  );
  const [notice, setNotice] = useState<string | null>(null);
  const [activeAdminTab, setActiveAdminTab] = useState<
    "products" | "variables" | "parameters" | "pipeline" | "rules" | "workflows" | "profiles"
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
        const normalizedMe = await new AuthApiClient().restore(storedSession.accessToken);
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

  useEffect(() => {
    function handleHashChange() {
      setRoute(readRoute());
    }

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  async function handleLogin(username: string, password: string) {
    setError(null);
    setIsSubmitting(true);

    try {
      const session = await new AuthApiClient().login(username, password);
      setToken(session.accessToken);
      setMe(session.me);
      saveStoredSession(session);
      window.location.hash = "#/consultas";
      setRoute("consultas");
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
    setLastConsultation(null);
    setLastEvaluation(null);
    setError(null);
    setNotice(null);
    window.location.hash = "";
    setRoute("consultas");
  }

  const adminClient = token ? new EngineAdminApiClient(token) : null;
  const attachmentsClient = token ? new AttachmentsApiClient(token) : null;
  const auditClient = token ? new AuditApiClient(token) : null;
  const runtimeClient = token ? new RuntimeApiClient(token) : null;
  const creditRequestsClient = token ? new CreditRequestsApiClient(token) : null;
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
      case "profiles":
        return <ProfilePermissionsPage {...sharedProps} />;
    }
  }

  function renderRouteContent() {
    if (runtimeClient === null || me === null) {
      return null;
    }

    if (route === "evaluaciones") {
      return (
        <EvaluationPage
          client={runtimeClient}
          me={me}
          consultation={lastConsultation}
          onEvaluationChange={setLastEvaluation}
        />
      );
    }

    if (route === "solicitudes" && creditRequestsClient !== null) {
      return (
        <>
            <CreditRequestPage
              client={creditRequestsClient}
              attachmentsClient={attachmentsClient}
              auditClient={auditClient}
              me={me}
              consultation={lastConsultation}
              evaluation={lastEvaluation}
            />
          <QueuePage client={creditRequestsClient} me={me} />
        </>
      );
    }

    if (route === "admin" && canManageEngine) {
      return (
        <section className="admin-shell">
          <div className="admin-shell-header">
            <div>
              <p className="eyebrow">Motor administrable</p>
              <h2>Phase 3</h2>
            </div>
            <p className="workspace-hint">
              Producto: {workspace.productCode || "sin definir"} | Workflow: {workspace.workflowCode || "sin definir"}
            </p>
          </div>

          <div className="tab-strip">
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("products")}>Productos</button>
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("variables")}>Variables</button>
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("parameters")}>Parametros</button>
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("pipeline")}>Pipeline</button>
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("rules")}>Reglas</button>
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("workflows")}>Versionado</button>
            <button className="secondary-button" type="button" onClick={() => setActiveAdminTab("profiles")}>Perfiles</button>
          </div>

          {notice ? <p className="success-banner">{notice}</p> : null}
          {renderAdminTab()}
        </section>
      );
    }

    return <ConsultationPage client={runtimeClient} onConsultationChange={setLastConsultation} />;
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

        {me === null ? (
          <LoginPage isSubmitting={isSubmitting} error={error} onLogin={handleLogin} />
        ) : null}

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
              <div className="tab-strip">
                <button className="secondary-button" type="button" onClick={() => { window.location.hash = "#/consultas"; setRoute("consultas"); }}>Consultas</button>
                <button className="secondary-button" type="button" onClick={() => { window.location.hash = "#/evaluaciones"; setRoute("evaluaciones"); }}>Evaluaciones</button>
                <button className="secondary-button" type="button" onClick={() => { window.location.hash = "#/solicitudes"; setRoute("solicitudes"); }}>Solicitudes</button>
                {canManageEngine ? (
                  <button className="secondary-button" type="button" onClick={() => { window.location.hash = "#/admin"; setRoute("admin"); }}>Motor</button>
                ) : null}
              </div>
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

        <ul className="feature-list">
          <li>Consulta y evaluacion PLD</li>
          <li>Bandeja y solicitudes</li>
          <li>Adjuntos ZIP</li>
          <li>Paneles AI asistivos</li>
        </ul>

        {me ? renderRouteContent() : null}
      </section>
    </main>
  );
}

export default App;
