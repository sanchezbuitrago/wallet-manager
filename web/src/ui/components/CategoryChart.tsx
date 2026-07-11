import { useState, useCallback } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { CategoryStatData } from "../../core/types";

interface CategoryChartProps {
  data: CategoryStatData[];
  onFetch: (from_date?: string, to_date?: string) => void;
}

const COLORS: Record<string, string> = {
  EXPENSE: "#f87171",
  INCOME: "#4ade80",
};

const PERIODS = [
  { label: "Última semana", days: 7 },
  { label: "Últimos 15 días", days: 15 },
  { label: "Último mes", days: 30 },
] as const;

function toISODate(daysAgo: number): string {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString().slice(0, 19) + "Z";
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload || payload.length === 0) return null;
  const entry = payload[0].payload;
  const typeColor = COLORS[entry.movement_type];
  return (
    <div className="rounded-lg border border-noir-700/60 bg-noir-900/95 px-3 py-2 shadow-xl backdrop-blur-sm">
      <p className="text-xs font-medium text-noir-200">{entry.category}</p>
      <p className="mt-0.5 text-xs" style={{ color: typeColor }}>
        {entry.movement_type}: ${Number(entry.total).toLocaleString()}
      </p>
    </div>
  );
};

export function CategoryChart({ data, onFetch }: CategoryChartProps) {
  const [period, setPeriod] = useState<number>(7);

  const handlePeriodChange = useCallback(
    (days: number) => {
      setPeriod(days);
      onFetch(toISODate(days));
    },
    [onFetch],
  );

  const chartData = data.map((d) => ({
    ...d,
    total: Number(d.total),
  }));

  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium text-noir-300">
          Gastos por categoría
        </h3>
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.days}
              onClick={() => handlePeriodChange(p.days)}
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
      {chartData.length === 0 ? (
        <p className="py-8 text-center text-sm text-noir-500">Sin datos</p>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
            <XAxis
              type="number"
              tick={{ fill: "#888", fontSize: 12 }}
              axisLine={{ stroke: "#333" }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="category"
              tick={{ fill: "#aaa", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={false}
              content={<CustomTooltip />}
            />
            <Bar dataKey="total" radius={[0, 6, 6, 0]} barSize={16}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={COLORS[entry.movement_type] || "#888"} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
