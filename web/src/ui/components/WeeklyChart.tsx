import {
  BarChart,
  Bar,
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

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-lg border border-noir-700/60 bg-noir-900/95 px-3 py-2 shadow-xl backdrop-blur-sm">
      <p className="mb-1 text-xs font-medium text-noir-200">{label}</p>
      {payload.map((entry: any, i: number) => (
        <p key={i} className="text-xs" style={{ color: entry.color }}>
          {entry.name}: ${Number(entry.value).toLocaleString()}
        </p>
      ))}
    </div>
  );
};

export function WeeklyChart({ data }: WeeklyChartProps) {
  const chartData = data.daily_balance.map((d) => ({
    day: d.date.slice(5),
    Ingresos: Number(d.income),
    Gastos: Number(d.expense),
  }));

  return (
    <div className="card p-5">
      <h3 className="mb-4 text-sm font-medium text-noir-300">
        Esta semana
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData}>
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
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, color: "#aaa" }} />
          <Bar dataKey="Ingresos" fill="#4ade80" fillOpacity={0.8} radius={[4, 4, 0, 0]} barSize={14} />
          <Bar dataKey="Gastos" fill="#f87171" fillOpacity={0.8} radius={[4, 4, 0, 0]} barSize={14} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
