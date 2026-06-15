import { FormEvent, useEffect, useState } from "react";

type Props = {
  roleCode: string;
  initialPermissionCodes: string[];
  onRoleCodeChange: (roleCode: string) => void;
  onSubmit: (permissionCodes: string[]) => Promise<void>;
};

export function ProfilePermissionEditor({
  roleCode,
  initialPermissionCodes,
  onRoleCodeChange,
  onSubmit,
}: Props) {
  const [rawPermissions, setRawPermissions] = useState(initialPermissionCodes.join(", "));
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setRawPermissions(initialPermissionCodes.join(", "));
  }, [initialPermissionCodes, roleCode]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      const permissionCodes = rawPermissions
        .split(",")
        .map((value) => value.trim())
        .filter((value) => value.length > 0);
      await onSubmit(permissionCodes);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="admin-form" onSubmit={handleSubmit}>
      <label className="field">
        <span>Perfil</span>
        <select value={roleCode} onChange={(event) => onRoleCodeChange(event.target.value)}>
          <option value="admin_negocio">Administrador de negocio</option>
          <option value="admin_riesgos">Administrador de riesgos</option>
          <option value="plataforma">Plataforma</option>
          <option value="admin">Administrador</option>
        </select>
      </label>
      <label className="field">
        <span>Permisos</span>
        <textarea
          value={rawPermissions}
          onChange={(event) => setRawPermissions(event.target.value)}
          rows={5}
          placeholder="administrar_productos, consultar_auditoria"
        />
      </label>
      <button className="primary-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Guardando..." : "Guardar permisos"}
      </button>
    </form>
  );
}
