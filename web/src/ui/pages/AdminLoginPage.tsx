import { useState, useEffect, type FormEvent } from "react";
import { useLocation } from "wouter";
import { authStore } from "../../core/stores/auth.store";
import { api } from "../../core/api/client";
import type { UserProfile } from "../../core/types";

export function AdminLoginPage() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (authStore.isAuthenticated()) {
      api
        .get<UserProfile>("/users/myself")
        .then((res) => {
          if (res.success && res.body.is_admin) {
            setLocation("/admin/dashboard");
          }
        })
        .catch(() => {});
    }
  }, [setLocation]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await authStore.login({ email, pin, require_admin: true });
      setLocation("/admin/dashboard");
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-noir-950 px-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-80 w-80 rounded-full bg-amber-500/10 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 h-80 w-80 rounded-full bg-amber-500/10 blur-3xl" />
      </div>

      <form
        onSubmit={handleSubmit}
        className="relative w-full max-w-sm rounded-2xl border border-noir-800/60 bg-noir-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm"
      >
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-amber-600">
            <span className="text-lg font-bold text-noir-950">WM</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-noir-100">
            Wallet Manager
          </h1>
          <p className="mt-1 text-xs text-amber-400/80">
            Panel de administracion
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          Correo electronico
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="input-field mb-4"
          placeholder="admin@correo.com"
        />

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          PIN
        </label>
        <input
          type="password"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          required
          className="input-field mb-6"
          placeholder="••••"
        />

        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? "Ingresando..." : "Ingresar"}
        </button>

        <p className="mt-4 text-center text-xs text-noir-500">
          <a href="/" className="text-noir-300 hover:text-noir-100">
            Volver al inicio de sesion
          </a>
        </p>
      </form>
    </div>
  );
}
