import { api } from "../api/client";
import type { AdminUser, AdminUserListPage } from "../types";

type Listener = () => void;

function createStore<T>(initial: T) {
  let state = initial;
  const listeners = new Set<Listener>();

  return {
    get: () => state,
    set: (next: T) => {
      state = next;
      listeners.forEach((l) => l());
    },
    subscribe: (listener: Listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

interface AdminUsersState {
  items: AdminUser[];
  nextCursor: string | null;
  loading: boolean;
}

const usersStore = createStore<AdminUsersState>({
  items: [],
  nextCursor: null,
  loading: false,
});

export const adminStore = {
  subscribe: usersStore.subscribe,
  getState: () => usersStore.get(),

  async fetchUsers(): Promise<void> {
    const current = usersStore.get();
    usersStore.set({ ...current, loading: true });

    const cursor = current.nextCursor;
    const url = cursor
      ? `/admin/users?cursor=${cursor}&limit=20`
      : "/admin/users?limit=20";

    const res = await api.get<AdminUserListPage>(url);
    if (!res.success) {
      usersStore.set({ ...current, loading: false });
      throw new Error(res.errors[0]?.detail || "Error al cargar usuarios");
    }

    usersStore.set({
      items: [...current.items, ...res.body.items],
      nextCursor: res.body.next_cursor,
      loading: false,
    });
  },

  async fetchUsersFresh(): Promise<void> {
    usersStore.set({ items: [], nextCursor: null, loading: true });

    const res = await api.get<AdminUserListPage>("/admin/users?limit=20");
    if (!res.success) {
      usersStore.set({ items: [], nextCursor: null, loading: false });
      throw new Error(res.errors[0]?.detail || "Error al cargar usuarios");
    }

    usersStore.set({
      items: res.body.items,
      nextCursor: res.body.next_cursor,
      loading: false,
    });
  },

  async blockUser(userId: string): Promise<void> {
    const res = await api.patch(`/admin/users/${userId}/block`);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al bloquear usuario");
    }
  },

  async unblockUser(userId: string): Promise<void> {
    const res = await api.patch(`/admin/users/${userId}/unblock`);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al desbloquear usuario");
    }
  },

  async assignAdmin(userId: string): Promise<void> {
    const res = await api.patch(`/admin/users/${userId}/admin`);
    if (!res.success) {
      throw new Error(
        res.errors[0]?.detail || "Error al asignar administrador",
      );
    }
  },

  async revokeAdmin(userId: string): Promise<void> {
    const res = await api.patch(`/admin/users/${userId}/revoke-admin`);
    if (!res.success) {
      throw new Error(
        res.errors[0]?.detail || "Error al revocar administrador",
      );
    }
  },
};
