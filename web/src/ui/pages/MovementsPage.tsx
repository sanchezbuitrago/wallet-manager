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
      <h2 className="text-2xl font-bold text-noir-100">Movements</h2>
      <MovementTable items={page.items} />
      {page.next_cursor && (
        <div className="flex justify-center">
          <button
            onClick={() => loadMore(page.next_cursor!)}
            className="rounded border border-noir-700 bg-noir-900 px-4 py-2 text-sm text-noir-300 transition-colors hover:bg-noir-800"
          >
            Load more
          </button>
        </div>
      )}
    </div>
  );
}
