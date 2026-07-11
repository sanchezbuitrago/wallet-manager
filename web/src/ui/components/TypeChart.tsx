import { useState, useEffect, useMemo, useCallback } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { movementStore } from "../../core/stores/movements.store";
import { useAccounts } from "../hooks/useAccount";
import { categoryLabel } from "../../core/utils/categories";
import type { MovementData } from "../../core/types";

interface TypeChartProps {
  movementType: "INCOME" | "EXPENSE";
  period: number;
  category: string;
  yDomain?: [number, number];
  onMaxChange?: (max: number) => void;
}

export const PERIODS = [
  { label: "Última semana", days: 7, groupBy: "day" as const },
  { label: "Último mes", days: 30, groupBy: "day" as const },
  { label: "Último año", days: 365, groupBy: "month" as const },
  { label: "Todo", days: 0, groupBy: "year" as const },
];

const CATEGORY_PALETTE = [
  "#60a5fa",
  "#f472b6",
  "#a78bfa",
  "#34d399",
  "#fbbf24",
  "#fb923c",
  "#38bdf8",
  "#e879f9",
  "#2dd4bf",
  "#a3e635",
  "#f43f5e",
  "#818cf8",
];

const colorMap: Record<string, string> = {};
let colorIndex = 0;

export function getCategoryColor(category: string): string {
  if (!colorMap[category]) {
    colorMap[category] = CATEGORY_PALETTE[colorIndex % CATEGORY_PALETTE.length];
    colorIndex++;
  }
  return colorMap[category];
}

function toISODate(daysAgo: number): string {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString().slice(0, 19) + "Z";
}

function groupKey(ts: number, groupBy: string): string {
  const d = new Date(ts * 1000);
  if (groupBy === "day") return d.toISOString().slice(0, 10);
  if (groupBy === "month") return d.toISOString().slice(0, 7);
  return String(d.getFullYear());
}

function formatLabel(key: string, groupBy: string): string {
  if (groupBy === "day") {
    const [, m, d] = key.split("-");
    return `${d}/${m}`;
  }
  if (groupBy === "month") {
    const months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
    const [y, m] = key.split("-");
    return `${months[parseInt(m) - 1]} ${y}`;
  }
  return key;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-lg border border-noir-700/60 bg-noir-900/95 px-3 py-2 shadow-xl backdrop-blur-sm">
      <p className="mb-1 text-xs font-medium text-noir-200">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 text-xs">
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-noir-400">{categoryLabel(entry.name)}</span>
          <span className="ml-auto font-medium" style={{ color: entry.color }}>
            ${Number(entry.value || 0).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
};

export function TypeChart({ movementType, period, category, yDomain, onMaxChange }: TypeChartProps) {
  const { selectedId } = useAccounts();
  const [movements, setMovements] = useState<MovementData[]>([]);
  const [loading, setLoading] = useState(false);

  const currentPeriod = PERIODS.find((p) => p.days === period)!;

  const fetchChart = useCallback(
    async (days: number, cat: string) => {
      if (!selectedId) return;
      setLoading(true);
      const opts: { movement_type: string; category?: string; from_date?: string; to_date?: string } = {
        movement_type: movementType,
      };
      if (days > 0) opts.from_date = toISODate(days);
      if (cat !== "all") opts.category = cat;
      const items = await movementStore.fetchForChart(selectedId, opts);
      setMovements(items);
      setLoading(false);
    },
    [selectedId, movementType],
  );

  useEffect(() => {
    fetchChart(period, category);
  }, [period, category, fetchChart]);

  const { chartData, allCategories, grandTotal } = useMemo(() => {
    const groups: Record<string, Record<string, number>> = {};
    const catSet = new Set<string>();
    let total = 0;

    for (const m of movements) {
      const key = groupKey(m.created_at.value, currentPeriod.groupBy);
      const cat = m.category || "Sin categoría";
      const amt = Number(m.amount);
      catSet.add(cat);
      if (!groups[key]) groups[key] = {};
      groups[key][cat] = (groups[key][cat] || 0) + amt;
      total += amt;
    }

    const sorted = Array.from(catSet).sort();
    const entries = Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));

    const data = entries.map(([key, cats]) => {
      const row: Record<string, string | number> = { name: formatLabel(key, currentPeriod.groupBy) };
      for (const c of sorted) {
        row[c] = cats[c] || 0;
      }
      return row;
    });

    return { chartData: data, allCategories: sorted, grandTotal: total };
  }, [movements, currentPeriod.groupBy]);

  const maxStacked = useMemo(() => {
    let mx = 0;
    for (const row of chartData) {
      let sum = 0;
      for (const c of allCategories) {
        sum += Number(row[c] || 0);
      }
      if (sum > mx) mx = sum;
    }
    return mx;
  }, [chartData, allCategories]);

  useEffect(() => {
    onMaxChange?.(maxStacked);
  }, [maxStacked, onMaxChange]);

  return (
    <div className="card p-5">
      <div className="mb-4 flex items-baseline justify-between">
        <h3 className="text-sm font-medium text-noir-300">
          {movementType === "INCOME" ? "Ingresos por período" : "Gastos por período"}
        </h3>
        <span className="text-sm font-semibold text-noir-200">
          ${Number(grandTotal).toLocaleString()}
        </span>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-noir-700 border-t-noir-300" />
        </div>
      ) : chartData.length === 0 ? (
        <p className="py-12 text-center text-sm text-noir-500">Sin datos</p>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <XAxis
                dataKey="name"
                tick={{ fill: "#888", fontSize: 11 }}
                axisLine={{ stroke: "#333" }}
                tickLine={false}
              />
              <YAxis
                domain={yDomain || [0, "auto"]}
                tick={{ fill: "#888", fontSize: 11 }}
                axisLine={{ stroke: "#333" }}
                tickLine={false}
                width={70}
                tickFormatter={(v) => `$${Number(v).toLocaleString()}`}
              />
              <Tooltip
                cursor={false}
                content={<CustomTooltip />}
              />
              {allCategories.map((cat) => (
                  <Bar
                    key={cat}
                    dataKey={cat}
                    stackId="a"
                    fill={getCategoryColor(cat)}
                    fillOpacity={0.85}
                    radius={[0, 0, 0, 0]}
                    label={({ x, y, width, height, value }) => {
                      if (!value || height < 14) return <></>;
                      const percentage = grandTotal > 0
                        ? ((Number(value) / grandTotal) * 100).toFixed(0)
                        : "0";
                      return (
                        <text
                          x={x + width / 2}
                          y={y + height / 2}
                          fill="#fff"
                          textAnchor="middle"
                          dominantBaseline="central"
                          fontSize={10}
                          fontWeight={500}
                        >
                          {percentage}%
                        </text>
                      );
                    }}
                  />
                ))}
            </BarChart>
          </ResponsiveContainer>

          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
            {allCategories.map((cat) => {
              const totalForCat = chartData.reduce((s, row) => s + Number(row[cat] || 0), 0);
              const pct = grandTotal > 0 ? ((totalForCat / grandTotal) * 100).toFixed(1) : "0";
              return (
                  <div key={cat} className="flex items-center gap-1.5 text-xs text-noir-400">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-sm"
                    style={{ backgroundColor: getCategoryColor(cat) }}
                  />
                  {categoryLabel(cat)}
                  <span className="text-noir-500">{pct}%</span>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
