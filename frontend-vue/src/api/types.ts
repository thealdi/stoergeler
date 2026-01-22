export interface OutageWindow {
  start: string;
  end?: string | null;
  duration_seconds?: number | null;
  status?: string | null;
}

export interface DeviceLogEntry {
  timestamp?: string | null;
  message?: string | null;
  raw: string;
}

export interface ConnectivityStatus {
  connected: boolean;
  external_ip?: string | null;
  wan_access_type?: string | null;
  wan_link_status?: string | null;
  max_bit_rate?: string | null;
  uptime?: number | string | null;
}

export interface OutageListResponse {
  outages: OutageWindow[];
}

export interface DeviceLogResponse {
  entries: DeviceLogEntry[];
}
