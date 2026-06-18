import { workspaceSidebar } from "./workflow-seed-data";

type WorkspaceSidebarProps = {
  activeGroup: string;
  activeItem: string;
  onSelect: (group: string, item: string) => void;
};

export function WorkspaceSidebar({ activeGroup, activeItem, onSelect }: WorkspaceSidebarProps) {
  return (
    <aside className="workspace-sidebar">
      {Object.entries(workspaceSidebar).map(([group, items]) => (
        <section className="workspace-sidebar-group" key={group}>
          <h3>{group}</h3>
          <div className="workspace-sidebar-items">
            {items.map((item) => {
              const isActive = activeGroup === group && activeItem === item.key;
              return (
                <button
                  aria-label={`Abrir ${item.label}`}
                  className={isActive ? "primary-button" : "secondary-button"}
                  key={item.key}
                  type="button"
                  onClick={() => onSelect(group, item.key)}
                >
                  {item.label}
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </aside>
  );
}
