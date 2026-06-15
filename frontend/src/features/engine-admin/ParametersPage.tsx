import { useState } from "react";

import { EngineAdminApiClient, EngineAdminWorkspaceState } from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function ParametersPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleCreateParameterSet() {
    setIsSubmitting(true);
    try {
      const parameterSet = await client.createParameterSet(workspace.productCode, workspace.workflowCode, {
        min_score: 500,
      });
      onWorkspaceChange({ parameterSetId: parameterSet.id });
      onNotice(`Set de parametros v${parameterSet.versionNumber} creado.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear el set de parametros.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivateParameterSet() {
    if (workspace.parameterSetId === null) {
      onNotice("Primero crea un set de parametros.");
      return;
    }

    setIsSubmitting(true);
    try {
      await client.activateParameterSet(workspace.parameterSetId);
      onNotice("Set de parametros activado.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar el set de parametros.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Parametros</h2>
      <p className="workspace-hint">
        Los parametros versionados se publican para el workflow actual. En draft la aprobacion permanece pendiente hasta activacion real.
      </p>
      <div className="action-row">
        <button className="primary-button" type="button" onClick={handleCreateParameterSet} disabled={isSubmitting}>
          Crear parametros draft
        </button>
        <button className="secondary-button" type="button" onClick={handleActivateParameterSet} disabled={isSubmitting}>
          Publicar parametros
        </button>
      </div>
      <p className="workspace-hint">Parameter set: {workspace.parameterSetId ?? "pendiente"}</p>
      <p className="workspace-hint">Workflow asociado: {workspace.workflowCode || "sin definir"}</p>
    </section>
  );
}
