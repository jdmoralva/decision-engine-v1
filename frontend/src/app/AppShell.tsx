import type { ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useSessionContext } from "./session-context";

type AppShellProps = {
  children: ReactNode;
};

function isActivePath(currentPath: string, targetPath: string): boolean {
  if (targetPath === "/productos") {
    return currentPath === "/" || currentPath.startsWith("/productos");
  }

  return currentPath === targetPath;
}

export function AppShell({ children }: AppShellProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { me, token, status, canManageCurrentSession, logout } = useSessionContext();

  function navigateTo(path: string): void {
    navigate(path);
  }

  function handleLogout(): void {
    logout();
    navigate("/login");
  }

  return (
    <main className="shell">
      <section className="card auth-card">
        <div className="auth-hero">
          <p className="eyebrow">Decision Engine</p>
          <h1>{me === null ? "Inicio de sesion" : "Plataforma visual de decision"}</h1>
          <p className="lead">
            {me === null
              ? "Prueba el acceso real con el usuario administrador sembrado en la base local."
              : "Explora productos, servicios y los accesos disponibles segun el rol autenticado."}
          </p>
        </div>

        {me === null ? children : null}

        <aside className="session-panel">
          <h2>Estado de sesion</h2>
          {status === "restoring" ? <p className="session-empty">Restaurando sesion...</p> : null}

          {status !== "restoring" && me ? (
            <>
              <p className="success-banner">Acceso correcto.</p>
              <dl className="session-grid">
                <div>
                  <dt>Usuario</dt>
                  <dd>{me.username}</dd>
                </div>
                <div>
                  <dt>Nombre</dt>
                  <dd>{me.displayName ?? "Sin nombre"}</dd>
                </div>
                <div>
                  <dt>Roles</dt>
                  <dd>{me.roles.join(", ")}</dd>
                </div>
                <div>
                  <dt>Token</dt>
                  <dd className="token-preview">{token}</dd>
                </div>
              </dl>
              <div className="tab-strip">
                <button
                  className={isActivePath(location.pathname, "/productos") ? "primary-button" : "secondary-button"}
                  type="button"
                  onClick={() => navigateTo("/productos")}
                >
                  Productos
                </button>
                <button
                  className={isActivePath(location.pathname, "/evaluaciones") ? "primary-button" : "secondary-button"}
                  type="button"
                  onClick={() => navigateTo("/evaluaciones")}
                >
                  Evaluaciones
                </button>
                <button
                  className={isActivePath(location.pathname, "/solicitudes") ? "primary-button" : "secondary-button"}
                  type="button"
                  onClick={() => navigateTo("/solicitudes")}
                >
                  Solicitudes
                </button>
                {canManageCurrentSession ? (
                  <button
                    className={isActivePath(location.pathname, "/admin") ? "primary-button" : "secondary-button"}
                    type="button"
                    onClick={() => navigateTo("/admin")}
                  >
                    Motor
                  </button>
                ) : null}
              </div>
              <button className="secondary-button" type="button" onClick={handleLogout}>
                Cerrar sesion
              </button>
            </>
          ) : null}

          {status === "anonymous" ? (
            <p className="session-empty">
              Aun no hay una sesion activa. Usa el formulario para autenticarte.
            </p>
          ) : null}
        </aside>

        <ul className="feature-list">
          <li>Login obligatorio y restauracion de sesion</li>
          <li>Catalogo multiproducto visible</li>
          <li>Navegacion protegida hacia servicios</li>
          <li>Integracion gradual con modulos operativos</li>
        </ul>

        {me ? children : null}
      </section>
    </main>
  );
}
