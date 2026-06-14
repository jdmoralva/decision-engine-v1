type StatusActionsProps = {
  actions: string[];
  onAction: (targetStatus: string) => void;
};


export function StatusActions({ actions, onAction }: StatusActionsProps) {
  if (actions.length === 0) {
    return <p className="session-empty">Sin acciones disponibles.</p>;
  }

  return (
    <div className="tab-strip">
      {actions.map((action) => (
        <button
          key={action}
          className="secondary-button"
          type="button"
          onClick={() => onAction(action)}
        >
          Mover a {action}
        </button>
      ))}
    </div>
  );
}
