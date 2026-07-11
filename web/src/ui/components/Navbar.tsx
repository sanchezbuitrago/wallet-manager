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
    { label: "Dashboard", path: "/" },
    { label: "Movements", path: "/movements" },
  ];

  return (
    <nav className="border-b border-noir-800 bg-noir-900">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <button
            onClick={() => setLocation("/")}
            className="text-lg font-bold tracking-tight text-noir-100"
          >
            WM
          </button>
          {navItems.map((item) => {
            const active = location === item.path;
            return (
              <button
                key={item.path}
                onClick={() => setLocation(item.path)}
                className={`text-sm transition-colors hover:text-noir-100 ${
                  active ? "text-noir-100 font-semibold" : "text-noir-400"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-4">
          {accounts.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-xs text-noir-500">Cuenta</label>
              <select
                value={selected?.id ?? ""}
                onChange={(e) => selectAccount(e.target.value)}
                className="rounded border border-noir-700 bg-noir-950 px-2 py-1.5 text-sm text-noir-300 focus:border-noir-400 focus:outline-none"
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.id}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            onClick={logout}
            className="rounded bg-noir-800 px-3 py-1.5 text-sm text-noir-300 transition-colors hover:bg-noir-700 hover:text-noir-100"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
