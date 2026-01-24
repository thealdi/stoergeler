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

export async function fetchDeviceLog(limit = 500): Promise<DeviceLogEntry[]> {
  const data = await request<DeviceLogResponse>(`/device-log?limit=${limit}`);
  return data.entries ?? [];
}

export async function fetchConnectionStatus(): Promise<ConnectivityStatus> {
  return request<ConnectivityStatus>('/connection-check');
}

export async function fetchBackendVersion(): Promise<BackendVersion> {
  return request<BackendVersion>('/version');
}
