import type { WorkspaceWorkflowSummary } from "./workspace-types";

type WorkflowCatalogPanelProps = {
  active: WorkspaceWorkflowSummary[];
  draft: WorkspaceWorkflowSummary[];
};

export function WorkflowCatalogPanel({ active, draft }: WorkflowCatalogPanelProps) {
  return (
    <section className="workspace-card">
      <h3>Workflows</h3>
      <p><strong>Aprobado</strong></p>
      {active.map((workflow) => (
        <p key={workflow.id}>{workflow.name}</p>
      ))}
      <p><strong>Borrador</strong></p>
      {draft.map((workflow) => (
        <p key={workflow.id}>{workflow.name}</p>
      ))}
    </section>
  );
}
