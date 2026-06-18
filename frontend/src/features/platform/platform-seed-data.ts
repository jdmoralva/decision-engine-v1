import type { PlatformProduct, PlatformService } from "./catalog-types";

export const platformProducts: PlatformProduct[] = [
  {
    productCode: "PLD",
    name: "PLD",
    environmentLabel: "Produccion",
    environmentTone: "production",
    quickActions: [
      { key: "services", label: "Servicios" },
      { key: "configuration", label: "Configuracion" },
      { key: "validation", label: "Validacion" },
      { key: "deployment", label: "Despliegue" },
    ],
    menuActions: [
      { key: "rename", label: "Renombrar" },
      { key: "duplicate", label: "Duplicar" },
      { key: "export", label: "Exportar" },
      { key: "delete", label: "Eliminar" },
    ],
    source: "seed",
  },
  {
    productCode: "Hipotecario",
    name: "Hipotecario",
    environmentLabel: "Sandbox",
    environmentTone: "staging",
    quickActions: [
      { key: "services", label: "Servicios" },
      { key: "configuration", label: "Configuracion" },
      { key: "validation", label: "Validacion" },
      { key: "deployment", label: "Despliegue" },
    ],
    menuActions: [
      { key: "rename", label: "Renombrar" },
      { key: "duplicate", label: "Duplicar" },
      { key: "export", label: "Exportar" },
      { key: "delete", label: "Eliminar" },
    ],
    source: "seed",
  },
];

export const platformServices: PlatformService[] = [
  {
    serviceKey: "CreditApplications",
    routeSegment: "credit-applications",
    displayName: "Bandeja de solicitudes",
    description: "Registro y seguimiento de solicitudes de credito.",
    statusLabel: "Disponible",
    iconKey: "queue",
    visibilityRoles: ["analista", "evaluador", "admin", "admin_negocio", "admin_riesgos"],
    supportsOpen: true,
  },
  {
    serviceKey: "DecisionEngine",
    routeSegment: "decision-engine",
    displayName: "Motor de decisiones",
    description: "Workspace visual para reglas, workflows y pruebas.",
    statusLabel: "Disponible",
    iconKey: "engine",
    visibilityRoles: ["admin", "admin_negocio", "admin_riesgos"],
    supportsOpen: true,
  },
  {
    serviceKey: "DataModel",
    routeSegment: "data-model",
    displayName: "Modelo de datos",
    description: "Administracion visual de estructuras y catalogos de datos.",
    statusLabel: "Disponible",
    iconKey: "data",
    visibilityRoles: ["admin", "admin_negocio", "admin_riesgos"],
    supportsOpen: true,
  },
];
