export const DEFAULT_API_PREFIX = '/api';

function normalizePrefix(rawPrefix) {
  if (!rawPrefix) {
    return '';
  }
  const trimmed = rawPrefix.trim();
  if (!trimmed || trimmed === '/') {
    return '';
  }
  return `/${trimmed.replace(/^\/+/, '').replace(/\/$/, '')}`;
}

export function ensureApiPrefix(baseUrl, prefix = DEFAULT_API_PREFIX) {
  const cleanedBase = baseUrl.replace(/\/$/, '');
  const normalized = normalizePrefix(prefix || DEFAULT_API_PREFIX);
  if (!normalized) {
    return cleanedBase;
  }
  if (cleanedBase.endsWith(normalized)) {
    return cleanedBase;
  }
  return `${cleanedBase}${normalized}`;
}

export function resolveBackendBaseUrl() {
  const explicitUrl = typeof window.STOERGELER_BACKEND_URL === 'string'
    ? window.STOERGELER_BACKEND_URL.trim()
    : '';
  if (explicitUrl) {
    return ensureApiPrefix(explicitUrl, window.STOERGELER_BACKEND_PATH);
  }

  const { protocol, hostname, port } = window.location;
  const effectivePort = (!port || port === '' || port === '80' || port === '443')
    ? ''
    : `:${port}`;
  const baseHost = `${protocol}//${hostname}${effectivePort}`;

  return ensureApiPrefix(baseHost, window.STOERGELER_BACKEND_PATH);
}
