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
    <div className="overflow-hidden rounded-xl border border-noir-800/60 backdrop-blur-sm">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-noir-800/60 bg-noir-900/80">
            <th className="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-noir-500">
              Fecha
            </th>
            <th className="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-noir-500">
              Categoría
            </th>
            <th className="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-noir-500">
              Descripción
            </th>
            <th className="px-5 py-3.5 text-right text-xs font-medium uppercase tracking-wider text-noir-500">
              Monto
            </th>
            <th className="px-5 py-3.5 text-right text-xs font-medium uppercase tracking-wider text-noir-500">
              Saldo
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-noir-800/40">
          {items.map((m, index) => {
            const isIncome = m.movement_type === "INCOME";
            return (
              <tr
                key={m.id}
                onClick={() => setLocation(`/movements/${m.id}`)}
                className={`group cursor-pointer border-l-4 transition-all duration-150 hover:bg-noir-800/30 ${
                  index % 2 === 0 ? "bg-noir-900/20" : ""
                }`}
                style={{ borderLeftColor: isIncome ? "#4ade80" : "#f87171" }}
              >
                <td className="whitespace-nowrap px-5 py-3.5 text-noir-400 transition-colors group-hover:text-noir-300">
                  {formatDate(m.created_at)}
                </td>
                <td className="px-5 py-3.5 text-noir-300 transition-colors group-hover:text-noir-200">
                  {m.category}
                </td>
                <td className="max-w-[200px] truncate px-5 py-3.5 text-noir-400 transition-colors group-hover:text-noir-300">
                  {m.description}
                </td>
                <td
                  className={`whitespace-nowrap px-5 py-3.5 text-right font-medium ${
                    isIncome ? "text-green-400" : "text-red-400"
                  }`}
                >
                  {isIncome ? "+" : "-"}$
                  {Number(m.amount).toLocaleString()}
                </td>
                <td className="whitespace-nowrap px-5 py-3.5 text-right text-noir-500">
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
