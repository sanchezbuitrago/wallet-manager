import type { MovementData, Timestamp } from "../../core/types";
import { useLocation } from "wouter";

function formatDate(ts: Timestamp): string {
  return new Date(ts.value * 1000).toISOString().slice(0, 10);
}

interface MovementTableProps {
  items: MovementData[];
}

export function MovementTable({ items }: MovementTableProps) {
  const [, setLocation] = useLocation();

  return (
    <div className="overflow-hidden rounded-lg border border-noir-800">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-noir-800 bg-noir-900">
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-noir-500">
              Date
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-noir-500">
              Category
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-noir-500">
              Description
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-noir-500">
              Amount
            </th>
            <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-noir-500">
              Balance
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-noir-800">
          {items.map((m) => {
            const isIncome = m.movement_type === "INCOME";
            return (
              <tr
                key={m.id}
                onClick={() => setLocation(`/movements/${m.id}`)}
                className="cursor-pointer border-l-4 transition-colors hover:bg-noir-900"
                style={{ borderLeftColor: isIncome ? "#4ade80" : "#f87171" }}
              >
                <td className="whitespace-nowrap px-4 py-3 text-noir-400">
                  {formatDate(m.created_at)}
                </td>
                <td className="px-4 py-3 text-noir-300">{m.category}</td>
                <td className="max-w-[200px] truncate px-4 py-3 text-noir-400">
                  {m.description}
                </td>
                <td
                  className={`whitespace-nowrap px-4 py-3 text-right font-medium ${
                    isIncome ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {isIncome ? "+" : "-"}$
                  {Number(m.amount).toLocaleString()}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-right text-noir-500">
                  ${Number(m.closing_balance).toLocaleString()}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
