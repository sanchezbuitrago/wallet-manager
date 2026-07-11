interface StatCardProps {
  label: string;
  value: string;
  subtitle?: string;
}

export function StatCard({ label, value, subtitle }: StatCardProps) {
  return (
    <div className="group relative overflow-hidden rounded-xl border border-noir-800/60 bg-noir-900/80 p-5 backdrop-blur-sm transition-all duration-200 hover:border-noir-700/60 hover:shadow-lg hover:shadow-black/20">
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
      <p className="relative text-xs font-medium uppercase tracking-wider text-noir-500">
        {label}
      </p>
      <p className="relative mt-2 text-2xl font-bold tracking-tight text-noir-100">
        {value}
      </p>
      {subtitle && (
        <p className="relative mt-1 text-xs text-noir-500">{subtitle}</p>
      )}
    </div>
  );
}
