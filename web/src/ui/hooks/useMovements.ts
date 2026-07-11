import { useSyncExternalStore, useEffect, useCallback, useState } from "react";
import {
  movementStore,
  statsStore,
} from "../../core/stores/movements.store";
import { accountsStore } from "../../core/stores/account.store";
import type { MovementData } from "../../core/types";

export function useMovements(accountId: string | null) {
  const page = useSyncExternalStore(
    movementStore.subscribe,
    movementStore.get,
    movementStore.get,
  );
  const loading = movementStore.getLoading();
  const error = movementStore.getError();

  const loadMore = useCallback(
    (cursor?: string) => {
      if (accountId) movementStore.listMovements(accountId, cursor);
    },
    [accountId],
  );

  useEffect(() => {
    if (accountId) movementStore.listMovements(accountId);
  }, [accountId]);

  return { page, loading, error, loadMore };
}

export function useMovementDetail(id: string) {
  const [movement, setMovement] = useState<MovementData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    movementStore.getMovement(id).then((m) => {
      setMovement(m);
      setLoading(false);
    });
  }, [id]);

  return { movement, loading };
}

export function useDashboard(accountId: string | null) {
  const selected = useSyncExternalStore(
    accountsStore.subscribe,
    accountsStore.getSelected,
    accountsStore.getSelected,
  );

  const summary = useSyncExternalStore(
    statsStore.subscribe,
    statsStore.getSummary,
    statsStore.getSummary,
  );
  const sLoading = statsStore.getSummaryLoading();

  const monthly = useSyncExternalStore(
    statsStore.subscribe,
    statsStore.getMonthly,
    statsStore.getMonthly,
  );
  const mLoading = statsStore.getMonthlyLoading();

  const weekly = useSyncExternalStore(
    statsStore.subscribe,
    statsStore.getWeekly,
    statsStore.getWeekly,
  );
  const wLoading = statsStore.getWeeklyLoading();

  const byCategory = useSyncExternalStore(
    statsStore.subscribe,
    statsStore.getByCategory,
    statsStore.getByCategory,
  );
  const cLoading = statsStore.getByCategoryLoading();

  useEffect(() => {
    if (!accountId) return;
    statsStore.fetchSummary(accountId);
    statsStore.fetchMonthly(accountId);
    statsStore.fetchWeekly(accountId);
    statsStore.fetchByCategory(accountId);
  }, [accountId]);

  const fetchByCategory = useCallback(
    (from_date?: string, to_date?: string) => {
      if (accountId) statsStore.fetchByCategory(accountId, from_date, to_date);
    },
    [accountId],
  );

  return {
    account: selected,
    summary,
    monthly,
    weekly,
    byCategory,
    loading: sLoading || mLoading || wLoading || cLoading,
    fetchByCategory,
  };
}
