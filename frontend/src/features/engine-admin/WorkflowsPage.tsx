import { useState } from "react";

import { EngineAdminApiClient, EngineAdminWorkspaceState } from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function WorkflowsPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

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
      onNotice("Workflow version activada.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar la version del workflow.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Versionado de workflow</h2>
      <div className="action-row">
        <button className="primary-button" type="button" onClick={handleCreateWorkflowVersion} disabled={isSubmitting}>
          Crear version de workflow
        </button>
        <button className="secondary-button" type="button" onClick={handleActivateWorkflowVersion} disabled={isSubmitting}>
          Activar version de workflow
        </button>
      </div>
      <p className="workspace-hint">Workflow version: {workspace.workflowVersionId ?? "pendiente"}</p>
    </section>
  );
}
