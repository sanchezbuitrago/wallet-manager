import { useState, type FormEvent } from "react";
import { useLocation, Link } from "wouter";
import { api } from "../../core/api/client";
import type { PinRecoveryRequest, ResetPinRequest } from "../../core/types";

export function RecoverPinPage() {
  const [, setLocation] = useLocation();
  const [step, setStep] = useState<"email" | "reset">("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPin, setNewPin] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleRequest(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await api.post("/auth/pin-recovery", {
        email,
      } satisfies PinRecoveryRequest);
      if (!res.success) {
        throw new Error(res.errors[0]?.detail || "Error al solicitar recuperacion");
      }
      setStep("reset");
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  async function handleReset(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);
    try {
      const res = await api.post<{ code_expired: boolean }>(
        "/auth/pin-recovery/verify",
        { email, code, new_pin: newPin } satisfies ResetPinRequest,
      );
      if (!res.success) {
        throw new Error(res.errors[0]?.detail || "Error al restablecer PIN");
      }
      if (res.body.code_expired) {
        setError(
          "El codigo expiro. Se envio un nuevo codigo a tu numero de telefono.",
        );
        setCode("");
        setNewPin("");
        setBusy(false);
        return;
      }
      setSuccess("PIN restablecido correctamente");
      setTimeout(() => setLocation("/login"), 1500);
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

      <div className="relative w-full max-w-sm rounded-2xl border border-noir-800/60 bg-noir-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-noir-100 to-noir-300">
            <span className="text-lg font-bold text-noir-950">WM</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-noir-100">
            Recuperar PIN
          </h1>
          <p className="mt-1 text-xs text-noir-500">
            {step === "email"
              ? "Ingresa tu correo para recibir un codigo de verificacion"
              : "Ingresa el codigo y tu nuevo PIN"}
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded-lg border border-green-500/20 bg-green-500/10 px-4 py-3 text-sm text-green-400">
            {success}
          </div>
        )}

        {step === "email" ? (
          <form onSubmit={handleRequest}>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
              Correo electronico
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input-field mb-6"
              placeholder="tu@correo.com"
            />

            <button type="submit" disabled={busy} className="btn-primary">
              {busy ? "Enviando..." : "Recuperar"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleReset}>
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
              Codigo de verificacion
            </label>
            <input
              type="text"
              value={code}
              onChange={(e) =>
                setCode(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              required
              minLength={6}
              maxLength={6}
              className="input-field mb-4 text-center text-2xl tracking-[0.5em]"
              placeholder="000000"
            />

            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
              Nuevo PIN
            </label>
            <input
              type="password"
              value={newPin}
              onChange={(e) => setNewPin(e.target.value)}
              required
              minLength={4}
              className="input-field mb-6"
              placeholder="••••"
            />

            <button type="submit" disabled={busy} className="btn-primary">
              {busy ? "Restableciendo..." : "Restablecer PIN"}
            </button>
          </form>
        )}

        <p className="mt-4 text-center text-xs text-noir-500">
          <Link href="/login" className="text-noir-300 hover:text-noir-100">
            Volver al inicio de sesion
          </Link>
        </p>
      </div>
    </div>
  );
}
