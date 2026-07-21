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
      throw new Error(res.errors[0]?.detail || "Error al iniciar sesion");
    }
    localStorage.setItem("token", res.body.access_token);
    localStorage.setItem("refresh_token", res.body.refresh_token);
    tokenStore.set(res.body.access_token);
  },

  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    tokenStore.set(null);
  },

  getToken: () => tokenStore.get(),

  getRefreshToken: (): string | null => {
    return localStorage.getItem("refresh_token");
  },

  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) {
      throw new Error("No hay token de recarga disponible");
    }

    const res = await fetch("/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const json = await res.json();

    if (!res.ok || !json.success) {
      throw new Error(json.errors?.[0]?.detail || "Error al recargar token");
    }

    localStorage.setItem("token", json.body.access_token);
    localStorage.setItem("refresh_token", json.body.refresh_token);
    tokenStore.set(json.body.access_token);

    return json.body.access_token;
  },
};
