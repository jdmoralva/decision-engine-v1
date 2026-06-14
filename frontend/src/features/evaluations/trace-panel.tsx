import { type DecisionTraceResponse } from "../../services/runtime-api";

type TracePanelProps = {
  trace: DecisionTraceResponse | null;
};

export function TracePanel({ trace }: TracePanelProps) {
  if (trace === null) {
    return null;
  }

  return (
    <div className="session-panel">
      <h3>Trace</h3>
      {trace.nodes_executed.map((node) => (
        <p key={node.node_key}>{node.node_key}</p>
      ))}
      {trace.evidence.map((item) => (
        <p key={`${item.source_key}:${item.field_name}`}>{item.field_name}</p>
      ))}
    </div>
  );
}
