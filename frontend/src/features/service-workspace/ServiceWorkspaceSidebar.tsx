import type { ServiceWorkspaceNavGroup } from "./service-workspace-types";

type ServiceWorkspaceSidebarProps = {
  groups: ServiceWorkspaceNavGroup[];
  activeSection: string;
  activeItem?: string;
  onSelect: (section: string, item?: string) => void;
};

export function ServiceWorkspaceSidebar({
  groups,
  activeSection,
  activeItem,
  onSelect,
}: ServiceWorkspaceSidebarProps) {
  return (
    <aside className="service-workspace-sidebar">
      {groups.map((group) => (
        <section className="service-workspace-sidebar-group" key={group.key}>
          <p className="service-workspace-sidebar-label">{group.label}</p>
          <div className="service-workspace-sidebar-items">
            {group.items.map((item) => {
              const isActive = item.section === activeSection && (item.item ?? null) === (activeItem ?? null);

              return (
                <button
                  aria-label={`Abrir ${item.ariaLabel ?? item.label}`}
                  className={isActive ? "service-workspace-nav-button service-workspace-nav-button--active" : "service-workspace-nav-button"}
                  key={item.key}
                  type="button"
                  onClick={() => onSelect(item.section, item.item)}
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
