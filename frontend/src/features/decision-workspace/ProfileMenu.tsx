type ProfileMenuProps = {
  isOpen: boolean;
  onToggle: () => void;
  onChangePassword: () => void;
  onShowPermissions: () => void;
  onLogout: () => void;
};

export function ProfileMenu({
  isOpen,
  onToggle,
  onChangePassword,
  onShowPermissions,
  onLogout,
}: ProfileMenuProps) {
  return (
    <div className="workspace-profile">
      <button aria-label="Abrir perfil de usuario" className="secondary-button" type="button" onClick={onToggle}>
        Perfil
      </button>
      {isOpen ? (
        <div className="workspace-profile-menu">
          <button aria-label="Cambiar contrasena" className="secondary-button" type="button" onClick={onChangePassword}>
            Cambiar contrasena
          </button>
          <button aria-label="Consultar permisos aprobados" className="secondary-button" type="button" onClick={onShowPermissions}>
            Consultar permisos aprobados
          </button>
          <button aria-label="Cerrar sesion workspace" className="secondary-button" type="button" onClick={onLogout}>
            Cerrar sesion
          </button>
        </div>
      ) : null}
    </div>
  );
}
