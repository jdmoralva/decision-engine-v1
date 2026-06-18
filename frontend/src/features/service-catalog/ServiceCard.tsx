import type { PlatformService } from "../platform/catalog-types";

type ServiceCardProps = {
  service: PlatformService;
  onOpen: (service: PlatformService) => void;
};

export function ServiceCard({ service, onOpen }: ServiceCardProps) {
  return (
    <article className="service-card">
      <div className="service-card-header">
        <div>
          <p className="service-card-icon">{service.iconKey}</p>
          <h3>{service.displayName}</h3>
        </div>
        <span className="environment-pill environment-pill--production">{service.statusLabel}</span>
      </div>

      <p className="workspace-hint">{service.description}</p>

      <div className="service-card-actions">
        <button
          aria-label={`Abrir servicio ${service.displayName}`}
          className="primary-button"
          type="button"
          onClick={() => onOpen(service)}
        >
          Abrir servicio
        </button>
        <button
          aria-label={`Eliminar servicio ${service.displayName}`}
          className="secondary-button"
          type="button"
        >
          Eliminar
        </button>
      </div>
    </article>
  );
}
