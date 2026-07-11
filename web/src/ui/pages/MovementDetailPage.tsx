import { useMovementDetail } from "../hooks/useMovements";
import { useLocation } from "wouter";
import { LoadingSpinner } from "../components/LoadingSpinner";
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
        Movement not found.
      </div>
    );
  }

  const label = movement.movement_type === "INCOME" ? "Income" : "Expense";

  return (
    <div className="space-y-6">
      <button
        onClick={() => setLocation("/movements")}
        className="text-sm text-noir-500 transition-colors hover:text-noir-300"
      >
        &larr; Back
      </button>

      <div className="rounded-lg border border-noir-800 bg-noir-900 p-6">
        <h2 className="text-xl font-bold text-noir-100">Movement Detail</h2>

        <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Amount
            </dt>
            <dd className="mt-1 text-lg font-semibold text-noir-100">
              ${Number(movement.amount).toLocaleString()}{" "}
              <span className="text-xs text-noir-500">
                {movement.currency}
              </span>
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Type
            </dt>
            <dd className="mt-1 text-noir-300">{label}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Category
            </dt>
            <dd className="mt-1 text-noir-300">{movement.category}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Date
            </dt>
            <dd className="mt-1 text-noir-300">
              {formatDate(movement.created_at)}
            </dd>
          </div>
          <div className="col-span-2">
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Description
            </dt>
            <dd className="mt-1 text-noir-400">{movement.description}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Opening Balance
            </dt>
            <dd className="mt-1 text-noir-300">
              ${Number(movement.opening_balance).toLocaleString()}
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-noir-500">
              Closing Balance
            </dt>
            <dd className="mt-1 text-noir-300">
              ${Number(movement.closing_balance).toLocaleString()}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
