export type WorkspaceViewport = {
  x: number;
  y: number;
  zoom: number;
};

export type WorkspaceNode = {
  id: string;
  name: string;
  type: string;
  x: number;
  y: number;
  description?: string;
  inputVariables?: string[];
  outputVariables?: string[];
  decisionLogic?: string;
  errorHandling?: string;
  executionMode?: string;
};

export type WorkspaceConnection = {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  label: string;
};

export type WorkspaceWorkflowSummary = {
  id: string;
  workflowCode: string;
  name: string;
  statusLabel: string;
  source: "backend" | "session";
};

export type WorkspaceChannel = {
  id: string;
  name: string;
  statusLabel: string;
  workflowId: string;
  approvedParameterSetIds: string[];
  compatibilityValidation: string;
};

export type WorkspaceDraftLocator = {
  productCode: string;
  serviceKey: string;
  workflowId: string;
};

export type WorkspaceDraftRecord = WorkspaceDraftLocator & {
  workflowCode: string | null;
  title: string;
  activeSidebarGroup: string;
  activeSidebarItem: string;
  selectedNodeId: string | null;
  viewport: WorkspaceViewport;
  dirty: boolean;
  nodes?: WorkspaceNode[];
  connections?: WorkspaceConnection[];
  executionHistory?: string[];
  validationMessages?: string[];
};
