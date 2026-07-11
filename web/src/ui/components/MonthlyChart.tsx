import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { MonthlyStatData } from "../../core/types";
import { format } from "date-fns";

interface MonthlyChartProps {
  data: MonthlyStatData[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null;
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
      <div style={{ color: "#eee", marginBottom: 4 }}>{label}</div>
      {payload.map((entry: any, i: number) => (
        <div key={i} style={{ color: entry.fill }}>
          {entry.name}: ${Number(entry.value).toLocaleString()}
        </div>
      ))}
    </div>
  );
};

export function MonthlyChart({ data }: MonthlyChartProps) {
  const chartData = data.map((d) => ({
    month: format(new Date(d.year, d.month - 1), "MMM"),
    Income: Number(d.income),
    Expense: Number(d.expense),
  }));

  return (
    <div className="rounded-lg border border-noir-800 bg-noir-900 p-4">
      <h3 className="mb-4 text-sm font-medium text-noir-300">
        Monthly Overview
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData}>
          <XAxis
            dataKey="month"
            tick={{ fill: "#888", fontSize: 12 }}
            axisLine={{ stroke: "#333" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#888", fontSize: 12 }}
            axisLine={{ stroke: "#333" }}
            tickLine={false}
          />
          <Tooltip
            cursor={false}
            content={<CustomTooltip />}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: "#aaa" }}
          />
          <Bar
            dataKey="Income"
            fill="#16a34a"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="Expense"
            fill="#dc2626"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
