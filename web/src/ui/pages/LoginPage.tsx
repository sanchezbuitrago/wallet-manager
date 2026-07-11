import { useState, type FormEvent } from "react";
import { useAuth } from "../hooks/useAuth";
import { useLocation } from "wouter";

export function LoginPage() {
  const { login } = useAuth();
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, pin);
      setLocation("/");
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-noir-950 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-lg border border-noir-800 bg-noir-900 p-8"
      >
        <h1 className="mb-6 text-center text-xl font-bold text-noir-100">
          Wallet Manager
        </h1>

        {error && (
          <p className="mb-4 rounded bg-noir-800 px-3 py-2 text-sm text-noir-400">
            {error}
          </p>
        )}

        <label className="mb-1 block text-xs uppercase tracking-wider text-noir-500">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mb-4 w-full rounded border border-noir-700 bg-noir-950 px-3 py-2 text-sm text-noir-100 placeholder-noir-600 focus:border-noir-400 focus:outline-none"
          placeholder="you@example.com"
        />

        <label className="mb-1 block text-xs uppercase tracking-wider text-noir-500">
          PIN
        </label>
        <input
          type="password"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          required
          className="mb-6 w-full rounded border border-noir-700 bg-noir-950 px-3 py-2 text-sm text-noir-100 placeholder-noir-600 focus:border-noir-400 focus:outline-none"
          placeholder="••••"
        />

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded bg-noir-100 px-4 py-2 text-sm font-medium text-noir-950 transition-colors hover:bg-noir-200 disabled:opacity-50"
        >
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}
