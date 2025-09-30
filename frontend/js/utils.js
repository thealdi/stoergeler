export function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString('de-DE', {
    dateStyle: 'short',
    timeStyle: 'medium',
  });
}

export function formatDuration(durationSeconds) {
  if (typeof durationSeconds !== 'number' || Number.isNaN(durationSeconds)) {
    return 'unbekannt';
  }
  const totalSeconds = Math.max(0, Math.floor(durationSeconds));
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const parts = [];
  if (days) parts.push(`${days}d`);
  if (hours) parts.push(`${hours}h`);
  if (minutes) parts.push(`${minutes}m`);
  if (seconds || parts.length === 0) parts.push(`${seconds}s`);
  return parts.join(' ');
}

export function formatRangeLabel(start, end) {
  const sameDay = start.toDateString() === end.toDateString();
  if (sameDay) {
    return `${start.toLocaleDateString('de-DE')} ${start.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
    })}–${end.toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit',
    })}`;
  }
  return `${start.toLocaleString('de-DE')} bis ${end.toLocaleString('de-DE')}`;
}
