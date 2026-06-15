import { useState } from "react";

import { EngineAdminApiClient, EngineAdminWorkspaceState } from "../../services/engine-admin-api";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function RulesPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleCreateRule() {
    if (workspace.workflowId === null) {
      onNotice("Primero crea un workflow.");
      return;
    }

    setIsSubmitting(true);
    try {
      const rule = await client.createRule(workspace.workflowId, {
        name: "Regla base",
        ruleType: "eligibility",
        conditionExpression: "validated_income > 0",
        actionExpression: "allow",
      });
      onWorkspaceChange({ ruleId: rule.id, ruleVersionId: rule.activeVersion.id });
      onNotice(`Regla ${rule.name} creada.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo crear la regla.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleActivateRule() {
    if (workspace.ruleVersionId === null) {
      onNotice("Primero crea una regla.");
      return;
    }

    const ruleVersionId = workspace.ruleVersionId;

    setIsSubmitting(true);
    try {
      await client.activateRuleVersion(ruleVersionId);
      onNotice("Regla activada.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar la regla.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteRule() {
    if (workspace.ruleId === null) {
      onNotice("Primero crea una regla.");
      return;
    }

    const ruleId = workspace.ruleId;

    setIsSubmitting(true);
    try {
      await client.deleteRule(ruleId);
      onNotice("Regla eliminada.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo eliminar la regla.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Reglas</h2>
      <p className="workspace-hint">
        `Eliminar` aplica solo a draft autorizados. Las reglas activas requieren reemplazo o retiro gobernado desde el workflow publicado.
      </p>
      <div className="action-row">
        <button className="primary-button" type="button" onClick={handleCreateRule} disabled={isSubmitting}>
          Crear regla draft
        </button>
        <button className="secondary-button" type="button" onClick={handleActivateRule} disabled={isSubmitting}>
          Activar regla
        </button>
        <button className="secondary-button" type="button" onClick={handleDeleteRule} disabled={isSubmitting}>
          Eliminar regla
        </button>
      </div>
      <p className="workspace-hint">Rule version: {workspace.ruleVersionId ?? "pendiente"}</p>
      <p className="workspace-hint">Workflow asociado: {workspace.workflowCode || "sin definir"}</p>
    </section>
  );
}
