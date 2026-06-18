import type { WorkspaceDraftLocator, WorkspaceDraftRecord, WorkspaceViewport } from "./workspace-types";

const WORKSPACE_STORAGE_PREFIX = "decision-engine.workspace";

function isViewport(value: unknown): value is WorkspaceViewport {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.x === "number" &&
    typeof candidate.y === "number" &&
    typeof candidate.zoom === "number"
  );
}

function isWorkspaceDraftRecord(value: unknown): value is WorkspaceDraftRecord {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.productCode === "string" &&
    typeof candidate.serviceKey === "string" &&
    typeof candidate.workflowId === "string" &&
    (typeof candidate.workflowCode === "string" || candidate.workflowCode === null) &&
    typeof candidate.title === "string" &&
    typeof candidate.activeSidebarGroup === "string" &&
    typeof candidate.activeSidebarItem === "string" &&
    (typeof candidate.selectedNodeId === "string" || candidate.selectedNodeId === null) &&
    typeof candidate.dirty === "boolean" &&
    isViewport(candidate.viewport)
  );
}

export function buildWorkspaceDraftStorageKey(locator: WorkspaceDraftLocator): string {
  return `${WORKSPACE_STORAGE_PREFIX}.${locator.productCode}.${locator.serviceKey}.${locator.workflowId}`;
}

export function saveWorkspaceDraft(draft: WorkspaceDraftRecord): void {
  sessionStorage.setItem(buildWorkspaceDraftStorageKey(draft), JSON.stringify(draft));
}

export function loadWorkspaceDraft(locator: WorkspaceDraftLocator): WorkspaceDraftRecord | null {
  const rawValue = sessionStorage.getItem(buildWorkspaceDraftStorageKey(locator));
  if (rawValue === null) {
    return null;
  }

  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!isWorkspaceDraftRecord(parsed)) {
      clearWorkspaceDraft(locator);
      return null;
    }
    return parsed;
  } catch {
    clearWorkspaceDraft(locator);
    return null;
  }
}

export function clearWorkspaceDraft(locator: WorkspaceDraftLocator): void {
  sessionStorage.removeItem(buildWorkspaceDraftStorageKey(locator));
}

export function clearAllWorkspaceDrafts(): void {
  const keysToRemove: string[] = [];

  for (let index = 0; index < sessionStorage.length; index += 1) {
    const key = sessionStorage.key(index);
    if (key !== null && key.startsWith(WORKSPACE_STORAGE_PREFIX)) {
      keysToRemove.push(key);
    }
  }

  for (const key of keysToRemove) {
    sessionStorage.removeItem(key);
  }
}
