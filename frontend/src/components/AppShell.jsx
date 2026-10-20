import { NavLink, Outlet } from "react-router-dom";

import { useSession } from "../session.jsx";
import Wordmark from "./Wordmark.jsx";

/**
 * Marco de la app: encabezado con la marca y el usuario, y las pestañas
 * del rol. En el celular las pestañas del alumno quedan abajo, a mano del
 * pulgar; la cafetería las tiene arriba porque usa una pantalla grande.
 */
export default function AppShell({ tabs, wide = false }) {
  const { user, logout } = useSession();
  const firstName = user.full_name.split(" ")[0];

  return (
    <div className={`shell ${wide ? "shell--wide" : "shell--narrow"}`}>
      <header className="topbar">
        <Wordmark />
        <div className="topbar__user">
          <span className="topbar__name">{firstName}</span>
          <button type="button" className="link-button" onClick={logout}>
            Salir
          </button>
        </div>
      </header>

      <nav className="tabs" aria-label="Secciones">
        {tabs.map((tab) => (
          <NavLink key={tab.to} to={tab.to} end={tab.end} className="tabs__link">
            {tab.label}
          </NavLink>
        ))}
      </nav>

      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}
