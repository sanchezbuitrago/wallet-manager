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
}

const COLORS: Record<string, string> = {
  EXPENSE: "#dc2626",
  INCOME: "#16a34a",
};

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload || payload.length === 0) return null;
  const entry = payload[0].payload;
  const typeColor = COLORS[entry.movement_type];
  return (
    <div
      style={{
        background: "#222",
        border: "1px solid #444",
        borderRadius: 6,
        padding: "6px 12px",
        fontSize: 13,
      }}
    >
      <span style={{ color: "#eee" }}>{entry.category}</span>
      <br />
      <span style={{ color: typeColor }}>
        {entry.movement_type}: ${Number(entry.total).toLocaleString()}
      </span>
    </div>
  );
};

export function CategoryChart({ data }: CategoryChartProps) {
  const chartData = data.map((d) => ({
    ...d,
    total: Number(d.total),
  }));

  return (
    <div className="rounded-lg border border-noir-800 bg-noir-900 p-4">
      <h3 className="mb-4 text-sm font-medium text-noir-300">
        Spending by Category
      </h3>
      {chartData.length === 0 ? (
        <p className="py-8 text-center text-sm text-noir-500">No data</p>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
            <XAxis
              type="number"
              tick={{ fill: "#888" }}
              axisLine={{ stroke: "#333" }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="category"
              tick={{ fill: "#aaa" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={false}
              content={<CustomTooltip />}
            />
            <Bar dataKey="total" radius={[0, 4, 0, 4]}>
              {chartData.map((entry, i) => (
                <Cell key={i} fill={COLORS[entry.movement_type] || "#888"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
