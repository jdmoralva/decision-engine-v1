import type { WorkspaceChannel, WorkspaceDraftRecord, WorkspaceNode, WorkspaceWorkflowSummary } from "./workspace-types";

export type WorkspaceState = WorkspaceDraftRecord & {
  governedWorkflows: {
    active: WorkspaceWorkflowSummary[];
    draft: WorkspaceWorkflowSummary[];
  };
  channels: WorkspaceChannel[];
  selectedParameterSetIds: string[];
  tests: string[];
  events: string[];
  notice: string | null;
  profileMenuOpen: boolean;
};

export type WorkspaceAction =
  | { type: "select-node"; nodeId: string }
  | { type: "move-selected-node" }
  | { type: "add-node" }
  | { type: "remove-selected-node" }
  | { type: "set-sidebar-item"; group: string; item: string }
  | { type: "set-governed-workflows"; active: WorkspaceWorkflowSummary[]; draft: WorkspaceWorkflowSummary[] }
  | { type: "toggle-parameter-set"; parameterSetId: string }
  | { type: "set-notice"; notice: string | null }
  | { type: "toggle-profile-menu" };

function nextNodeId(nodes: WorkspaceNode[]): string {
  return `node-${nodes.length + 1}`;
}

export function workspaceReducer(state: WorkspaceState, action: WorkspaceAction): WorkspaceState {
  switch (action.type) {
    case "select-node":
      return { ...state, selectedNodeId: action.nodeId, dirty: true };
    case "move-selected-node": {
      if (state.selectedNodeId === null || state.nodes === undefined) {
        return state;
      }

      return {
        ...state,
        dirty: true,
        nodes: state.nodes.map((node) =>
          node.id === state.selectedNodeId ? { ...node, x: node.x + 24, y: node.y + 12 } : node,
        ),
        executionHistory: [...(state.executionHistory ?? []), `Nodo ${state.selectedNodeId} movido`],
      };
    }
    case "add-node": {
      const nodes = state.nodes ?? [];
      const nextId = nextNodeId(nodes);
      return {
        ...state,
        dirty: true,
        selectedNodeId: nextId,
        nodes: [
          ...nodes,
          {
            id: nextId,
            name: `Nodo ${nodes.length + 1}`,
            type: "subworkflow",
            x: 180 + nodes.length * 20,
            y: 260,
            description: "Subworkflow local agregado en sesion.",
            executionMode: "Manual",
          },
        ],
      };
    }
    case "remove-selected-node": {
      if (state.selectedNodeId === null || state.nodes === undefined) {
        return state;
      }

      return {
        ...state,
        dirty: true,
        nodes: state.nodes.filter((node) => node.id !== state.selectedNodeId),
        connections: (state.connections ?? []).filter(
          (connection) =>
            connection.sourceNodeId !== state.selectedNodeId && connection.targetNodeId !== state.selectedNodeId,
        ),
        selectedNodeId: null,
      };
    }
    case "set-sidebar-item":
      return {
        ...state,
        activeSidebarGroup: action.group,
        activeSidebarItem: action.item,
      };
    case "set-governed-workflows":
      return {
        ...state,
        governedWorkflows: {
          active: action.active,
          draft: action.draft,
        },
      };
    case "toggle-parameter-set":
      return {
        ...state,
        selectedParameterSetIds: state.selectedParameterSetIds.includes(action.parameterSetId)
          ? state.selectedParameterSetIds.filter((item) => item !== action.parameterSetId)
          : [...state.selectedParameterSetIds, action.parameterSetId],
      };
    case "set-notice":
      return { ...state, notice: action.notice };
    case "toggle-profile-menu":
      return { ...state, profileMenuOpen: !state.profileMenuOpen };
    default:
      return state;
  }
}

export function buildInitialWorkspaceState(draft: WorkspaceDraftRecord): WorkspaceState {
  return {
    ...draft,
    nodes: draft.nodes ?? [],
    connections: draft.connections ?? [],
    executionHistory: draft.executionHistory ?? [],
    validationMessages: draft.validationMessages ?? [],
    governedWorkflows: {
      active: [],
      draft: [],
    },
    channels: [
      {
        id: "channel-1",
        name: "Canal originacion digital",
        statusLabel: "Borrador",
        workflowId: "wf-active",
        approvedParameterSetIds: ["param-1", "param-2"],
        compatibilityValidation: "Compatibilidad valida",
      },
    ],
    selectedParameterSetIds: ["param-1", "param-2"],
    tests: ["Champion vs challenger - originacion retail", "Prueba de stress - score bajo"],
    events: [
      "Consulta motor 2026-06-17 10:00 - Cliente 1020 - Resultado aprobado",
      "Consulta motor 2026-06-17 10:15 - Cliente 1042 - Revision manual",
    ],
    notice: null,
    profileMenuOpen: false,
  };
}
