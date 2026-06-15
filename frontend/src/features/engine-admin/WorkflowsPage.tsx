import { useEffect, useState } from "react";

import {
  AdminArtifactState,
  EngineAdminApiClient,
  EngineAdminWorkspaceState,
  WorkflowDetailResponse,
  WorkflowResponse,
} from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function WorkflowsPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [viewState, setViewState] = useState<AdminArtifactState>("active");
  const [workflows, setWorkflows] = useState<WorkflowResponse[]>([]);
  const [detail, setDetail] = useState<WorkflowDetailResponse | null>(null);

  useEffect(() => {
    if (!workspace.productCode) {
      setWorkflows([]);
      return;
    }

    let cancelled = false;
    async function loadWorkflows() {
      try {
        const response = await client.listWorkflows(workspace.productCode, viewState);
        if (!cancelled) {
          setWorkflows(response.items);
        }
      } catch (error) {
        if (!cancelled) {
          onNotice(error instanceof Error ? error.message : "No se pudieron cargar workflows.");
        }
      }
    }

    void loadWorkflows();
    return () => {
      cancelled = true;
    };
  }, [client, onNotice, viewState, workspace.productCode]);

  async function handleRefresh() {
    if (!workspace.productCode) {
      setWorkflows([]);
      return;
    }
    const response = await client.listWorkflows(workspace.productCode, viewState);
    setWorkflows(response.items);
  }

  async function handleLoadDetail(workflowId: string) {
    try {
      const response = await client.getWorkflowDetail(workflowId);
      setDetail(response);
      onWorkspaceChange({ workflowId: response.id, workflowCode: response.workflowCode });
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo cargar el detalle del workflow.");
    }
  }

  async function handleCreateWorkflowVersion() {
    if (
      workspace.workflowId === null ||
      workspace.catalogId === null ||
      workspace.parameterSetId === null ||
      workspace.pipelineStrategyId === null ||
      workspace.ruleVersionId === null
    ) {
      onNotice("Completa catalogo, parametros, pipeline y reglas antes de versionar.");
      return;
    }

    setIsSubmitting(true);
    try {
      const version = await client.createWorkflowVersion(workspace.workflowId, {
        variableCatalogVersionId: workspace.catalogId,
        parameterSetId: workspace.parameterSetId,
        pipelineStrategyId: workspace.pipelineStrategyId,
        ruleVersionIds: [workspace.ruleVersionId],
        changeNotes: "Version inicial desde UI",
      });
      onWorkspaceChange({ workflowVersionId: version.id });
      await handleRefresh();
      onNotice(`Workflow version v${version.versionNumber} creada.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear la version del workflow.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivateWorkflowVersion() {
    if (workspace.workflowVersionId === null) {
      onNotice("Primero crea una version de workflow.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.activateWorkflowVersion(workspace.workflowVersionId);
      if (workspace.workflowId) {
        await handleLoadDetail(workspace.workflowId);
      }
      await handleRefresh();
      onNotice("Workflow version activada.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar la version del workflow.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteWorkflow() {
    if (workspace.workflowId === null) {
      onNotice("Primero crea un workflow.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.deleteWorkflow(workspace.workflowId);
      setDetail(null);
      await handleRefresh();
      onNotice("Workflow eliminado.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo eliminar el workflow.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleRetireWorkflow() {
    if (workspace.workflowId === null) {
      onNotice("Primero crea un workflow.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.retireWorkflow(workspace.workflowId);
      await handleRefresh();
      await handleLoadDetail(workspace.workflowId);
      onNotice("Workflow retirado.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo retirar el workflow.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Versionado de workflow</h2>
      <div className="action-row">
        <button className="secondary-button" type="button" onClick={() => setViewState("active")} disabled={viewState === "active"}>
          Ver activos
        </button>
        <button className="secondary-button" type="button" onClick={() => setViewState("draft")} disabled={viewState === "draft"}>
          Ver draft
        </button>
      </div>
      <div className="action-row">
        <button className="primary-button" type="button" onClick={handleCreateWorkflowVersion} disabled={isSubmitting}>
          Crear version de workflow
        </button>
        <button className="secondary-button" type="button" onClick={handleActivateWorkflowVersion} disabled={isSubmitting}>
          Activar version de workflow
        </button>
        <button className="secondary-button" type="button" onClick={handleDeleteWorkflow} disabled={isSubmitting}>
          Eliminar workflow draft
        </button>
        <button className="secondary-button" type="button" onClick={handleRetireWorkflow} disabled={isSubmitting}>
          Retirar workflow
        </button>
      </div>
      <p className="workspace-hint">Workflow version: {workspace.workflowVersionId ?? "pendiente"}</p>
      <ul className="feature-list">
        {workflows.map((workflow) => (
          <li key={workflow.id}>
            {workflow.workflowCode} · {workflow.name} · {workflow.status}{" "}
            <button className="secondary-button" type="button" onClick={() => void handleLoadDetail(workflow.id)}>
              Ver detalle
            </button>
          </li>
        ))}
      </ul>
      {detail ? (
        <div className="session-panel">
          <h3>Detalle del workflow</h3>
          <p>
            {detail.workflowCode} · {detail.name}
          </p>
          <p>Aprobacion: {detail.approval.status === "pending" ? "pendiente" : detail.approval.approvedBy ?? "aprobado"}</p>
          <p>Retiro: {detail.retirement.performedAt ? detail.retirement.performedAt : "sin registro"}</p>
          <p>Eliminacion: {detail.deletion.performedAt ? detail.deletion.performedAt : "sin registro"}</p>
          <p>Reglas versionadas: {detail.ruleVersionIds.length}</p>
        </div>
      ) : null}
    </section>
  );
}
