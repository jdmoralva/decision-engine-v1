import type { WorkspaceConnection, WorkspaceNode } from "./workspace-types";

type WorkspaceCanvasProps = {
  nodes: WorkspaceNode[];
  connections: WorkspaceConnection[];
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
  onMoveSelectedNode: () => void;
  onAddNode: () => void;
  onRemoveSelectedNode: () => void;
};

export function WorkspaceCanvas({
  nodes,
  connections,
  selectedNodeId,
  onSelectNode,
  onMoveSelectedNode,
  onAddNode,
  onRemoveSelectedNode,
}: WorkspaceCanvasProps) {
  return (
    <section className="workspace-canvas-panel">
      <div className="workspace-toolbar">
        <button aria-label="Agregar nodo" className="secondary-button" type="button" onClick={onAddNode}>
          Agregar nodo
        </button>
        <button
          aria-label="Mover nodo seleccionado"
          className="secondary-button"
          type="button"
          onClick={onMoveSelectedNode}
        >
          Mover nodo
        </button>
        <button
          aria-label="Eliminar nodo seleccionado"
          className="secondary-button"
          type="button"
          onClick={onRemoveSelectedNode}
        >
          Eliminar nodo
        </button>
      </div>

      <div className="workspace-canvas">
        {connections.map((connection) => (
          <div className="workspace-connection" key={connection.id}>
            {connection.label}
          </div>
        ))}
        <div className="workspace-node-grid">
          {nodes.map((node) => {
            const isSelected = node.id === selectedNodeId;
            return (
              <button
                aria-label={`Nodo ${node.name}`}
                className={isSelected ? "workspace-node workspace-node--selected" : "workspace-node"}
                key={node.id}
                type="button"
                onClick={() => onSelectNode(node.id)}
              >
                {node.name}
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
