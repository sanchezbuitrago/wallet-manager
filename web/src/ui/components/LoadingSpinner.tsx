export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="relative h-10 w-10">
        <div className="absolute inset-0 animate-spin rounded-full border-2 border-noir-800" />
        <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-noir-300" style={{ animationDuration: "0.8s" }} />
      </div>
    </div>
  );
}
