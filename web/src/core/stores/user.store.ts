import { api } from "../api/client";
import type {
  UserProfile,
  UpdateProfileRequest,
  UpdatePinRequest,
  VerifyRequest,
} from "../types";

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

const profileStore = createStore<UserProfile | null>(null);
const updatePendingStore = createStore<boolean>(false);

export const userStore = {
  subscribe: profileStore.subscribe,
  get: profileStore.get,

  getUpdatePending: () => updatePendingStore.get(),
  subscribeUpdatePending: updatePendingStore.subscribe,

  async fetchProfile(): Promise<UserProfile> {
    const res = await api.get<UserProfile>("/users/myself");
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al cargar perfil");
    }
    profileStore.set(res.body);
    return res.body;
  },

  async requestUpdate(data: UpdateProfileRequest): Promise<boolean> {
    const res = await api.patch<{ requires_verification: boolean }>(
      "/users/myself/profile",
      data,
    );
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al actualizar perfil");
    }
    if (res.body.requires_verification) {
      updatePendingStore.set(true);
      return true;
    }
    await profileStore.get() && profileStore.set({ ...profileStore.get()! });
    return false;
  },

  async requestPinChange(data: UpdatePinRequest): Promise<void> {
    const res = await api.patch("/users/myself/pin", data);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al cambiar PIN");
    }
    updatePendingStore.set(true);
  },

  async verifyUpdate(data: VerifyRequest): Promise<void> {
    const res = await api.post("/users/myself/verify", data);
    if (!res.success) {
      throw new Error(res.errors[0]?.detail || "Error al verificar codigo");
    }
    updatePendingStore.set(false);
  },

  clearPending: () => updatePendingStore.set(false),
};
