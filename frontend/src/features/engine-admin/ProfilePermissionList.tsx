import type { PermissionResponse } from "../../services/engine-admin-api";

type Props = {
  permissions: PermissionResponse[];
};

export function ProfilePermissionList({ permissions }: Props) {
  if (permissions.length === 0) {
    return <p className="workspace-hint">Sin permisos asignados.</p>;
  }

  return (
    <>
      <p className="workspace-hint">Permisos efectivos cargados para el perfil seleccionado.</p>
      <ul className="feature-list">
      {permissions.map((permission) => (
        <li key={permission.code}>
          <strong>{permission.code}</strong>
          {permission.description ? `: ${permission.description}` : ""}
        </li>
      ))}
      </ul>
    </>
  );
}
