import type { WorkspaceChannel, WorkspaceWorkflowSummary } from "./workspace-types";

type ChannelPanelProps = {
  channels: WorkspaceChannel[];
  activeWorkflows: WorkspaceWorkflowSummary[];
  selectedParameterSetIds: string[];
  onToggleParameterSet: (parameterSetId: string) => void;
};

export function ChannelPanel({
  channels,
  activeWorkflows,
  selectedParameterSetIds,
  onToggleParameterSet,
}: ChannelPanelProps) {
  return (
    <section className="workspace-card">
      <h3>Canales</h3>
      <p>Workflow aprobado</p>
      {activeWorkflows.map((workflow) => (
        <p key={workflow.id}>{workflow.name}</p>
      ))}
      <div className="workspace-checkboxes">
        {[
          { id: "param-1", label: "Limites aprobados" },
          { id: "param-2", label: "Autonomia aprobada" },
        ].map((item) => (
          <label key={item.id}>
            <input
              checked={selectedParameterSetIds.includes(item.id)}
              type="checkbox"
              onChange={() => onToggleParameterSet(item.id)}
            />
            {item.label}
          </label>
        ))}
      </div>
      {channels.map((channel) => (
        <p key={channel.id}>{channel.compatibilityValidation}</p>
      ))}
    </section>
  );
}
