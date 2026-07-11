import { useMovementDetail } from "../hooks/useMovements";
import { useLocation } from "wouter";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { categoryLabel } from "../../core/utils/categories";
import type { Timestamp } from "../../core/types";

function formatDate(ts: Timestamp): string {
  return new Date(ts.value * 1000).toISOString().slice(0, 10);
}

export function MovementDetailPage({ id }: { id: string }) {
  const { movement, loading } = useMovementDetail(id);
  const [, setLocation] = useLocation();

  if (loading) return <LoadingSpinner />;
  if (!movement) {
    return (
      <div className="py-20 text-center text-noir-500">
        Movimiento no encontrado.
      </div>
    );
  }

  const isIncome = movement.movement_type === "INCOME";

  return (
    <div className="space-y-6">
      <button
        onClick={() => setLocation("/movements")}
        className="group flex items-center gap-2 text-sm text-noir-500 transition-colors hover:text-noir-300"
      >
        <span className="transition-transform group-hover:-translate-x-1">&larr;</span>
        Volver a movimientos
      </button>

      <div className="card overflow-hidden">
        <div className={`border-b px-6 py-5 ${isIncome ? "border-green-500/10 bg-green-500/5" : "border-red-500/10 bg-red-500/5"}`}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold tracking-tight text-noir-100">
                Detalle del movimiento
              </h2>
              <p className="mt-1 text-sm text-noir-500">
                {categoryLabel(movement.category)} &middot; {formatDate(movement.created_at)}
              </p>
            </div>
            <span className={isIncome ? "badge-income" : "badge-expense"}>
              {isIncome ? "Ingreso" : "Gasto"}
            </span>
          </div>
        </div>

        <div className="px-6 py-5">
          <div className="mb-6">
            <p className="text-xs font-medium uppercase tracking-wider text-noir-500">
              Monto
            </p>
            <p className={`mt-1 text-3xl font-bold tracking-tight ${isIncome ? "text-green-400" : "text-red-400"}`}>
              {isIncome ? "+" : "-"}${Number(movement.amount).toLocaleString()}
              <span className="ml-2 text-sm font-normal text-noir-500">
                {movement.currency}
              </span>
            </p>
          </div>

          <dl className="grid grid-cols-2 gap-5 text-sm">
            <div className="rounded-lg bg-noir-800/30 p-3">
              <dt className="text-xs font-medium uppercase tracking-wider text-noir-500">
                Tipo
              </dt>
              <dd className="mt-1 text-noir-200">
                {isIncome ? "Ingreso" : "Gasto"}
              </dd>
            </div>
            <div className="rounded-lg bg-noir-800/30 p-3">
              <dt className="text-xs font-medium uppercase tracking-wider text-noir-500">
                Categoría
              </dt>
              <dd className="mt-1 text-noir-200">{categoryLabel(movement.category)}</dd>
            </div>
            <div className="rounded-lg bg-noir-800/30 p-3">
              <dt className="text-xs font-medium uppercase tracking-wider text-noir-500">
                Saldo anterior
              </dt>
              <dd className="mt-1 text-noir-200">
                ${Number(movement.opening_balance).toLocaleString()}
              </dd>
            </div>
            <div className="rounded-lg bg-noir-800/30 p-3">
              <dt className="text-xs font-medium uppercase tracking-wider text-noir-500">
                Saldo actual
              </dt>
              <dd className="mt-1 text-noir-200">
                ${Number(movement.closing_balance).toLocaleString()}
              </dd>
            </div>
            <div className="col-span-2 rounded-lg bg-noir-800/30 p-3">
              <dt className="text-xs font-medium uppercase tracking-wider text-noir-500">
                Descripción
              </dt>
              <dd className="mt-1 text-noir-300">{movement.description}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}
