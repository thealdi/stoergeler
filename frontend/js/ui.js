import { formatDate, formatDuration } from './utils.js';

const elements = {
  statusMessage: document.querySelector('#statusMessage'),
  outageTableBody: document.querySelector('#outageTableBody'),
  deviceLogTableBody: document.querySelector('#deviceLogTableBody'),
  calendarSelectionInfo: document.querySelector('#calendarSelectionInfo'),
  checkConnectionButton: document.querySelector('#checkConnectionButton'),
  refreshButton: document.querySelector('#refreshButton'),
  clearFilterButton: document.querySelector('#clearFilterButton'),
  outagePagination: document.querySelector('#outage-pagination'),
  deviceLogPagination: document.querySelector('#device-log-pagination'),
};

export function onCheckConnection(handler) {
  elements.checkConnectionButton.addEventListener('click', handler);
}

export function onRefresh(handler) {
  elements.refreshButton.addEventListener('click', handler);
}

export function onClearFilter(handler) {
  elements.clearFilterButton.addEventListener('click', handler);
}

export function toggleClearFilter(disabled) {
  elements.clearFilterButton.disabled = disabled;
}

export function updateStatus(message, type = 'info') {
  elements.statusMessage.textContent = message;
  elements.statusMessage.className = type;
}

export function updateFilterInfo(text) {
  elements.calendarSelectionInfo.textContent = text;
}

export function renderOutageTable(outages) {
  elements.outageTableBody.innerHTML = '';
  if (!outages.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 4;
    cell.textContent = 'Keine Störungen aufgezeichnet.';
    row.appendChild(cell);
    elements.outageTableBody.appendChild(row);
    return;
  }

  outages.forEach((outage) => {
    const row = document.createElement('tr');
    if (outage.status && outage.status.startsWith('planned')) {
      row.classList.add('outage-row-planned');
      row.title = 'Planmäßige Zwangstrennung';
    }

    const startCell = document.createElement('td');
    startCell.textContent = outage.start ? formatDate(outage.start) : 'Unbekannt';
    row.appendChild(startCell);

    const endCell = document.createElement('td');
    endCell.textContent = outage.end ? formatDate(outage.end) : 'läuft...';
    row.appendChild(endCell);

    const durationCell = document.createElement('td');
    durationCell.textContent = formatDuration(outage.duration_seconds);
    row.appendChild(durationCell);

    const statusCell = document.createElement('td');
    statusCell.textContent = outage.status ?? 'unbekannt';
    row.appendChild(statusCell);

    elements.outageTableBody.appendChild(row);
  });
}

export function renderDeviceLog(entries) {
  elements.deviceLogTableBody.innerHTML = '';
  if (!entries.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 2;
    cell.textContent = 'Keine Einträge vorhanden.';
    row.appendChild(cell);
    elements.deviceLogTableBody.appendChild(row);
    return;
  }

  entries
    .slice()
    .sort((a, b) => {
      const timeA = a.timestamp ? new Date(a.timestamp).getTime() : -Infinity;
      const timeB = b.timestamp ? new Date(b.timestamp).getTime() : -Infinity;
      return timeB - timeA;
    })
    .forEach((entry) => {
      const row = document.createElement('tr');

      const timeCell = document.createElement('td');
      timeCell.textContent = entry.timestamp ? formatDate(entry.timestamp) : 'Unbekannt';
      row.appendChild(timeCell);

      const messageCell = document.createElement('td');
      messageCell.textContent = entry.message ?? entry.raw ?? '';
      row.appendChild(messageCell);

      elements.deviceLogTableBody.appendChild(row);
    });
}

export function setLoading(isLoading) {
  if (isLoading) {
    updateStatus('Aktualisiere Daten ...', 'info');
  }
}

function renderPagination(container, paginator, handlers) {
  if (!container) {
    return;
  }
  if (!paginator || paginator.totalPages <= 1) {
    container.innerHTML = '';
    container.style.display = 'none';
    return;
  }

  container.style.display = 'flex';
  container.innerHTML = '';

  const prevButton = document.createElement('button');
  prevButton.type = 'button';
  prevButton.textContent = 'Zurück';
  prevButton.disabled = !paginator.canPrev();
  prevButton.addEventListener('click', (event) => {
    event.preventDefault();
    handlers?.onPrev?.();
  });

  const info = document.createElement('span');
  info.className = 'pagination-info';
  info.textContent = `Seite ${paginator.currentPage + 1} von ${paginator.totalPages}`;

  const nextButton = document.createElement('button');
  nextButton.type = 'button';
  nextButton.textContent = 'Weiter';
  nextButton.disabled = !paginator.canNext();
  nextButton.addEventListener('click', (event) => {
    event.preventDefault();
    handlers?.onNext?.();
  });

  container.append(prevButton, info, nextButton);
}

export function renderOutagePagination(paginator, handlers) {
  renderPagination(elements.outagePagination, paginator, handlers);
}

export function renderDeviceLogPagination(paginator, handlers) {
  renderPagination(elements.deviceLogPagination, paginator, handlers);
}
