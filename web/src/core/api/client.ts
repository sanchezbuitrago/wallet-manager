import { authStore } from "../stores/auth.store";

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

interface ApiResult<T> {
  success: boolean;
  body: T;
  errors: { title: string; code: string; detail: string }[];
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
    return { success: false, body: json.body, errors: json.errors ?? [] };
  }

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  return { success: true, body: json.body, errors: json.errors ?? [] };
}

export const api = {
  get: <T>(url: string) => request<T>("GET", url),
  post: <T>(url: string, body?: unknown) => request<T>("POST", url, body),
  patch: <T>(url: string, body?: unknown) => request<T>("PATCH", url, body),
  delete: <T>(url: string) => request<T>("DELETE", url),
};
