import { api } from "../api/client";
import type { AccountData } from "../types";

type Listener = () => void;
const listeners = new Set<Listener>();

interface AccountsState {
  items: AccountData[];
  selectedId: string | null;
}

let state: AccountsState = { items: [], selectedId: null };
let loading = false;
let error: string | null = null;

function notify() {
  listeners.forEach((l) => l());
}

export const accountsStore = {
  subscribe: (listener: Listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  getState: () => state,
  getLoading: () => loading,
  getError: () => error,

  getSelected: () => {
    if (!state.selectedId) return null;
    return state.items.find((a) => a.id === state.selectedId) ?? null;
  },

  selectAccount: (id: string) => {
    state = { ...state, selectedId: id };
    notify();
  },

  fetch: async () => {
    loading = true;
    error = null;
    notify();
    try {
      const res = await api.get<{ items: AccountData[] }>("/analytics/accounts");
      if (!res.success) {
        error = res.errors[0]?.detail || "Failed to load accounts";
        state = { items: [], selectedId: null };
      } else {
        const items = res.body.items;
        const selectedId = state.selectedId && items.some((a) => a.id === state.selectedId)
          ? state.selectedId
          : items[0]?.id ?? null;
        state = { items, selectedId };
        error = null;
      }
    } catch (e) {
      error = (e as Error).message;
      state = { items: [], selectedId: null };
    }
    loading = false;
    notify();
  },
};
