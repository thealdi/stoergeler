import { fetchConnectionStatus, fetchDeviceLog, fetchOutages } from './api.js';
import {
  initCalendar,
  renderOutages as renderCalendarOutages,
  highlightEvent
} from './calendar.js';
import {
  onCheckConnection,
  onRefresh,
  onClearFilter,
  updateStatus,
  renderOutageTable,
  renderDeviceLog,
  renderOutagePagination,
  renderDeviceLogPagination,
  updateFilterInfo,
  toggleClearFilter
} from './ui.js';
import {
  state,
  updateLogs,
  updateOutages,
  resetSelection,
  setSelectedEvent
} from './state.js';
import { formatRangeLabel } from './utils.js';
import { Paginator } from './pagination.js';

const calendarElement = document.querySelector('#calendar');
const calendar = initCalendar(calendarElement, {
  onEventClick: handleCalendarEventClick
});

const outagePaginator = new Paginator([], 5);
const logPaginator = new Paginator([], 20);

async function refreshData() {
  updateStatus('Aktualisiere Daten ...', 'info');
  try {
    const [outages, logs] = await Promise.all([
      fetchOutages(),
      fetchDeviceLog()
    ]);

    // Sort outages by start_time descending
    const sortedOutages = [...outages].sort(
      (a, b) =>
        new Date(b.start).getTime() - new Date(a.start).getTime()
    );

    updateOutages(sortedOutages);
    updateLogs(logs);

    outagePaginator.setItems(sortedOutages);
    logPaginator.setItems(logs);

    updateOutageView();
    updateLogView();
    renderCalendarOutages(calendar, outages);
    highlightEvent(calendar, null);

    updateFilterInfo('Keine Filter aktiv. Alle Ereignisse werden angezeigt.');
    toggleClearFilter(true);

    updateStatus(
      `Daten aktualisiert – ${outages.length} Störungen, ${logs.length} Logzeilen`,
      'success'
    );
  } catch (error) {
    updateStatus(error.message, 'error');
  }
}

async function handleConnectionCheck() {
  updateStatus('Prüfe TR-064 Verbindung ...', 'info');
  try {
    const connection = await fetchConnectionStatus();
    const info = buildConnectionInfoSummary(connection);
    updateStatus(`TR-064 Verbindung aktiv${info}`, 'success');
  } catch (error) {
    updateStatus(error.message, 'error');
  }
}

function handleCalendarEventClick(event) {
  const start = event.start;
  const end = event.end ?? new Date();
  const label = event.extendedProps.label ?? formatRangeLabel(start, end);

  setSelectedEvent(event.id);
  const filteredLogs = filterLogsByRange(state.logs, start, end);
  renderDeviceLog(filteredLogs);
  renderDeviceLogPagination(null);
  updateFilterInfo(
    `Gefiltert nach ${label} (${filteredLogs.length} Ereignisse).`
  );
  toggleClearFilter(false);
  highlightEvent(calendar, event.id);
}

function handleClearFilter() {
  resetSelection();
  logPaginator.setItems(state.logs);
  updateLogView();
  updateFilterInfo('Keine Filter aktiv. Alle Ereignisse werden angezeigt.');
  toggleClearFilter(true);
  highlightEvent(calendar, null);
}

function filterLogsByRange(entries, start, end) {
  const startMs = start.getTime();
  const endMs = end.getTime();
  return entries.filter((entry) => {
    if (!entry.timestamp) {
      return false;
    }
    const entryMs = new Date(entry.timestamp).getTime();
    return entryMs >= startMs && entryMs <= endMs;
  });
}

function buildConnectionInfoSummary(connection) {
  const infoBits = [];
  if (connection.external_ip) infoBits.push(`IP ${connection.external_ip}`);
  if (connection.wan_access_type) infoBits.push(connection.wan_access_type);
  if (connection.wan_link_status)
    infoBits.push(`Link ${connection.wan_link_status}`);
  return infoBits.length ? ` (${infoBits.join(' | ')})` : '';
}

function registerEventHandlers() {
  onCheckConnection(handleConnectionCheck);
  onRefresh(refreshData);
  onClearFilter(handleClearFilter);
}

function updateOutageView() {
  renderOutageTable(outagePaginator.pageItems);
  renderOutagePagination(outagePaginator, {
    onPrev: () => {
      outagePaginator.prev();
      updateOutageView();
    },
    onNext: () => {
      outagePaginator.next();
      updateOutageView();
    }
  });
}

function updateLogView() {
  renderDeviceLog(logPaginator.pageItems);
  renderDeviceLogPagination(logPaginator, {
    onPrev: () => {
      logPaginator.prev();
      updateLogView();
    },
    onNext: () => {
      logPaginator.next();
      updateLogView();
    }
  });
}

registerEventHandlers();
refreshData();
