import { useState } from "react";
import {
  HashRouter,
  Navigate,
  Route,
  Routes,
  useParams,
} from "react-router-dom";

import { AppShell } from "../app/AppShell";
import { useSessionContext } from "../app/session-context";
import { LoginPage } from "../features/auth/LoginPage";
import {
  findVisibleServiceForRoles,
} from "../features/platform/service-visibility";
import { ProductCatalogPage } from "../features/product-catalog/ProductCatalogPage";
import { DecisionWorkspacePage } from "../features/decision-workspace/DecisionWorkspacePage";
import { ServiceCatalogPage } from "../features/service-catalog/ServiceCatalogPage";
import { ParametersPage } from "../features/engine-admin/ParametersPage";
import { PipelinePage } from "../features/engine-admin/PipelinePage";
import { ProfilePermissionsPage } from "../features/engine-admin/ProfilePermissionsPage";
import { ProductsPage } from "../features/engine-admin/ProductsPage";
import { RulesPage } from "../features/engine-admin/RulesPage";
import { VariablesPage } from "../features/engine-admin/VariablesPage";
import { WorkflowsPage } from "../features/engine-admin/WorkflowsPage";
import { CreditRequestPage } from "../features/credit-requests/CreditRequestPage";
import { QueuePage } from "../features/credit-requests/QueuePage";
import { EvaluationPage } from "../features/evaluations/EvaluationPage";
import { ConsultationPage } from "../features/loan-consultations/ConsultationPage";
import { AttachmentsApiClient } from "../services/attachments-api";
import { AuditApiClient } from "../services/audit-api";
import { CreditRequestsApiClient } from "../services/credit-requests-api";
import {
  emptyEngineAdminWorkspaceState,
  EngineAdminApiClient,
  type EngineAdminWorkspaceState,
} from "../services/engine-admin-api";
import {
  RuntimeApiClient,
  type ConsultationResponse,
  type EvaluationResponse,
} from "../services/runtime-api";

type AdminTab =
  | "products"
  | "variables"
  | "parameters"
  | "pipeline"
  | "rules"
  | "workflows"
  | "profiles";

function LoginRoute() {
  const { status, isSubmitting, error, login } = useSessionContext();

  if (status === "authenticated") {
    return <Navigate to="/productos" replace />;
  }

  return (
    <AppShell>
      <LoginPage isSubmitting={isSubmitting} error={error} onLogin={login} />
    </AppShell>
  );
}

function ProtectedRoute() {
  const { status } = useSessionContext();

  if (status === "restoring") {
    return <AppShell><div /></AppShell>;
  }

  if (status !== "authenticated") {
    return <Navigate to="/login" replace />;
  }

  return <AuthenticatedLayout />;
}

function AuthenticatedLayout() {
  const { me, token, canManageCurrentSession } = useSessionContext();
  const [lastConsultation, setLastConsultation] = useState<ConsultationResponse | null>(null);
  const [lastEvaluation, setLastEvaluation] = useState<EvaluationResponse | null>(null);
  const [workspace, setWorkspace] = useState<EngineAdminWorkspaceState>(emptyEngineAdminWorkspaceState);
  const [notice, setNotice] = useState<string | null>(null);
  const [activeAdminTab, setActiveAdminTab] = useState<AdminTab>("products");

  if (me === null || token === null) {
    return <Navigate to="/login" replace />;
  }

  const runtimeClient = new RuntimeApiClient(token);
  const creditRequestsClient = new CreditRequestsApiClient(token);
  const attachmentsClient = new AttachmentsApiClient(token);
  const auditClient = new AuditApiClient(token);
  const adminClient = canManageCurrentSession ? new EngineAdminApiClient(token) : null;

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

  return (
    <AppShell>
      <Routes>
        <Route
          path="/"
          element={<Navigate to="/productos" replace />}
        />
        <Route
          path="/consultas"
          element={
            <ConsultationPage client={runtimeClient} onConsultationChange={setLastConsultation} />
          }
        />
        <Route
          path="/evaluaciones"
          element={
            <EvaluationPage
              client={runtimeClient}
              me={me}
              consultation={lastConsultation}
              onEvaluationChange={setLastEvaluation}
            />
          }
        />
        <Route
          path="/solicitudes"
          element={
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
          }
        />
        <Route path="/admin" element={canManageCurrentSession ? (
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
        ) : <Navigate to="/productos" replace />} />
        <Route path="/productos" element={<ProductCatalogPage />} />
        <Route path="/productos/:productCode/servicios" element={<ServiceCatalogPage />} />
        <Route path="/productos/:productCode/servicios/:serviceKey" element={<ServiceWorkspaceFoundationPage />} />
        <Route
          path="/productos/:productCode/servicios/decision-engine/:section/:item"
          element={<DecisionWorkspaceFoundationPage />}
        />
        <Route
          path="/productos/:productCode/servicios/decision-engine/:section"
          element={<DecisionWorkspaceFoundationPage />}
        />
        <Route path="*" element={<Navigate to="/productos" replace />} />
      </Routes>
    </AppShell>
  );
}

function ServiceWorkspaceFoundationPage() {
  const { me } = useSessionContext();
  const { productCode, serviceKey } = useParams();

  if (me === null || productCode === undefined || serviceKey === undefined) {
    return <Navigate to="/productos" replace />;
  }

  const service = findVisibleServiceForRoles(me.roles, serviceKey);

  if (service === null) {
    return <Navigate to={`/productos/${productCode}/servicios`} replace />;
  }

  if (service.routeSegment === "decision-engine") {
    return <DecisionWorkspacePage />;
  }

  return (
    <section className="workspace-card">
      <div className="breadcrumb-row">
        <span>Productos</span>
        <span>/</span>
        <span>{productCode}</span>
        <span>/</span>
        <strong>{service.displayName}</strong>
      </div>
      <p className="eyebrow">Workspace</p>
      <h2>{service.displayName}</h2>
      <p className="workspace-hint">
        Navegacion protegida lista para {productCode}. Servicio activo: {service.displayName}.
      </p>
    </section>
  );
}

function DecisionWorkspaceFoundationPage() {
  return <DecisionWorkspacePage />;
}

export function AppRouter() {
  return (
    <HashRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        <Route path="/login" element={<LoginRoute />} />
        <Route path="/*" element={<ProtectedRoute />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </HashRouter>
  );
}
