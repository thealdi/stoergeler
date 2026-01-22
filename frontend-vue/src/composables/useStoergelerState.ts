import { reactive } from 'vue';
import type { DeviceLogEntry, OutageWindow } from '../api/types';

interface StoergelerState {
  outages: OutageWindow[];
  logs: DeviceLogEntry[];
  selectedEventId: string | null;
}

const state = reactive<StoergelerState>({
  outages: [],
  logs: [],
  selectedEventId: null,
});

export function useStoergelerState() {
  function setOutages(outages: OutageWindow[]) {
    state.outages = outages;
  }

  function setLogs(logs: DeviceLogEntry[]) {
    state.logs = logs;
  }

  function setSelectedEvent(eventId: string | null) {
    state.selectedEventId = eventId;
  }

  function resetSelection() {
    state.selectedEventId = null;
  }

  return {
    state,
    setOutages,
    setLogs,
    setSelectedEvent,
    resetSelection,
  };
}
