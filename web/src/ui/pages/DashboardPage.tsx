import { useAccounts } from "../hooks/useAccount";
import { useDashboard } from "../hooks/useMovements";
import { StatCard } from "../components/StatCard";
import { CategoryChart } from "../components/CategoryChart";
import { MonthlyChart } from "../components/MonthlyChart";
import { WeeklyChart } from "../components/WeeklyChart";
import { LoadingSpinner } from "../components/LoadingSpinner";

export function DashboardPage() {
  const { selectedId } = useAccounts();
  const {
    account,
    summary,
    monthly,
    weekly,
    byCategory,
    loading,
    fetchByCategory,
  } = useDashboard(selectedId);

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
        <div className="mb-4">
          <h3 className="text-base font-semibold text-noir-200">Esta semana</h3>
          <p className="text-xs text-noir-500">Movimientos de los últimos 7 días</p>
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {weekly && <WeeklyChart data={weekly} />}
          <CategoryChart data={byCategory} onFetch={fetchByCategory} />
        </div>
      </div>

      {monthly.length > 0 && (
        <div>
          <div className="mb-4">
            <h3 className="text-base font-semibold text-noir-200">Tendencia mensual</h3>
            <p className="text-xs text-noir-500">Comparación de ingresos y gastos por mes</p>
          </div>
          <MonthlyChart data={monthly} />
        </div>
      )}
    </div>
  );
}
