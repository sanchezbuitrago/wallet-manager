import { useState, useEffect, type FormEvent } from "react";
import { useLocation } from "wouter";
import { userStore } from "../../core/stores/user.store";
import type { UpdateProfileRequest, UpdatePinRequest } from "../../core/types";

type Tab = "profile" | "pin";

export function SettingsPage() {
  const [, setLocation] = useLocation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("profile");
  const [verifyContext, setVerifyContext] = useState<Tab>("profile");

  const [firstNames, setFirstNames] = useState("");
  const [lastNames, setLastNames] = useState("");
  const [email, setEmail] = useState("");
  const [countryCode, setCountryCode] = useState("+57");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [currentPin, setCurrentPin] = useState("");
  const [newPin, setNewPin] = useState("");
  const [verifyCode, setVerifyCode] = useState("");

  useEffect(() => {
    userStore
      .fetchProfile()
      .then((profile) => {
        setFirstNames(profile.first_names);
        setLastNames(profile.last_names);
        setEmail(profile.email);
        setCountryCode(profile.phone_number.country_code);
        setPhoneNumber(profile.phone_number.number);
        setLoading(false);
      })
      .catch(() => {
        setLocation("/login");
      });
  }, [setLocation]);

  function resetForms() {
    setVerifying(false);
    setVerifyCode("");
    setError("");
    setSuccess("");
    setCurrentPin("");
    setNewPin("");
  }

  async function handleRequestProfile(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);

    const body: UpdateProfileRequest = {};
    const profile = userStore.get();
    if (profile) {
      if (firstNames !== profile.first_names) body.first_names = firstNames;
      if (lastNames !== profile.last_names) body.last_names = lastNames;
      if (email !== profile.email) body.email = email;
      if (
        phoneNumber !== profile.phone_number.number ||
        countryCode !== profile.phone_number.country_code
      ) {
        body.phone_number = { country_code: countryCode, number: phoneNumber };
      }
    }

    if (Object.keys(body).length === 0) {
      setError("No hay cambios para guardar");
      setBusy(false);
      return;
    }

    try {
      const needsVerification = await userStore.requestUpdate(body);
      if (needsVerification) {
        setVerifyContext("profile");
        setVerifying(true);
      } else {
        setSuccess("Perfil actualizado correctamente");
        await userStore.fetchProfile();
      }
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  async function handleRequestPin(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);

    const body: UpdatePinRequest = { old_pin: currentPin, new_pin: newPin };

    try {
      await userStore.requestPinChange(body);
      setVerifyContext("pin");
      setVerifying(true);
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  async function handleVerify(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const profile = userStore.get();
      await userStore.verifyUpdate({ email: profile!.email, code: verifyCode });
      setVerifying(false);
      setVerifyCode("");
      setCurrentPin("");
      setNewPin("");
      setSuccess(
        verifyContext === "pin"
          ? "PIN actualizado correctamente"
          : "Perfil actualizado correctamente",
      );
      await userStore.fetchProfile();
    } catch (err) {
      setError((err as Error).message);
    }
    setBusy(false);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-noir-600 border-t-noir-200" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="section-title mb-6">Configuracion</h1>

      <div className="card p-6">
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

        {verifying ? (
          <form onSubmit={handleVerify}>
            <p className="mb-4 text-sm text-noir-400">
              Ingresa el codigo de 6 digitos enviado a tu WhatsApp para
              confirmar los cambios.
            </p>

            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
              Codigo de verificacion
            </label>
            <input
              type="text"
              value={verifyCode}
              onChange={(e) =>
                setVerifyCode(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              required
              minLength={6}
              maxLength={6}
              className="input-field mb-6 text-center text-2xl tracking-[0.5em]"
              placeholder="000000"
            />

            <div className="flex gap-3">
              <button
                type="button"
                onClick={resetForms}
                className="btn-ghost flex-1"
              >
                Cancelar
              </button>
              <button type="submit" disabled={busy} className="btn-primary flex-1">
                {busy ? "Verificando..." : "Confirmar"}
              </button>
            </div>
          </form>
        ) : (
          <>
            <div className="mb-6 flex gap-2 rounded-lg bg-noir-900/60 p-1">
              <button
                type="button"
                onClick={() => {
                  setActiveTab("profile");
                  resetForms();
                }}
                className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200 ${
                  activeTab === "profile"
                    ? "bg-noir-800 text-noir-100"
                    : "text-noir-400 hover:text-noir-200"
                }`}
              >
                Actualizar datos
              </button>
              <button
                type="button"
                onClick={() => {
                  setActiveTab("pin");
                  resetForms();
                }}
                className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200 ${
                  activeTab === "pin"
                    ? "bg-noir-800 text-noir-100"
                    : "text-noir-400 hover:text-noir-200"
                }`}
              >
                Actualizar PIN
              </button>
            </div>

            {activeTab === "profile" && (
              <form onSubmit={handleRequestProfile}>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
                  Nombres
                </label>
                <input
                  type="text"
                  value={firstNames}
                  onChange={(e) => setFirstNames(e.target.value)}
                  required
                  className="input-field mb-4"
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
                />

                <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
                  Numero de celular
                </label>
                <div className="mb-6 flex gap-2">
                  <input
                    type="text"
                    value={countryCode}
                    onChange={(e) => setCountryCode(e.target.value)}
                    required
                    className="input-field w-20"
                  />
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    required
                    className="input-field flex-1"
                  />
                </div>

                <button type="submit" disabled={busy} className="btn-primary">
                  {busy ? "Guardando..." : "Guardar cambios"}
                </button>
              </form>
            )}

            {activeTab === "pin" && (
              <form onSubmit={handleRequestPin}>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-noir-400">
                  PIN actual
                </label>
                <input
                  type="password"
                  value={currentPin}
                  onChange={(e) => setCurrentPin(e.target.value)}
                  required
                  className="input-field mb-4"
                  placeholder="••••"
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
                  {busy ? "Guardando..." : "Cambiar PIN"}
                </button>
              </form>
            )}
          </>
        )}
      </div>
    </div>
  );
}
