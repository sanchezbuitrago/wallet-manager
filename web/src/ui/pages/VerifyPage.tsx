import { useState, type FormEvent, useEffect } from "react";
import { useLocation, Link } from "wouter";
import { registerStore } from "../../core/stores/register.store";

export function VerifyPage() {
  const [, setLocation] = useLocation();
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const email = registerStore.getRegistrationEmail();

  useEffect(() => {
    if (!email) {
      setLocation("/register");
    }
  }, [email, setLocation]);

  if (!email) {
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email) return;
    setError("");
    setBusy(true);
    try {
      await registerStore.verify({ email, code });
      registerStore.clearRegistrationEmail();
      setLocation("/login");
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-noir-950 px-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-80 w-80 rounded-full bg-noir-800/20 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 h-80 w-80 rounded-full bg-noir-800/20 blur-3xl" />
      </div>

      <form
        onSubmit={handleSubmit}
        className="relative w-full max-w-sm rounded-2xl border border-noir-800/60 bg-noir-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm"
      >
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-noir-100 to-noir-300">
            <span className="text-lg font-bold text-noir-950">WM</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-noir-100">
            Verificar cuenta
          </h1>
          <p className="mt-1 text-xs text-noir-500">
            Ingresa el codigo de 6 digitos enviado a tu WhatsApp
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          Codigo de verificacion
        </label>
        <input
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
          required
          minLength={6}
          maxLength={6}
          className="input-field mb-6 text-center text-2xl tracking-[0.5em]"
          placeholder="000000"
        />

        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? "Verificando..." : "Verificar"}
        </button>

        <p className="mt-4 text-center text-xs text-noir-500">
          <Link href="/register" className="text-noir-300 hover:text-noir-100">
            Volver al registro
          </Link>
        </p>
      </form>
    </div>
  );
}
