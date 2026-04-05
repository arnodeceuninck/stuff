import { clearToken, getToken } from "./auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function _parseDetail(raw, fallback) {
  if (!raw) return fallback;
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw)) {
    // FastAPI validation errors: [{loc, msg, type}, ...]
    return raw.map((e) => (e.msg ? `${e.loc?.slice(-1)[0] ?? "field"}: ${e.msg}` : JSON.stringify(e))).join("; ");
  }
  return JSON.stringify(raw);
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const body = await response.json();
      detail = _parseDetail(body.detail, detail);
    } catch {
      detail = response.statusText || detail;
    }
    if (response.status === 401) {
      clearToken();
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function register(email, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email, password) {
  // The backend proxy uses OAuth2PasswordRequestForm which requires
  // application/x-www-form-urlencoded with a 'username' field.
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!response.ok) {
    let detail = "Login failed";
    try {
      const json = await response.json();
      detail = _parseDetail(json.detail, detail);
    } catch {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  return response.json();
}

export async function getDashboard() {
  return request("/users/me/dashboard");
}

export async function getLocation(locationId) {
  return request(`/locations/${locationId}`);
}

export async function getItem(itemId) {
  return request(`/items/${itemId}`);
}

export async function patchItem(itemId, payload) {
  return request(`/items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function createItemComment(itemId, payload) {
  return request(`/items/${itemId}/comments`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createItem(payload) {
  return request("/items", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createLocation(payload) {
  return request("/locations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateLocation(locationId, payload) {
  return request(`/locations/${locationId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteLocation(locationId) {
  return request(`/locations/${locationId}`, {
    method: "DELETE",
  });
}
