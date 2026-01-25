import { ref } from 'vue';
import { createDiscreteApi } from 'naive-ui';
import { fetchConnectionStatus, fetchDeviceLog, fetchOutages } from '../api/client';
import type { ConnectivityStatus } from '../api/types';
import { themeOverrides } from '../theme';
import { useStoergelerState } from './useStoergelerState';

export function useDashboardData() {
  const { setOutages, setLogs } = useStoergelerState();
  const isRefreshing = ref(false);
  const isChecking = ref(false);

  const { message } = createDiscreteApi(['message'], {
    configProviderProps: {
      themeOverrides,
    },
    messageProviderProps: {
      placement: 'top',
      keepAliveOnHover: true,
    },
  });

  function updateStatus(text: string, type: 'info' | 'success' | 'error' = 'info') {
    if (type === 'error') {
      message.error(text);
      return;
    }
    if (type === 'success') {
      message.success(text);
      return;
    }
    message.info(text);
  }

  function buildConnectionInfoSummary(connection: ConnectivityStatus) {
    const infoBits: string[] = [];
    if (connection.external_ip) infoBits.push(`IP ${connection.external_ip}`);
    if (connection.wan_access_type) infoBits.push(connection.wan_access_type);
    if (connection.wan_link_status) infoBits.push(`Link ${connection.wan_link_status}`);
    return infoBits.length ? ` (${infoBits.join(' | ')})` : '';
  }

  async function refreshData() {
    if (isRefreshing.value) {
      return;
    }
    isRefreshing.value = true;
    updateStatus('Aktualisiere Daten ...', 'info');
    try {
      const [outages, logs] = await Promise.all([fetchOutages(), fetchDeviceLog()]);
      const sortedOutages = [...outages].sort(
        (a, b) => new Date(b.start).getTime() - new Date(a.start).getTime()
      );
      setOutages(sortedOutages);
      setLogs(logs);
      updateStatus(
        `Daten aktualisiert – ${outages.length} Stoerungen, ${logs.length} Logzeilen`,
        'success'
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      updateStatus(message, 'error');
    } finally {
      isRefreshing.value = false;
    }
  }

  async function handleConnectionCheck() {
    if (isChecking.value) {
      return;
    }
    isChecking.value = true;
    updateStatus('Prüfe TR-064 Verbindung ...', 'info');
    try {
      const connection = await fetchConnectionStatus();
      const info = buildConnectionInfoSummary(connection);
      updateStatus(`TR-064 Verbindung aktiv${info}`, 'success');
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      updateStatus(message, 'error');
    } finally {
      isChecking.value = false;
    }
  }

  return {
    isRefreshing,
    isChecking,
    refreshData,
    handleConnectionCheck,
  };
}
