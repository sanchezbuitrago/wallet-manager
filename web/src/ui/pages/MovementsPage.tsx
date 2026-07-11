import { useAccounts } from "../hooks/useAccount";
import { useMovements } from "../hooks/useMovements";
import { MovementTable } from "../components/MovementTable";
import { LoadingSpinner } from "../components/LoadingSpinner";

export function MovementsPage() {
  const { selectedId } = useAccounts();
  const { page, loading, loadMore } = useMovements(selectedId);

  if (!selectedId || loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-noir-100">
          Movimientos
        </h2>
        <p className="mt-1 text-sm text-noir-500">
          Historial de transacciones
        </p>
      </div>
      <MovementTable items={page.items} />
      {page.next_cursor && (
        <div className="flex justify-center">
          <button
            onClick={() => loadMore(page.next_cursor!)}
            className="btn-ghost"
          >
            Cargar más
          </button>
        </div>
      )}
    </div>
  );
}
