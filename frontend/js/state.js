export const state = {
  outages: [],
  logs: [],
  selectedEventId: null,
};

export function updateOutages(outages) {
  state.outages = outages;
}

export function updateLogs(logs) {
  state.logs = logs;
}

export function setSelectedEvent(eventId) {
  state.selectedEventId = eventId;
}

export function resetSelection() {
  state.selectedEventId = null;
}
