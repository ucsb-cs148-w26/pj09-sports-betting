// const DEFAULT_BACKEND = "http://localhost:8000";
const DEFAULT_BACKEND = "https://pj09-sports-betting.onrender.com";

function normalizeBackendBase(raw: string | undefined): string {
  const value = raw?.trim();
  if (!value) return DEFAULT_BACKEND;

  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value.replace(/\/+$/, "");
  }

  const isLocalHost =
    value.startsWith("localhost") || value.startsWith("127.0.0.1");
  const protocol = isLocalHost ? "http" : "https";
  return `${protocol}://${value}`.replace(/\/+$/, "");
}

export const BACKEND_BASE_URL = normalizeBackendBase(
  process.env.NEXT_PUBLIC_BACKEND_URL,
);

export const BACKEND_WS_URL = `${BACKEND_BASE_URL.replace(/^http/, "ws")}/ws`;

export function backendApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${BACKEND_BASE_URL}${normalizedPath}`;
}
