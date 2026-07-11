import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { WeeklyStatData } from "../../core/types";

interface WeeklyChartProps {
  data: WeeklyStatData;
}

export function WeeklyChart({ data }: WeeklyChartProps) {
  const chartData = data.daily_balance.map((d) => ({
    day: d.date.slice(5),
    Income: Number(d.income),
    Expense: Number(d.expense),
  }));

  return (
    <div className="rounded-lg border border-noir-800 bg-noir-900 p-4">
      <h3 className="mb-4 text-sm font-medium text-noir-300">
        This Week
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <XAxis
            dataKey="day"
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
            contentStyle={{
              background: "#222",
              border: "1px solid #444",
              borderRadius: 6,
              color: "#eee",
              fontSize: 13,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "#aaa" }} />
          <Line
            type="monotone"
            dataKey="Income"
            stroke="#16a34a"
            strokeWidth={2}
            dot={{ r: 3, fill: "#16a34a" }}
          />
          <Line
            type="monotone"
            dataKey="Expense"
            stroke="#dc2626"
            strokeWidth={2}
            dot={{ r: 3, fill: "#dc2626" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
