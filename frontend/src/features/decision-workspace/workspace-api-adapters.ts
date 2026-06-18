import type { EngineAdminApiClient, ProfilePermissionResponse, WorkflowResponse } from "../../services/engine-admin-api";
import { getStatusLabel } from "../platform/status-labels";
import type { WorkspaceWorkflowSummary } from "./workspace-types";

function toWorkflowSummary(item: WorkflowResponse): WorkspaceWorkflowSummary {
  return {
    id: item.id,
    workflowCode: item.workflowCode,
    name: item.name,
    statusLabel: getStatusLabel(item.status),
    source: "backend",
  };
}

export async function loadGovernedWorkflows(
  client: EngineAdminApiClient,
  productCode: string,
): Promise<{ active: WorkspaceWorkflowSummary[]; draft: WorkspaceWorkflowSummary[] }> {
  const [active, draft] = await Promise.all([
    client.listWorkflows(productCode),
    client.listWorkflows(productCode, "draft"),
  ]);

  return {
    active: active.items.map(toWorkflowSummary),
    draft: draft.items.map(toWorkflowSummary),
  };
}

export async function loadApprovedPermissions(
  client: EngineAdminApiClient,
  roleCode: string,
): Promise<ProfilePermissionResponse> {
  return client.getProfilePermissions(roleCode);
}
