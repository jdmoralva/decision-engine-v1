import { useState } from "react";

import { EngineAdminApiClient, EngineAdminWorkspaceState } from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function PipelinePage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleCreatePipeline() {
    setIsSubmitting(true);
    try {
      const strategy = await client.createPipelineStrategy(workspace.productCode, {
        graphDefinition: { entryNode: "eligibility" },
        nodes: [{ nodeKey: "eligibility", nodeType: "rule_group", configPayload: { mode: "all" } }],
      });
      onWorkspaceChange({ pipelineStrategyId: strategy.id });
      onNotice(`Pipeline v${strategy.versionNumber} creado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear el pipeline.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivatePipeline() {
    if (workspace.pipelineStrategyId === null) {
      onNotice("Primero crea un pipeline.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.activatePipelineStrategy(workspace.pipelineStrategyId);
      onNotice("Pipeline activado.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar el pipeline.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Pipeline</h2>
      <div className="action-row">
        <button className="primary-button" type="button" onClick={handleCreatePipeline} disabled={isSubmitting}>
          Crear pipeline draft
        </button>
        <button className="secondary-button" type="button" onClick={handleActivatePipeline} disabled={isSubmitting}>
          Activar pipeline
        </button>
      </div>
      <p className="workspace-hint">Pipeline: {workspace.pipelineStrategyId ?? "pendiente"}</p>
    </section>
  );
}
