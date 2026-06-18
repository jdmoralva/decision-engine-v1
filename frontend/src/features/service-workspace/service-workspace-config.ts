import type { ServiceWorkspaceDefinition } from "./service-workspace-types";

export const serviceWorkspaceDefinitions: Record<string, ServiceWorkspaceDefinition> = {
  "credit-applications": {
    defaultSection: "resumen",
    groups: [
      {
        key: "overview",
        label: "Workspace",
        items: [{ key: "summary", label: "Resumen", section: "resumen" }],
      },
      {
        key: "operations",
        label: "Operaciones",
        items: [
          { key: "queue", label: "Cola activa", section: "cola-activa" },
          { key: "prioritization", label: "Priorizacion", section: "priorizacion" },
          { key: "assignments", label: "Asignaciones", section: "asignaciones" },
          { key: "sla", label: "SLA", section: "sla" },
          { key: "audit", label: "Auditoria", section: "auditoria" },
        ],
      },
    ],
  },
  "data-model": {
    defaultSection: "resumen",
    groups: [
      {
        key: "overview",
        label: "Workspace",
        items: [{ key: "summary", label: "Resumen", section: "resumen" }],
      },
      {
        key: "modeling",
        label: "Gobernanza",
        items: [
          { key: "entities", label: "Entidades", section: "entidades" },
          { key: "relationships", label: "Relaciones", section: "relaciones" },
          { key: "catalogs", label: "Catalogos", section: "catalogos" },
          { key: "quality", label: "Calidad", section: "calidad" },
          { key: "publication", label: "Publicacion", section: "publicacion" },
        ],
      },
    ],
  },
  "decision-engine": {
    defaultSection: "workflows",
    groups: [
      {
        key: "overview",
        label: "Workspace",
        items: [{ key: "summary", label: "Resumen", section: "resumen" }],
      },
      {
        key: "business-rules",
        label: "Reglas de Negocio",
        items: [
          { key: "channels", label: "Canales", section: "canales", ariaLabel: "channels" },
          { key: "workflows", label: "Workflows", section: "workflows" },
          { key: "testing", label: "Testing", section: "testing", ariaLabel: "testing" },
          { key: "events", label: "Eventos", section: "eventos", ariaLabel: "events" },
        ],
      },
      {
        key: "parameters",
        label: "Parametros",
        items: [
          { key: "internal-limits", label: "Limites internos", section: "parametros", item: "limites-internos" },
          { key: "global-limits", label: "Limites globales", section: "parametros", item: "limites-globales" },
          { key: "autonomy-levels", label: "Niveles de autonomia", section: "parametros", item: "niveles-autonomia" },
        ],
      },
      {
        key: "data",
        label: "Data",
        items: [
          { key: "import-dataset", label: "Importar dataset", section: "data", item: "importar-dataset" },
          { key: "configure-relationships", label: "Configurar relaciones", section: "data", item: "configurar-relaciones" },
          { key: "manage-measures", label: "Administrar medidas", section: "data", item: "administrar-medidas" },
          { key: "manage-catalogs", label: "Administrar catalogos", section: "data", item: "administrar-catalogos" },
        ],
      },
    ],
  },
};

export function getServiceWorkspaceDefinition(routeSegment: string): ServiceWorkspaceDefinition | null {
  return serviceWorkspaceDefinitions[routeSegment] ?? null;
}

export function buildServiceWorkspacePath(
  productCode: string,
  routeSegment: string,
  section?: string,
  item?: string,
): string {
  const base = `/productos/${productCode}/servicios/${routeSegment}`;

  if (section === undefined) {
    return base;
  }

  if (item === undefined) {
    return `${base}/${section}`;
  }

  return `${base}/${section}/${item}`;
}
