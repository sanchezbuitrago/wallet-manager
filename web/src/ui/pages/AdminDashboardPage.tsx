import { useEffect, useState, useSyncExternalStore } from "react";
import { useLocation } from "wouter";
import { adminStore } from "../../core/stores/admin.store";
import { useAdminAuth } from "../hooks/useAdminAuth";

export function AdminDashboardPage() {
  const { isAuthenticated, isAdmin, profile, loading: authLoading } = useAdminAuth();
  const [, setLocation] = useLocation();
  const [error, setError] = useState("");
  const [actionBusy, setActionBusy] = useState<string | null>(null);

  const state = useSyncExternalStore(
    adminStore.subscribe,
    adminStore.getState,
    adminStore.getState,
  );
  const users = state.items;
  const nextCursor = state.nextCursor;
  const loading = state.loading;

  useEffect(() => {
    if (isAuthenticated && isAdmin === true) {
      adminStore.fetchUsersFresh().catch((err) => {
        setError((err as Error).message);
      });
    }
  }, [isAuthenticated, isAdmin]);

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || isAdmin === false)) {
      setLocation("/admin/login");
    }
  }, [authLoading, isAuthenticated, isAdmin, setLocation]);

  async function handleAction(
    action: string,
    userId: string,
    fn: () => Promise<void>,
  ) {
    setActionBusy(`${action}-${userId}`);
    setError("");
    try {
      await fn();
      await adminStore.fetchUsersFresh();
    } catch (err) {
      setError((err as Error).message);
    }
    setActionBusy(null);
  }

  function formatDate(timestamp: number | null): string {
    if (!timestamp) return "-";
    const date = new Date(timestamp * 1000);
    return date.toLocaleString("es-CO", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  if (authLoading || !isAuthenticated || isAdmin !== true) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-noir-600 border-t-noir-200" />
      </div>
    );
  }

  return (
    <div>
      <h1 className="section-title mb-6">Usuarios</h1>

      {error && (
        <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-noir-800/60 text-xs uppercase tracking-wider text-noir-400">
                <th className="px-4 py-3">Nombre</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Telefono</th>
                <th className="px-4 py-3">Estado</th>
                <th className="px-4 py-3">Admin</th>
                <th className="px-4 py-3">Ultimo login</th>
                <th className="px-4 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr
                  key={user.id}
                  className="border-b border-noir-800/30 transition-colors hover:bg-noir-800/20"
                >
                  <td className="px-4 py-3 text-noir-200">
                    {user.first_names} {user.last_names}
                  </td>
                  <td className="px-4 py-3 text-noir-300">{user.email}</td>
                  <td className="px-4 py-3 text-noir-300">
                    {user.phone_number.country_code} {user.phone_number.number}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                        user.status === "ACTIVE"
                          ? "bg-green-500/10 text-green-400"
                          : user.status === "BLOCKED"
                            ? "bg-red-500/10 text-red-400"
                            : "bg-yellow-500/10 text-yellow-400"
                      }`}
                    >
                      {user.status === "ACTIVE"
                        ? "Activo"
                        : user.status === "BLOCKED"
                          ? "Bloqueado"
                          : "Pendiente"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {user.is_admin ? (
                      <span className="inline-flex items-center rounded-full bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-400">
                        Admin
                      </span>
                    ) : (
                      <span className="text-noir-500">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-noir-400">
                    {formatDate(user.last_login)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {user.id === profile?.id ? (
                        <span className="text-xs text-noir-500">Tu</span>
                      ) : (
                        <>
                          {user.status === "BLOCKED" ? (
                            <button
                              disabled={actionBusy === `unblock-${user.id}`}
                              onClick={() =>
                                handleAction("unblock", user.id, () =>
                                  adminStore.unblockUser(user.id),
                                )
                              }
                              className="rounded-md border border-green-500/30 bg-green-500/10 px-3 py-1.5 text-xs font-medium text-green-400 transition-colors hover:bg-green-500/20"
                            >
                              {actionBusy === `unblock-${user.id}`
                                ? "..."
                                : "Desbloquear"}
                            </button>
                          ) : user.status === "ACTIVE" ? (
                            <button
                              disabled={actionBusy === `block-${user.id}`}
                              onClick={() =>
                                handleAction("block", user.id, () =>
                                  adminStore.blockUser(user.id),
                                )
                              }
                              className="rounded-md border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/20"
                            >
                              {actionBusy === `block-${user.id}` ? "..." : "Bloquear"}
                            </button>
                          ) : null}

                          {user.is_admin ? (
                            <button
                              disabled={actionBusy === `revoke-${user.id}`}
                              onClick={() =>
                                handleAction("revoke", user.id, () =>
                                  adminStore.revokeAdmin(user.id),
                                )
                              }
                              className="rounded-md border border-noir-600 bg-noir-800/50 px-3 py-1.5 text-xs font-medium text-noir-300 transition-colors hover:bg-noir-700/50"
                            >
                              {actionBusy === `revoke-${user.id}`
                                ? "..."
                                : "Revocar admin"}
                            </button>
                          ) : (
                            <button
                              disabled={actionBusy === `admin-${user.id}`}
                              onClick={() =>
                                handleAction("admin", user.id, () =>
                                  adminStore.assignAdmin(user.id),
                                )
                              }
                              className="rounded-md border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-medium text-amber-400 transition-colors hover:bg-amber-500/20"
                            >
                              {actionBusy === `admin-${user.id}`
                                ? "..."
                                : "Hacer admin"}
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {users.length === 0 && !loading && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-4 py-8 text-center text-noir-500"
                  >
                    No hay usuarios registrados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {nextCursor && (
          <div className="border-t border-noir-800/30 px-4 py-3">
            <button
              disabled={loading}
              onClick={() =>
                adminStore.fetchUsers().catch((err) => {
                  setError((err as Error).message);
                })
              }
              className="btn-ghost w-full"
            >
              {loading ? "Cargando..." : "Cargar mas"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
