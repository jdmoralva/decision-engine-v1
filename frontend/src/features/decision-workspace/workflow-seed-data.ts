import type {
  WorkspaceChannel,
  WorkspaceConnection,
  WorkspaceDraftRecord,
  WorkspaceNode,
  WorkspaceViewport,
} from "./workspace-types";

export const defaultWorkspaceViewport: WorkspaceViewport = {
  x: 0,
  y: 0,
  zoom: 1,
};

export const seededWorkflowNodes: WorkspaceNode[] = [
  {
    id: "node-start",
    name: "Inicio",
    type: "inicio",
    x: 80,
    y: 100,
    description: "Punto inicial del flujo.",
    inputVariables: ["solicitud"],
    outputVariables: ["cliente"],
    decisionLogic: "Inicializar el contexto.",
    errorHandling: "Registrar incidente y detener.",
    executionMode: "Secuencial",
  },
  {
    id: "node-identity",
    name: "Validacion de identidad",
    type: "regla",
    x: 260,
    y: 100,
    description: "Valida identidad y consistencia documental.",
    inputVariables: ["cliente", "documento"],
    outputVariables: ["identidad_validada"],
    decisionLogic: "Comparar documento y biometria.",
    errorHandling: "Enviar a revision manual.",
    executionMode: "Secuencial",
  },
  {
    id: "node-score",
    name: "Verificacion de score",
    type: "score",
    x: 470,
    y: 100,
    description: "Consulta score y politicas de endeudamiento.",
    inputVariables: ["identidad_validada"],
    outputVariables: ["score_cliente"],
    decisionLogic: "Evaluar score minimo y perfil de deuda.",
    errorHandling: "Asignar score neutral.",
    executionMode: "Secuencial",
  },
  {
    id: "node-policy",
    name: "Aplicacion de politica",
    type: "politica",
    x: 680,
    y: 100,
    description: "Aplica politica aprobada de oferta y riesgo.",
    inputVariables: ["score_cliente"],
    outputVariables: ["oferta_preliminar"],
    decisionLogic: "Seleccionar politica activa.",
    errorHandling: "Pasar a revision manual.",
    executionMode: "Secuencial",
  },
  {
    id: "node-end",
    name: "Aprobacion",
    type: "fin",
    x: 890,
    y: 100,
    description: "Fin exitoso del workflow.",
    inputVariables: ["oferta_preliminar"],
    outputVariables: ["resultado"],
    decisionLogic: "Confirmar aprobacion.",
    errorHandling: "Ninguno.",
    executionMode: "Secuencial",
  },
];

export const seededWorkflowConnections: WorkspaceConnection[] = [
  { id: "edge-1", sourceNodeId: "node-start", targetNodeId: "node-identity", label: "continuar" },
  { id: "edge-2", sourceNodeId: "node-identity", targetNodeId: "node-score", label: "si" },
  { id: "edge-3", sourceNodeId: "node-score", targetNodeId: "node-policy", label: "aprobado" },
  { id: "edge-4", sourceNodeId: "node-policy", targetNodeId: "node-end", label: "continuar" },
];

export const seededChannels: WorkspaceChannel[] = [
  {
    id: "channel-1",
    name: "Canal originacion digital",
    statusLabel: "Borrador",
    workflowId: "wf-active",
    approvedParameterSetIds: ["param-1", "param-2"],
    compatibilityValidation: "Compatibilidad valida",
  },
];

export const seededTests = [
  "Champion vs challenger - originacion retail",
  "Prueba de stress - score bajo",
];

export const seededEvents = [
  "Consulta motor 2026-06-17 10:00 - Cliente 1020 - Resultado aprobado",
  "Consulta motor 2026-06-17 10:15 - Cliente 1042 - Revision manual",
];

export const workspaceSidebar = {
  "Reglas de Negocio": [
    { key: "channels", label: "channels" },
    { key: "workflows", label: "workflows" },
    { key: "testing", label: "testing" },
    { key: "events", label: "events" },
  ],
  Parametros: [
    { key: "limites-internos", label: "Limites internos" },
    { key: "limites-globales", label: "Limites globales" },
    { key: "niveles-autonomia", label: "Niveles de autonomia" },
  ],
  Data: [
    { key: "importar-dataset", label: "Importar dataset" },
    { key: "configurar-relaciones", label: "Configurar relaciones" },
    { key: "administrar-medidas", label: "Administrar medidas" },
    { key: "administrar-catalogos", label: "Administrar catalogos" },
  ],
} as const;

export function createSeededWorkspaceDraft(productCode: string): WorkspaceDraftRecord {
  return {
    productCode,
    serviceKey: "DecisionEngine",
    workflowId: "wf-local-originacion",
    workflowCode: "originacion",
    title: "Workflow originacion",
    activeSidebarGroup: "Reglas de Negocio",
    activeSidebarItem: "workflows",
    selectedNodeId: null,
    viewport: defaultWorkspaceViewport,
    dirty: false,
    nodes: seededWorkflowNodes,
    connections: seededWorkflowConnections,
    executionHistory: ["Workflow inicializado"],
    validationMessages: ["Compatibilidad valida"],
  };
}
