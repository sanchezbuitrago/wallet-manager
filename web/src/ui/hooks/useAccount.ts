import { useSyncExternalStore, useEffect, useCallback } from "react";
import { accountsStore } from "../../core/stores/account.store";

export function useAccounts() {
  const state = useSyncExternalStore(
    accountsStore.subscribe,
    accountsStore.getState,
    accountsStore.getState,
  );
  const loading = accountsStore.getLoading();
  const error = accountsStore.getError();

  useEffect(() => {
    accountsStore.fetch();
  }, []);

  return { accounts: state.items, selectedId: state.selectedId, loading, error };
}

export function useAccountSelector() {
  const selected = useSyncExternalStore(
    accountsStore.subscribe,
    accountsStore.getSelected,
    accountsStore.getSelected,
  );

  const selectAccount = useCallback((id: string) => {
    accountsStore.selectAccount(id);
  }, []);

  return { selected, selectAccount };
}
