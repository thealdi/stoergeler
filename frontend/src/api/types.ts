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
  external_ipv6?: string | null;
  connection_service?: string | null;
  is_linked?: boolean | null;
  max_bit_rate?: string | null;
  transmission_rate?: string | null;
  uptime?: string | null;
}

export interface OutageListResponse {
  outages: OutageWindow[];
}

export interface DeviceLogResponse {
  entries: DeviceLogEntry[];
}
