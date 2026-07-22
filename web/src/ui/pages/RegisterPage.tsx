import { useState, useEffect, type FormEvent } from "react";
import { useLocation, Link } from "wouter";
import { registerStore } from "../../core/stores/register.store";

export function RegisterPage() {
  const [, setLocation] = useLocation();
  const [firstNames, setFirstNames] = useState("");
  const [lastNames, setLastNames] = useState("");
  const [email, setEmail] = useState("");
  const [countryCode, setCountryCode] = useState("+57");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!success) return;
    const timer = setTimeout(() => setLocation("/login"), 2000);
    return () => clearTimeout(timer);
  }, [success, setLocation]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await registerStore.register({
        first_names: firstNames,
        last_names: lastNames,
        email,
        phone_number: { country_code: countryCode, number: phoneNumber },
        pin,
      });
      setSuccess(true);
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-noir-950 px-4 py-8">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-80 w-80 rounded-full bg-noir-800/20 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 h-80 w-80 rounded-full bg-noir-800/20 blur-3xl" />
      </div>

      {success ? (
        <div className="relative w-full max-w-sm rounded-2xl border border-noir-800/60 bg-noir-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600">
            <svg className="h-6 w-6 text-noir-950" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-noir-100">Cuenta creada con exito</h2>
          <p className="mt-2 text-sm text-noir-400">Redirigiendo al inicio de sesion...</p>
          <div className="mt-5 h-1 w-full overflow-hidden rounded-full bg-noir-800">
            <div className="h-full rounded-full bg-emerald-500 animate-[shrink_2s_linear_forwards]" />
          </div>
        </div>
      ) : (
      <form
        onSubmit={handleSubmit}
        className="relative w-full max-w-sm rounded-2xl border border-noir-800/60 bg-noir-900/80 p-8 shadow-2xl shadow-black/40 backdrop-blur-sm"
      >
        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-noir-100 to-noir-300">
            <span className="text-lg font-bold text-noir-950">WM</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-noir-100">
            Wallet Manager
          </h1>
          <p className="mt-1 text-xs text-noir-500">
            Crea tu cuenta para comenzar
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          Nombres
        </label>
        <input
          type="text"
          value={firstNames}
          onChange={(e) => setFirstNames(e.target.value)}
          required
          className="input-field mb-4"
          placeholder="Tus nombres"
        />

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          Apellidos
        </label>
        <input
          type="text"
          value={lastNames}
          onChange={(e) => setLastNames(e.target.value)}
          required
          className="input-field mb-4"
          placeholder="Tus apellidos"
        />

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          Correo electronico
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="input-field mb-4"
          placeholder="tu@correo.com"
        />

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          Numero de celular
        </label>
        <div className="mb-4 flex gap-2">
          <input
            type="text"
            value={countryCode}
            onChange={(e) => setCountryCode(e.target.value)}
            required
            className="input-field w-20"
            placeholder="+57"
          />
          <input
            type="tel"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            required
            className="input-field flex-1"
            placeholder="3001234567"
          />
        </div>

        <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
          PIN
        </label>
        <input
          type="password"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          required
          minLength={4}
          className="input-field mb-6"
          placeholder="••••"
        />

        <button type="submit" disabled={busy} className="btn-primary">
          {busy ? "Creando cuenta..." : "Crear cuenta"}
        </button>

        <p className="mt-4 text-center text-xs text-noir-500">
          Ya tienes una cuenta?{" "}
          <Link href="/login" className="text-noir-300 hover:text-noir-100">
            Iniciar sesion
          </Link>
        </p>
      </form>
      )}
    </div>
  );
}
