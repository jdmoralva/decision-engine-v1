import { useEffect } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { useSessionContext } from "../../app/session-context";
import { EngineAdminApiClient } from "../../services/engine-admin-api";
import { canManageEngine } from "../platform/service-visibility";
import { loadWorkspaceDraft } from "./workspace-session";
import { WorkspaceProvider, useWorkspaceContext } from "./workspace-context";
import { createSeededWorkspaceDraft } from "./workflow-seed-data";
import { loadGovernedWorkflows } from "./workspace-api-adapters";
import { WorkspaceSidebar } from "./WorkspaceSidebar";
import { WorkspaceCanvas } from "./WorkspaceCanvas";
import { NodeInspector } from "./NodeInspector";
import { WorkflowCatalogPanel } from "./WorkflowCatalogPanel";
import { ChannelPanel } from "./ChannelPanel";
import { TestingPanel } from "./TestingPanel";
import { EventsPanel } from "./EventsPanel";
import { ParametersPanel } from "./ParametersPanel";
import { DataPanel } from "./DataPanel";
import { ProfileMenu } from "./ProfileMenu";

function normalizeGroupFromSection(section: string | undefined): string {
  switch (section) {
    case "parametros":
      return "Parametros";
    case "data":
      return "Data";
    default:
      return "Reglas de Negocio";
  }
}

function WorkspaceScreen() {
  const navigate = useNavigate();
  const { logout, me, token } = useSessionContext();
  const { state, dispatch } = useWorkspaceContext();
  const { productCode, section, item } = useParams();

  useEffect(() => {
    if (token === null || productCode === undefined || !canManageEngine(me?.roles ?? [])) {
      return;
    }

    const client = new EngineAdminApiClient(token);
    void loadGovernedWorkflows(client, productCode)
      .then((result) => {
        dispatch({ type: "set-governed-workflows", active: result.active, draft: result.draft });
      })
      .catch(() => {
        dispatch({ type: "set-notice", notice: "No fue posible consultar workflows gobernados." });
      });
  }, [dispatch, me?.roles, productCode, token]);

  useEffect(() => {
    dispatch({
      type: "set-sidebar-item",
      group: normalizeGroupFromSection(section),
      item: item ?? (section === "parametros" ? "limites-internos" : section === "data" ? "importar-dataset" : "workflows"),
    });
  }, [dispatch, item, section]);

  const selectedNode = (state.nodes ?? []).find((node) => node.id === state.selectedNodeId) ?? null;

  function handleSelectSidebar(group: string, nextItem: string) {
    const nextSection =
      group === "Parametros" ? "parametros" : group === "Data" ? "data" : nextItem;
    navigate(`/productos/${state.productCode}/servicios/decision-engine/${nextSection}/${nextItem}`);
  }

  function renderPanel() {
    if (state.activeSidebarGroup === "Parametros") {
      return <ParametersPanel item={state.activeSidebarItem} canEdit={me?.roles.includes("admin_riesgos") ?? false} />;
    }

    if (state.activeSidebarGroup === "Data") {
      return <DataPanel item={state.activeSidebarItem} />;
    }

    if (state.activeSidebarItem === "channels") {
      return (
        <ChannelPanel
          activeWorkflows={state.governedWorkflows.active}
          channels={state.channels}
          selectedParameterSetIds={state.selectedParameterSetIds}
          onToggleParameterSet={(parameterSetId) => dispatch({ type: "toggle-parameter-set", parameterSetId })}
        />
      );
    }

    if (state.activeSidebarItem === "testing") {
      return <TestingPanel tests={state.tests} />;
    }

    if (state.activeSidebarItem === "events") {
      return <EventsPanel events={state.events} />;
    }

    return <WorkflowCatalogPanel active={state.governedWorkflows.active} draft={state.governedWorkflows.draft} />;
  }

  return (
    <section className="decision-workspace-page">
      <div className="breadcrumb-row">
        <span>Productos</span>
        <span>/</span>
        <span>{state.productCode}</span>
        <span>/</span>
        <span>Motor de decisiones</span>
        <span>/</span>
        <strong>{section ?? "workflows"}</strong>
      </div>

      <div>
        <p className="eyebrow">Workspace</p>
        <h2 className="workspace-title">Motor de decisiones</h2>
      </div>

      {state.notice ? <p className="success-banner">{state.notice}</p> : null}

      <div className="decision-workspace-layout">
        <WorkspaceSidebar
          activeGroup={state.activeSidebarGroup}
          activeItem={state.activeSidebarItem}
          onSelect={handleSelectSidebar}
        />

        <div className="decision-workspace-main">
          {renderPanel()}
          <WorkspaceCanvas
            connections={state.connections ?? []}
            nodes={state.nodes ?? []}
            selectedNodeId={state.selectedNodeId}
            onAddNode={() => dispatch({ type: "add-node" })}
            onMoveSelectedNode={() => dispatch({ type: "move-selected-node" })}
            onRemoveSelectedNode={() => dispatch({ type: "remove-selected-node" })}
            onSelectNode={(nodeId) => dispatch({ type: "select-node", nodeId })}
          />
        </div>

        <div className="decision-workspace-sidepanel">
          <NodeInspector node={selectedNode} />
          <ProfileMenu
            isOpen={state.profileMenuOpen}
            onToggle={() => dispatch({ type: "toggle-profile-menu" })}
            onChangePassword={() => dispatch({ type: "set-notice", notice: "Cambio de contrasena disponible como demo local" })}
            onShowPermissions={() => dispatch({ type: "set-notice", notice: "Permisos aprobados visibles como referencia local" })}
            onLogout={() => {
              logout();
              navigate("/login");
            }}
          />
        </div>
      </div>
    </section>
  );
}

export function DecisionWorkspacePage() {
  const { me } = useSessionContext();
  const { productCode } = useParams();

  if (me === null || productCode === undefined || !canManageEngine(me.roles)) {
    return <Navigate to={`/productos/${productCode ?? "PLD"}/servicios`} replace />;
  }

  const storedDraft = loadWorkspaceDraft({
    productCode,
    serviceKey: "DecisionEngine",
    workflowId: "wf-local-originacion",
  });
  const draft = storedDraft ?? createSeededWorkspaceDraft(productCode);

  return (
    <WorkspaceProvider draft={draft}>
      <WorkspaceScreen />
    </WorkspaceProvider>
  );
}
