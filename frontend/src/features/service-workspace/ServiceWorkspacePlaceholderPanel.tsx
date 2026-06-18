type PlaceholderRow = {
  name: string;
  detail: string;
  status: string;
};

type ServiceWorkspacePlaceholderPanelProps = {
  serviceName: string;
  sectionTitle: string;
  description: string;
  rows: PlaceholderRow[];
};

export function ServiceWorkspacePlaceholderPanel({
  serviceName,
  sectionTitle,
  description,
  rows,
}: ServiceWorkspacePlaceholderPanelProps) {
  return (
    <section className="service-workspace-panel">
      <div className="service-workspace-panel-header">
        <div>
          <p className="eyebrow">Mock operativo</p>
          <h3>{sectionTitle}</h3>
          <p className="workspace-hint">{description}</p>
        </div>
        <span className="service-workspace-status">{serviceName}</span>
      </div>

      <div className="service-workspace-table" role="table" aria-label={`${sectionTitle} placeholder`}>
        <div className="service-workspace-table-header" role="row">
          <span>Elemento</span>
          <span>Contexto</span>
          <span>Estado</span>
        </div>
        {rows.map((row) => (
          <div className="service-workspace-table-row" key={row.name} role="row">
            <strong>{row.name}</strong>
            <span>{row.detail}</span>
            <span>{row.status}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
