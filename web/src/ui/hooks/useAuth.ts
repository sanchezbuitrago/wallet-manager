import { useSyncExternalStore, useCallback } from "react";
import { authStore } from "../../core/stores/auth.store";

export function useAuth() {
  const isAuthenticated = useSyncExternalStore(
    authStore.subscribe,
    authStore.isAuthenticated,
    authStore.isAuthenticated,
  );

  const login = useCallback(
    async (email: string, pin: string) => {
      await authStore.login({ email, pin });
    },
    [],
  );

  const logout = useCallback(() => {
    authStore.logout();
  }, []);

  return { isAuthenticated, login, logout };
}
