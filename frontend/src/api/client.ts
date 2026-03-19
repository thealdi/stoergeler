import { resolveBackendBaseUrl } from '../config';
import type {
  ConnectivityStatus,
  DeviceLogResponse,
  OutageListResponse,
  OutageWindow,
  DeviceLogEntry,
} from './types';

export type BackendVersion = {
  version: string;
  commit?: string;
};

const backendBaseUrl = resolveBackendBaseUrl();

async function request<T>(path: string): Promise<T> {
  const url = `${backendBaseUrl}${path}`;
  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new Error(`Konnte Backend nicht erreichen (${url})`);
  }

  if (!response.ok) {
    throw new Error(`Backend antwortete mit Status ${response.status} (${url})`);
  }

  return response.json() as Promise<T>;
}

export async function fetchOutages(): Promise<OutageWindow[]> {
  const data = await request<OutageListResponse>('/outages');
  return data.outages ?? [];
}

/** Format a Date as a naive (no timezone) ISO string matching the DB storage format. */
function toNaiveISO(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0');
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
    `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  );
}

export async function fetchDeviceLog(
  options: { limit?: number; start?: Date; end?: Date } = {},
): Promise<DeviceLogEntry[]> {
  const params = new URLSearchParams();
  if (options.limit != null) params.set('limit', String(options.limit));
  if (options.start) params.set('start', toNaiveISO(options.start));
  if (options.end) params.set('end', toNaiveISO(options.end));
  const qs = params.toString();
  const data = await request<DeviceLogResponse>(`/device-log${qs ? `?${qs}` : ''}`);
  return data.entries ?? [];
}

export async function fetchConnectionStatus(): Promise<ConnectivityStatus> {
  return request<ConnectivityStatus>('/connection-check');
}

export async function fetchBackendVersion(): Promise<BackendVersion> {
  return request<BackendVersion>('/version');
}

export async function fetchWeeklyReport(scope: 'last' | 'current' = 'last'): Promise<string> {
  const url = `${backendBaseUrl}/report/weekly?scope=${scope}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Fehler beim Abrufen des Reports');
  }
  return response.text();
}

export async function sendTestEmail(): Promise<{ status: string }> {
  const url = `${backendBaseUrl}/report/send-test-email`;
  const response = await fetch(url, { method: 'POST' });
  if (!response.ok) {
    throw new Error('Fehler beim Senden der Test-Email');
  }
  return response.json();
}
