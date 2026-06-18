import type { WorkspaceNode } from "./workspace-types";

type NodeInspectorProps = {
  node: WorkspaceNode | null;
};

export function NodeInspector({ node }: NodeInspectorProps) {
  if (node === null) {
    return (
      <aside className="workspace-inspector">
        <h3>Inspector</h3>
        <p className="workspace-hint">Selecciona un nodo para ver su configuracion.</p>
      </aside>
    );
  }

  return (
    <aside className="workspace-inspector">
      <h3>Inspector</h3>
      <p><strong>Nodo seleccionado</strong></p>
      <p>{node.name}</p>
      <p>{`Tipo ${node.type}`}</p>
      <p>{node.description}</p>
      <p>{node.decisionLogic}</p>
    </aside>
  );
}
