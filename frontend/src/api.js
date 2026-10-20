/**
 * Cliente de la API.
 *
 * Todas las llamadas van a /api en el mismo dominio (el Ingress, nginx o Vite
 * se encargan de mandarlas al backend). Si el backend responde con error, se
 * lanza un ApiError con el `code` fijo y el `detail` listo para mostrar
 * (ver "Errores" en architecture.md).
 */

const TOKEN_KEY = "cafeteria.token";

export class ApiError extends Error {
  constructor(status, code, detail) {
    super(detail);
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

// Lo llama la sesión para enterarse cuando el token venció.
let onUnauthorized = () => {};
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

async function request(method, path, body) {
  const headers = { Accept: "application/json" };
  const token = getToken();

  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "NETWORK", "No hay conexión con el servidor. Revisá tu internet y probá de nuevo.");
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    if (response.status === 401 && path !== "/auth/login") onUnauthorized();
    throw new ApiError(response.status, data?.code ?? "UNKNOWN", readableDetail(data));
  }

  return data;
}

/** FastAPI devuelve los errores de validación como una lista; los nuestros, como texto. */
function readableDetail(data) {
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.detail)) return "Algunos datos no son válidos. Revisalos y probá de nuevo.";
  return "Algo salió mal en el servidor. Probá de nuevo en un momento.";
}

// ---------------------------------------------------------------------------

export const api = {
  login: (email, password) => request("POST", "/auth/login", { email, password }),
  me: () => request("GET", "/auth/me"),

  products: () => request("GET", "/products"),
  createProduct: (product) => request("POST", "/products", product),
  updateProduct: (id, changes) => request("PATCH", `/products/${id}`, changes),

  recesses: () => request("GET", "/recesses"),
  recessesToday: () => request("GET", "/recesses/today"),
  createRecess: (recess) => request("POST", "/recesses", recess),
  updateRecess: (id, changes) => request("PATCH", `/recesses/${id}`, changes),

  placeOrder: (recessId, items) => request("POST", "/orders", { recess_id: recessId, items }),
  myOrders: () => request("GET", "/orders/mine"),
  changeOrderStatus: (id, status) => request("PATCH", `/orders/${id}/status`, { status }),

  nextRecessBoard: () => request("GET", "/cafeteria/next-recess"),
  ordersToday: () => request("GET", "/cafeteria/orders-today"),
  salesSummary: (serviceDate) =>
    request("GET", `/cafeteria/sales-summary${serviceDate ? `?service_date=${serviceDate}` : ""}`),

  configuration: () => request("GET", "/configuration"),
  updateOrderCutoff: (minutes) => request("PUT", "/configuration/order-cutoff", { order_cutoff_minutes: minutes }),
};
