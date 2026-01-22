import { resolveBackendBaseUrl } from './config.js';

const backendBaseUrl = resolveBackendBaseUrl();

async function request(path) {
  const url = `${backendBaseUrl}${path}`;
  let response;
  try {
    response = await fetch(url);
  } catch (error) {
    throw new Error(`Konnte Backend nicht erreichen (${url})`);
  }

  if (!response.ok) {
    throw new Error(`Backend antwortete mit Status ${response.status} (${url})`);
  }

  return response.json();
}

export async function fetchOutages() {
  const data = await request('/outages');
  return data.outages ?? [];
}

export async function fetchDeviceLog(limit = 500) {
  const data = await request(`/device-log?limit=${limit}`);
  return data.entries ?? [];
}

export async function fetchConnectionStatus() {
  return request('/connection-check');
}
