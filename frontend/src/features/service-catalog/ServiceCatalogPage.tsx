import { Navigate, useNavigate, useParams } from "react-router-dom";

import { useSessionContext } from "../../app/session-context";
import { getVisibleServicesForRoles } from "../platform/service-visibility";
import type { PlatformService } from "../platform/catalog-types";
import { ServiceCard } from "./ServiceCard";

export function ServiceCatalogPage() {
  const navigate = useNavigate();
  const { me } = useSessionContext();
  const { productCode } = useParams();

  if (me === null || productCode === undefined) {
    return <Navigate to="/productos" replace />;
  }

  const services = getVisibleServicesForRoles(me.roles);

  function handleOpenService(service: PlatformService) {
    navigate(`/productos/${productCode}/servicios/${service.routeSegment}`);
  }

  return (
    <section className="service-catalog-page">
      <div className="breadcrumb-row">
        <span>Productos</span>
        <span>/</span>
        <span>{productCode}</span>
        <span>/</span>
        <strong>Servicios</strong>
      </div>

      <div className="catalog-header">
        <div>
          <p className="eyebrow">Servicios</p>
          <h2>{productCode}</h2>
          <p className="workspace-hint">
            Catalogo filtrado por rol. La visibilidad se mantiene igual entre productos.
          </p>
        </div>
      </div>

      <div className="service-catalog-grid">
        {services.map((service) => (
          <ServiceCard key={service.serviceKey} service={service} onOpen={handleOpenService} />
        ))}
      </div>
    </section>
  );
}
