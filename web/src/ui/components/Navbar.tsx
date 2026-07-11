import { useAuth } from "../hooks/useAuth";
import { useAccounts, useAccountSelector } from "../hooks/useAccount";
import { useLocation } from "wouter";

export function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const [location, setLocation] = useLocation();
  const { accounts } = useAccounts();
  const { selected, selectAccount } = useAccountSelector();

  if (!isAuthenticated) return null;

  const navItems = [
    { label: "Resumen", path: "/" },
    { label: "Movimientos", path: "/movements" },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-noir-800/60 bg-noir-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-8">
          <button
            onClick={() => setLocation("/")}
            className="flex items-center gap-2 text-lg font-bold tracking-tight text-noir-100 transition-opacity hover:opacity-80"
          >
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-br from-noir-100 to-noir-300">
              <span className="text-xs font-bold text-noir-950">WM</span>
            </div>
          </button>
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const active = location === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => setLocation(item.path)}
                  className={`relative rounded-lg px-3 py-1.5 text-sm transition-all duration-200 ${
                    active
                      ? "bg-noir-800/60 text-noir-100 font-medium"
                      : "text-noir-400 hover:bg-noir-800/30 hover:text-noir-200"
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-3">
          {accounts.length > 0 && (
            <div className="flex items-center gap-2 rounded-lg border border-noir-800/40 bg-noir-900/40 px-3 py-1.5">
              <label className="text-xs text-noir-500">Cuenta</label>
              <select
                value={selected?.id ?? ""}
                onChange={(e) => selectAccount(e.target.value)}
                className="bg-transparent text-sm text-noir-300 focus:outline-none"
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.id} className="bg-noir-900">
                    {a.id}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            onClick={logout}
            className="rounded-lg px-3 py-1.5 text-sm text-noir-400 transition-all duration-200 hover:bg-noir-800/60 hover:text-noir-200"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </nav>
  );
}
