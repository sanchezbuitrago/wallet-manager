import type { ReactNode } from "react";
import { Navbar } from "./Navbar";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-noir-950">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -left-40 top-1/4 h-96 w-96 rounded-full bg-noir-800/10 blur-3xl" />
        <div className="absolute -right-40 top-2/3 h-96 w-96 rounded-full bg-noir-800/10 blur-3xl" />
      </div>
      <div className="relative">
        <Navbar />
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </div>
    </div>
  );
}
