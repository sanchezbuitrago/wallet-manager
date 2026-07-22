import { useLocation } from "wouter";
import { authStore } from "../../core/stores/auth.store";

export function AdminNavbar() {
  const [, setLocation] = useLocation();

  function handleLogout() {
    authStore.logout();
    setLocation("/login");
  }

  function handleLogoutAdmin() {
    authStore.logout();
    setLocation("/admin/login");
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-noir-800/60 bg-noir-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-8">
          <button
            onClick={handleLogout}
            className="rounded-lg border border-noir-700 bg-noir-800/50 px-3 py-1.5 text-xs font-medium text-noir-300 transition-colors hover:bg-noir-700/50 hover:text-noir-100"
          >
            Ir a la app de usuarios
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-amber-400">Admin</span>
          <button
            onClick={handleLogoutAdmin}
            className="rounded-lg px-3 py-1.5 text-sm text-noir-400 transition-all duration-200 hover:bg-noir-800/60 hover:text-noir-200"
          >
            Cerrar sesion
          </button>
        </div>
      </div>
    </nav>
  );
}
