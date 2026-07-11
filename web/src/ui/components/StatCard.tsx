interface StatCardProps {
  label: string;
  value: string;
  subtitle?: string;
}

export function StatCard({ label, value, subtitle }: StatCardProps) {
  return (
    <div className="rounded-lg border border-noir-800 bg-noir-900 p-4">
      <p className="text-xs uppercase tracking-wider text-noir-500">
        {label}
      </p>
      <p className="mt-1 text-2xl font-bold text-noir-100">{value}</p>
      {subtitle && (
        <p className="mt-0.5 text-xs text-noir-600">{subtitle}</p>
      )}
    </div>
  );
}
