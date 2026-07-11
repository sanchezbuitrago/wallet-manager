import { useState, useEffect, useMemo, useCallback } from "react";
import { useAccounts } from "../hooks/useAccount";
import { useDashboard } from "../hooks/useMovements";
import { movementStore } from "../../core/stores/movements.store";
import { StatCard } from "../components/StatCard";
import { MonthlyChart } from "../components/MonthlyChart";
import { WeeklyChart } from "../components/WeeklyChart";
import { TypeChart, PERIODS } from "../components/TypeChart";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { categoryLabel } from "../../core/utils/categories";
import type { MovementData } from "../../core/types";

export function DashboardPage() {
  const { selectedId } = useAccounts();
  const {
    account,
    summary,
    monthly,
    weekly,
    loading,
  } = useDashboard(selectedId);

  const [period, setPeriod] = useState(7);
  const [category, setCategory] = useState("all");
  const [allMovements, setAllMovements] = useState<MovementData[]>([]);
  const [incomeMax, setIncomeMax] = useState(0);
  const [expenseMax, setExpenseMax] = useState(0);

  useEffect(() => {
    if (!selectedId) return;
    movementStore.fetchForChart(selectedId, {}).then(setAllMovements);
  }, [selectedId]);

  const categories = useMemo(() => {
    const set = new Set(allMovements.map((m) => m.category));
    return Array.from(set).sort();
  }, [allMovements]);

  const sharedMax = useMemo(() => {
    const m = Math.max(incomeMax, expenseMax);
    return m > 0 ? m * 1.1 : 0;
  }, [incomeMax, expenseMax]);

  const yDomain: [number, number] | undefined = sharedMax > 0 ? [0, sharedMax] : undefined;

  const handleIncomeMax = useCallback((v: number) => setIncomeMax(v), []);
  const handleExpenseMax = useCallback((v: number) => setExpenseMax(v), []);

  if (!selectedId || loading) return <LoadingSpinner />;

  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-noir-100">
          Resumen
        </h2>
        <p className="mt-1 text-sm text-noir-500">
          Resumen de tu cuenta
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Saldo"
          value={`$${Number(account?.balance || 0).toLocaleString()}`}
          subtitle={account?.currency || "COP"}
        />
        <StatCard
          label="Ingresos"
          value={`$${Number(summary?.total_income || 0).toLocaleString()}`}
        />
        <StatCard
          label="Gastos"
          value={`$${Number(summary?.total_expense || 0).toLocaleString()}`}
        />
        <StatCard
          label="Transacciones"
          value={String(summary?.movement_count || 0)}
        />
      </div>

      <div>
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-base font-semibold text-noir-200">Detalle por tipo</h3>
            <p className="text-xs text-noir-500">Ingresos y gastos filtrados por categoría y período</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="rounded-md border border-noir-700/40 bg-noir-900/60 px-2.5 py-1 text-xs text-noir-300 focus:outline-none"
            >
              <option value="all" className="bg-noir-900">Todas las categorías</option>
              {categories.map((c) => (
                <option key={c} value={c} className="bg-noir-900">{categoryLabel(c)}</option>
              ))}
            </select>
            <div className="flex gap-1">
              {PERIODS.map((p) => (
                <button
                  key={p.days}
                  onClick={() => setPeriod(p.days)}
                  className={`rounded-md px-2.5 py-1 text-xs font-medium transition-all duration-150 ${
                    period === p.days
                      ? "bg-noir-700/60 text-noir-100"
                      : "text-noir-500 hover:bg-noir-800/40 hover:text-noir-300"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <TypeChart
            movementType="INCOME"
            period={period}
            category={category}
            yDomain={yDomain}
            onMaxChange={handleIncomeMax}
          />
          <TypeChart
            movementType="EXPENSE"
            period={period}
            category={category}
            yDomain={yDomain}
            onMaxChange={handleExpenseMax}
          />
        </div>
      </div>

      <div>
        <div className="mb-4">
          <h3 className="text-base font-semibold text-noir-200">Tendencias</h3>
          <p className="text-xs text-noir-500">Evolución semanal y mensual</p>
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {weekly && <WeeklyChart data={weekly} />}
          {monthly.length > 0 && <MonthlyChart data={monthly} />}
        </div>
      </div>
    </div>
  );
}
