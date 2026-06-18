import { createContext, useContext, useEffect, useMemo, useReducer, type ReactNode } from "react";

import { saveWorkspaceDraft } from "./workspace-session";
import { buildInitialWorkspaceState, workspaceReducer, type WorkspaceAction, type WorkspaceState } from "./workspace-reducer";
import type { WorkspaceDraftRecord } from "./workspace-types";

type WorkspaceContextValue = {
  state: WorkspaceState;
  dispatch: React.Dispatch<WorkspaceAction>;
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ draft, children }: { draft: WorkspaceDraftRecord; children: ReactNode }) {
  const [state, dispatch] = useReducer(workspaceReducer, draft, buildInitialWorkspaceState);

  useEffect(() => {
    saveWorkspaceDraft({
      productCode: state.productCode,
      serviceKey: state.serviceKey,
      workflowId: state.workflowId,
      workflowCode: state.workflowCode,
      title: state.title,
      activeSidebarGroup: state.activeSidebarGroup,
      activeSidebarItem: state.activeSidebarItem,
      selectedNodeId: state.selectedNodeId,
      viewport: state.viewport,
      dirty: state.dirty,
      nodes: state.nodes,
      connections: state.connections,
      executionHistory: state.executionHistory,
      validationMessages: state.validationMessages,
    });
  }, [state]);

  const value = useMemo(() => ({ state, dispatch }), [state]);

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspaceContext(): WorkspaceContextValue {
  const context = useContext(WorkspaceContext);
  if (context === null) {
    throw new Error("useWorkspaceContext must be used within WorkspaceProvider.");
  }

  return context;
}
