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

        <div className="flex items-center gap-2">
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
            onClick={() => setLocation("/settings")}
            className="rounded-lg px-2 py-1.5 text-noir-400 transition-all duration-200 hover:bg-noir-800/60 hover:text-noir-200"
            title="Configuracion"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-5 w-5">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
            </svg>
          </button>
          <button
            onClick={logout}
            className="rounded-lg px-3 py-1.5 text-sm text-noir-400 transition-all duration-200 hover:bg-noir-800/60 hover:text-noir-200"
          >
            Cerrar sesion
          </button>
        </div>
      </div>
    </nav>
  );
}
