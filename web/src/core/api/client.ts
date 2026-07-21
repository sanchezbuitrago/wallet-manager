import { authStore } from "../stores/auth.store";

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

interface ApiResult<T> {
  success: boolean;
  body: T;
  errors: { title: string; code: string; detail: string }[];
}

const ERROR_TRANSLATIONS: Record<string, string> = {
  BAD_EMAIL_OR_PASSWORD_ERROR: "El correo o el PIN son incorrectos",
  USER_NOT_ACTIVE:
    "Tu cuenta esta pendiente de verificacion. Por favor verifica tu numero de telefono.",
  USER_ALREADY_EXIST:
    "El usuario con este correo ya esta registrado y activo",
  PHONE_NUMBER_ALREADY_EXIST:
    "El numero de telefono ya esta registrado por otro usuario",
  USER_NOT_FOUND: "No se encontro usuario con este correo",
  INVALID_VERIFICATION_CODE: "El codigo de verificacion es incorrecto",
  VERIFICATION_CODE_EXPIRED:
    "El codigo de verificacion ha expirado. Solicita uno nuevo.",
  "AUTH/INVALID_REFRESH_TOKEN":
    "El token de sesion ha expirado. Inicia sesion de nuevo.",
  PIN_NOT_MATCH: "El PIN actual es incorrecto",
};

function translateErrors(
  errors: { title: string; code: string; detail: string }[],
) {
  return errors.map((e) => ({
    ...e,
    detail: ERROR_TRANSLATIONS[e.code] ?? e.detail,
  }));
}

async function request<T>(
  method: HttpMethod,
  url: string,
  body?: unknown,
  retryCount = 0,
): Promise<ApiResult<T>> {
  const headers: Record<string, string> = {};
  const token = authStore.getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  if (res.status === 401 && retryCount === 0) {
    try {
      await authStore.refreshToken();
      return request<T>(method, url, body, retryCount + 1);
    } catch {
      authStore.logout();
      window.location.href = "/login";
      return { success: false, body: null as T, errors: [] };
    }
  }

  if (res.status === 401 && retryCount > 0) {
    authStore.logout();
    window.location.href = "/login";
    return { success: false, body: null as T, errors: [] };
  }

  if (res.status === 304) {
    return { success: false, body: null as T, errors: [] };
  }

  const json = await res.json();

  if (res.status === 200 && json.success === false) {
    return { success: false, body: json.body, errors: translateErrors(json.errors ?? []) };
  }

  if (!res.ok) {
    throw new Error(`Error del servidor (HTTP ${res.status})`);
  }

  return { success: true, body: json.body, errors: json.errors ?? [] };
}

export const api = {
  get: <T>(url: string) => request<T>("GET", url),
  post: <T>(url: string, body?: unknown) => request<T>("POST", url, body),
  patch: <T>(url: string, body?: unknown) => request<T>("PATCH", url, body),
  delete: <T>(url: string) => request<T>("DELETE", url),
};
