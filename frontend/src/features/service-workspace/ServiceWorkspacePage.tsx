import { Navigate, useNavigate, useParams } from "react-router-dom";

import { useSessionContext } from "../../app/session-context";
import { findVisibleServiceForRoles } from "../platform/service-visibility";
import { DecisionWorkspaceEmbedded } from "../decision-workspace/DecisionWorkspacePage";
import {
  buildServiceWorkspacePath,
  getServiceWorkspaceDefinition,
} from "./service-workspace-config";
import { ServiceWorkspacePlaceholderPanel } from "./ServiceWorkspacePlaceholderPanel";
import { ServiceWorkspaceSidebar } from "./ServiceWorkspaceSidebar";

type PlaceholderConfig = {
  title: string;
  description: string;
  rows: Array<{ name: string; detail: string; status: string }>;
};

const placeholderContent: Record<string, Record<string, PlaceholderConfig>> = {
  "credit-applications": {
    resumen: {
      title: "Resumen",
      description: "Vista consolidada del servicio con volumen, capacidad y desvio operativo en modo local.",
      rows: [
        { name: "Cola vigente", detail: "312 solicitudes listas para analisis", status: "Operativa" },
        { name: "Capacidad", detail: "3 equipos con cobertura activa", status: "Balanceada" },
        { name: "Alertas", detail: "2 reglas de priorizacion esperando ajuste", status: "En seguimiento" },
      ],
    },
    "cola-activa": {
      title: "Cola activa",
      description: "Backlog visible por canal, producto y severidad para pruebas de layout frontend.",
      rows: [
        { name: "Retail digital", detail: "94 solicitudes con scoring listo", status: "En curso" },
        { name: "Convenios", detail: "28 casos pendientes de evidencia", status: "Bloqueado" },
        { name: "Hipotecario sandbox", detail: "16 casos para ensayo operativo", status: "Mock" },
      ],
    },
    priorizacion: {
      title: "Priorizacion",
      description: "Matriz temporal para evaluar orden de atencion y carga de trabajo sin backend real.",
      rows: [
        { name: "Alta prioridad", detail: "Ingresos mayores a 15k y SLA critico", status: "Activa" },
        { name: "Revision manual", detail: "Solicitudes con validaciones cruzadas", status: "Programada" },
        { name: "Reproceso", detail: "Casos con adjuntos incompletos", status: "Monitoreo" },
      ],
    },
    asignaciones: {
      title: "Asignaciones",
      description: "Distribucion simulada por equipo para validar densidad y estructura de la pantalla.",
      rows: [
        { name: "Mesa norte", detail: "63 expedientes a resolver", status: "Disponible" },
        { name: "Mesa premium", detail: "42 expedientes con scoring preferente", status: "Activa" },
        { name: "Soporte documental", detail: "18 expedientes observados", status: "Saturada" },
      ],
    },
    sla: {
      title: "SLA",
      description: "Panel de seguimiento para vencimientos y tiempos objetivo en modo placeholder.",
      rows: [
        { name: "Atencion inicial", detail: "Objetivo 15 minutos", status: "93% en rango" },
        { name: "Revision analista", detail: "Objetivo 4 horas", status: "87% en rango" },
        { name: "Resolucion final", detail: "Objetivo 24 horas", status: "Alerta" },
      ],
    },
    auditoria: {
      title: "Auditoria",
      description: "Bitacora visual de eventos internos para la futura integracion del servicio.",
      rows: [
        { name: "Cambio de prioridad", detail: "Actualizado por admin_riesgos", status: "Registrado" },
        { name: "Reasignacion", detail: "Movimiento entre mesas de analisis", status: "Validado" },
        { name: "Escalamiento", detail: "Caso con excepcion de politica", status: "Pendiente" },
      ],
    },
  },
  "data-model": {
    resumen: {
      title: "Resumen",
      description: "Workspace local para gobernanza visual de entidades, catalogos y calidad del dato.",
      rows: [
        { name: "Dominios activos", detail: "Cliente, solicitud y oferta", status: "Alineados" },
        { name: "Relaciones pendientes", detail: "2 cruces a validar en sandbox", status: "En revision" },
        { name: "Publicaciones", detail: "Ultima ventana de despliegue simulada", status: "Mock" },
      ],
    },
    entidades: {
      title: "Entidades",
      description: "Inventario base de estructuras administradas por el producto en esta version visual.",
      rows: [
        { name: "Cliente", detail: "57 atributos principales", status: "Publicada" },
        { name: "Solicitud", detail: "42 atributos operativos", status: "Borrador" },
        { name: "Oferta", detail: "19 atributos de salida", status: "Aprobada" },
      ],
    },
    relaciones: {
      title: "Relaciones",
      description: "Mapa de joins y dependencias funcionales presentado como Mock operativo.",
      rows: [
        { name: "Cliente -> Solicitud", detail: "Relacion 1:N con versionado visual", status: "Vigente" },
        { name: "Solicitud -> Oferta", detail: "Dependencia condicionada por workflow", status: "Analisis" },
        { name: "Cliente -> Score", detail: "Fuente externa pendiente de contrato", status: "Simulada" },
      ],
    },
    catalogos: {
      title: "Catalogos",
      description: "Gestion local de valores de referencia con copy y estructura enterprise.",
      rows: [
        { name: "Tipo de documento", detail: "8 valores homologados", status: "Activo" },
        { name: "Canal", detail: "5 valores para originacion", status: "En ajuste" },
        { name: "Segmento", detail: "4 categorias comerciales", status: "Aprobado" },
      ],
    },
    calidad: {
      title: "Calidad",
      description: "Indicadores placeholder para consistencia, completitud y trazabilidad de datos.",
      rows: [
        { name: "Completitud", detail: "97.4% de campos obligatorios", status: "Estable" },
        { name: "Consistencia", detail: "3 reglas locales con observaciones", status: "Alerta" },
        { name: "Trazabilidad", detail: "Linaje visual en preparacion", status: "Mock" },
      ],
    },
    publicacion: {
      title: "Publicacion",
      description: "Flujo de release visual para futuros artefactos de datos gobernados.",
      rows: [
        { name: "Ventana sandbox", detail: "Lista para validacion funcional", status: "Preparada" },
        { name: "Checklist negocio", detail: "Pendiente de firma", status: "Borrador" },
        { name: "Release notes", detail: "Version local no persistida", status: "Mock" },
      ],
    },
  },
};

function renderPlaceholder(routeSegment: string, serviceName: string, section: string) {
  const content = placeholderContent[routeSegment]?.[section] ?? placeholderContent[routeSegment]?.resumen;

  if (content === undefined) {
    return null;
  }

  return (
    <ServiceWorkspacePlaceholderPanel
      description={content.description}
      rows={content.rows}
      sectionTitle={content.title}
      serviceName={serviceName}
    />
  );
}

export function ServiceWorkspacePage() {
  const navigate = useNavigate();
  const { me } = useSessionContext();
  const { productCode, serviceKey, section, item } = useParams();

  if (me === null || productCode === undefined || serviceKey === undefined) {
    return <Navigate to="/productos" replace />;
  }

  const service = findVisibleServiceForRoles(me.roles, serviceKey);

  if (service === null) {
    return <Navigate to={`/productos/${productCode}/servicios`} replace />;
  }

  const definition = getServiceWorkspaceDefinition(service.routeSegment);

  if (definition === null) {
    return <Navigate to={`/productos/${productCode}/servicios`} replace />;
  }

  const resolvedProductCode = productCode;
  const resolvedService = service;

  const activeSection = section ?? definition.defaultSection;
  const activeItem = item ?? definition.defaultItem;

  function handleSelect(nextSection: string, nextItem?: string) {
    navigate(buildServiceWorkspacePath(resolvedProductCode, resolvedService.routeSegment, nextSection, nextItem));
  }

  return (
    <section className="service-workspace-page">
      <div className="service-workspace-breadcrumb">
        <span>Productos</span>
        <span>/</span>
        <span>{productCode}</span>
        <span>/</span>
        <span>{resolvedService.displayName}</span>
        <span>/</span>
        <strong>{activeItem ?? activeSection}</strong>
      </div>

      <div className="service-workspace-topbar">
        <div>
          <p className="eyebrow">Workspace</p>
          <h2 className="workspace-title">{resolvedService.displayName}</h2>
          <p className="workspace-hint">Navegacion lateral unificada y contenido contextual por seccion activa.</p>
        </div>
        <span className="service-workspace-status">{resolvedService.statusLabel}</span>
      </div>

      <div className={resolvedService.routeSegment === "decision-engine" ? "service-workspace-layout service-workspace-layout--with-inspector" : "service-workspace-layout"}>
        <ServiceWorkspaceSidebar
          activeItem={activeItem}
          activeSection={activeSection}
          groups={definition.groups}
          onSelect={handleSelect}
        />

        {resolvedService.routeSegment === "decision-engine" ? (
          <DecisionWorkspaceEmbedded />
        ) : (
          <div className="service-workspace-main">{renderPlaceholder(resolvedService.routeSegment, resolvedService.displayName, activeSection)}</div>
        )}
      </div>
    </section>
  );
}
