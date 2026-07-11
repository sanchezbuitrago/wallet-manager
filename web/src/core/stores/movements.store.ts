import { api } from "../api/client";
import type {
  MovementData,
  MovementPageData,
  CategoryStatData,
  MonthlyStatData,
  WeeklyStatData,
  SummaryData,
} from "../types";

type Listener = () => void;

function createLoadingStore<T>(initial: T) {
  let data = initial;
  let loading = false;
  let error: string | null = null;
  const listeners = new Set<Listener>();

  function notify() {
    listeners.forEach((l) => l());
  }

  return {
    subscribe: (listener: Listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    get: () => data,
    getLoading: () => loading,
    getError: () => error,
    setLoading: () => {
      loading = true;
      error = null;
      notify();
    },
    setData: (next: typeof data) => {
      data = next;
      loading = false;
      error = null;
      notify();
    },
    setError: (msg: string) => {
      error = msg;
      loading = false;
      notify();
    },
  };
}

const movementsStore = createLoadingStore<MovementPageData>({
  items: [],
  next_cursor: null,
});

const summaryStore = createLoadingStore<SummaryData | null>(null);

const monthlyStore = createLoadingStore<MonthlyStatData[]>([]);

const weeklyStore = createLoadingStore<WeeklyStatData | null>(null);

const byCategoryStore = createLoadingStore<CategoryStatData[]>([]);

export const movementStore = {
  subscribe: movementsStore.subscribe,
  get: movementsStore.get,
  getLoading: movementsStore.getLoading,
  getError: movementsStore.getError,

  listMovements: async (accountId: string, cursor?: string, limit = 50) => {
    movementsStore.setLoading();
    try {
      const params = new URLSearchParams({ limit: String(limit), account_id: accountId });
      if (cursor) params.set("cursor", cursor);
      const res = await api.get<MovementPageData>(
        `/analytics/movements?${params}`,
      );
      if (!res.success) {
        movementsStore.setError(res.errors[0]?.detail || "Failed to load");
      } else {
        movementsStore.setData(res.body);
      }
    } catch (e) {
      movementsStore.setError((e as Error).message);
    }
  },

  getMovement: async (id: string): Promise<MovementData | null> => {
    try {
      const res = await api.get<MovementData>(`/analytics/movements/${id}`);
      if (!res.success) return null;
      return res.body;
    } catch {
      return null;
    }
  },

  fetchForChart: async (
    accountId: string,
    opts: { movement_type?: string; category?: string; from_date?: string; to_date?: string },
  ): Promise<MovementData[]> => {
    try {
      const params = new URLSearchParams({ limit: "1000", account_id: accountId });
      if (opts.movement_type) params.set("movement_type", opts.movement_type);
      if (opts.category) params.set("category", opts.category);
      if (opts.from_date) params.set("from_date", opts.from_date);
      if (opts.to_date) params.set("to_date", opts.to_date);
      const res = await api.get<MovementPageData>(`/analytics/movements?${params}`);
      if (!res.success) return [];
      return res.body.items;
    } catch {
      return [];
    }
  },
};

export const statsStore = {
  subscribe: (listener: Listener) => {
    const unsub1 = summaryStore.subscribe(listener);
    const unsub2 = monthlyStore.subscribe(listener);
    const unsub3 = weeklyStore.subscribe(listener);
    const unsub4 = byCategoryStore.subscribe(listener);
    return () => {
      unsub1();
      unsub2();
      unsub3();
      unsub4();
    };
  },

  getSummary: summaryStore.get,
  getSummaryLoading: summaryStore.getLoading,
  getMonthly: monthlyStore.get,
  getMonthlyLoading: monthlyStore.getLoading,
  getWeekly: weeklyStore.get,
  getWeeklyLoading: weeklyStore.getLoading,
  getByCategory: byCategoryStore.get,
  getByCategoryLoading: byCategoryStore.getLoading,

  fetchSummary: async (accountId: string) => {
    summaryStore.setLoading();
    try {
      const res = await api.get<SummaryData>(`/analytics/stats/summary?account_id=${accountId}`);
      if (!res.success) {
        summaryStore.setError(res.errors[0]?.detail || "Failed");
      } else {
        summaryStore.setData(res.body);
      }
    } catch (e) {
      summaryStore.setError((e as Error).message);
    }
  },

  fetchMonthly: async (accountId: string, months = 6) => {
    monthlyStore.setLoading();
    try {
      const res = await api.get<{ items: MonthlyStatData[] }>(
        `/analytics/stats/monthly?account_id=${accountId}&months=${months}`,
      );
      if (!res.success) {
        monthlyStore.setError(res.errors[0]?.detail || "Failed");
      } else {
        monthlyStore.setData(res.body.items);
      }
    } catch (e) {
      monthlyStore.setError((e as Error).message);
    }
  },

  fetchWeekly: async (accountId: string) => {
    weeklyStore.setLoading();
    try {
      const res = await api.get<WeeklyStatData>(`/analytics/stats/weekly?account_id=${accountId}`);
      if (!res.success) {
        weeklyStore.setError(res.errors[0]?.detail || "Failed");
      } else {
        weeklyStore.setData(res.body);
      }
    } catch (e) {
      weeklyStore.setError((e as Error).message);
    }
  },

  fetchByCategory: async (accountId: string, from_date?: string, to_date?: string) => {
    byCategoryStore.setLoading();
    try {
      const params = new URLSearchParams({ account_id: accountId });
      if (from_date) params.set("from_date", from_date);
      if (to_date) params.set("to_date", to_date);
      const res = await api.get<{ items: CategoryStatData[] }>(
        `/analytics/stats/by-category?${params}`,
      );
      if (!res.success) {
        byCategoryStore.setError(res.errors[0]?.detail || "Failed");
      } else {
        byCategoryStore.setData(res.body.items);
      }
    } catch (e) {
      byCategoryStore.setError((e as Error).message);
    }
  },
};
