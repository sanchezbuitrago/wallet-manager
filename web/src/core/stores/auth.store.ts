import { api } from "../api/client";
import type { LoginRequest, LoginResponse } from "../types";

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

const tokenStore = createStore<string | null>(localStorage.getItem("token"));

export const authStore = {
  isAuthenticated: () => tokenStore.get() !== null,
  subscribe: tokenStore.subscribe,

  async login(data: LoginRequest): Promise<void> {
    const res = await api.post<LoginResponse>("/auth/login", data);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Login failed");
    }
    localStorage.setItem("token", res.body.access_token);
    tokenStore.set(res.body.access_token);
  },

  logout: () => {
    localStorage.removeItem("token");
    tokenStore.set(null);
  },

  getToken: () => tokenStore.get(),
};
