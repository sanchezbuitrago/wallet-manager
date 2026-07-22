import type { ReactNode } from "react";
import { AdminNavbar } from "./AdminNavbar";

interface AdminLayoutProps {
  children: ReactNode;
}

export function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <div className="min-h-screen bg-noir-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -left-40 top-1/4 h-96 w-96 rounded-full bg-amber-500/5 blur-3xl" />
        <div className="absolute -right-40 top-2/3 h-96 w-96 rounded-full bg-amber-500/5 blur-3xl" />
      </div>
      <div className="relative">
        <AdminNavbar />
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </div>
    </div>
  );
}
