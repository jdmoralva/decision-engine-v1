import { useState } from "react";

import {
  EngineAdminApiClient,
  EngineAdminWorkspaceState,
  type PermissionResponse,
} from "../../services/engine-admin-api";
import { ProfilePermissionEditor } from "./ProfilePermissionEditor";
import { ProfilePermissionList } from "./ProfilePermissionList";

type Props = {
  client: EngineAdminApiClient;
  workspace: EngineAdminWorkspaceState;
  onWorkspaceChange: (patch: Partial<EngineAdminWorkspaceState>) => void;
  onNotice: (message: string) => void;
};

export function ProfilePermissionsPage({ client, workspace, onWorkspaceChange, onNotice }: Props) {
  const [permissions, setPermissions] = useState<PermissionResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  async function handleLoadPermissions() {
    setIsLoading(true);
    try {
      const response = await client.getProfilePermissions(workspace.selectedRoleCode);
      setPermissions(response.permissions);
      onWorkspaceChange({
        selectedPermissionCodes: response.permissions.map((permission) => permission.code),
      });
      onNotice(`Permisos cargados para ${response.roleCode}.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudieron cargar los permisos.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleReplacePermissions(permissionCodes: string[]) {
    try {
      const response = await client.replaceProfilePermissions(workspace.selectedRoleCode, permissionCodes);
      setPermissions(response.permissions);
      onWorkspaceChange({ selectedPermissionCodes: permissionCodes });
      onNotice(`Permisos actualizados para ${response.roleCode}.`);
    } catch (error) {
      onNotice(error instanceof Error ? error.message : "No se pudieron actualizar los permisos.");
    }
  }

  return (
    <section className="workspace-card">
      <h2>Perfiles y permisos</h2>
      <div className="action-row">
        <button className="secondary-button" type="button" onClick={handleLoadPermissions} disabled={isLoading}>
          {isLoading ? "Cargando..." : "Cargar permisos actuales"}
        </button>
      </div>
      <ProfilePermissionEditor
        roleCode={workspace.selectedRoleCode}
        initialPermissionCodes={workspace.selectedPermissionCodes}
        onRoleCodeChange={(roleCode) => onWorkspaceChange({ selectedRoleCode: roleCode })}
        onSubmit={handleReplacePermissions}
      />
      <ProfilePermissionList permissions={permissions} />
    </section>
  );
}
