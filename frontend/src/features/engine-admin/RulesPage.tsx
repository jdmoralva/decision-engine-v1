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
      onWorkspaceChange({ ruleVersionId: rule.activeVersion.id });
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

    setIsSubmitting(true);
    try {
      await client.activateRuleVersion(workspace.ruleVersionId);
      onNotice("Regla activada.");
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudo activar la regla.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="workspace-card">
      <h2>Reglas</h2>
      <div className="action-row">
        <button className="primary-button" type="button" onClick={handleCreateRule} disabled={isSubmitting}>
          Crear regla draft
        </button>
        <button className="secondary-button" type="button" onClick={handleActivateRule} disabled={isSubmitting}>
          Activar regla
        </button>
      </div>
      <p className="workspace-hint">Rule version: {workspace.ruleVersionId ?? "pendiente"}</p>
    </section>
  );
}
