import { api } from "../api/client";
import type { RegisterRequest, VerifyRequest } from "../types";

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

const emailStore = createStore<string | null>(null);

export const registerStore = {
  subscribe: emailStore.subscribe,

  getRegistrationEmail: () => emailStore.get(),

  setRegistrationEmail: (email: string) => {
    emailStore.set(email);
  },

  clearRegistrationEmail: () => {
    emailStore.set(null);
  },

  async register(data: RegisterRequest): Promise<void> {
    const res = await api.post("/users/", data);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al registrar usuario");
    }
    emailStore.set(data.email);
  },

  async verify(data: VerifyRequest): Promise<void> {
    const res = await api.post("/users/verify", data);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al verificar codigo");
    }
  },
};
