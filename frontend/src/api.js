// Hardcoded for local dev only — this app is just for clicking through and
// sanity-checking the backend by hand, so it isn't worth env-configuring yet.
const API_BASE = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` };
}

export function signup(email, password) {
  return request("/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export function login(email, password) {
  // the login endpoint is OAuth2's form-encoded shape, not JSON — it calls
  // the email field "username" because that's the OAuth2 spec's field name
  const body = new URLSearchParams({ username: email, password });
  return request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

export function listTransactions(token) {
  return request("/transactions", { headers: authHeaders(token) });
}

export function createTransaction(token, data) {
  return request("/transactions", {
    method: "POST",
    headers: { ...authHeaders(token), "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteTransaction(token, id) {
  return request(`/transactions/${id}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
}

export function getSummary(token) {
  return request("/summary", { headers: authHeaders(token) });
}
