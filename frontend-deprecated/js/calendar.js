import { formatRangeLabel } from './utils.js';

export function initCalendar(element, { onEventClick }) {
  const calendar = new FullCalendar.Calendar(element, {
    locale: 'de',
    initialView: 'timeGridWeek',
    headerToolbar: {
      start: 'prev,next today',
      center: 'title',
      end: 'dayGridMonth,timeGridWeek,listWeek',
    },
    height: 'auto',
    firstDay: 1,
    nowIndicator: true,
    selectable: false,
    events: [],
    eventClick(info) {
      onEventClick?.(info.event);
    },
  });

  calendar.render();
  return calendar;
}

export function renderOutages(calendar, outages) {
  calendar.batchRendering(() => {
    calendar.removeAllEvents();

    outages.forEach((outage, index) => {
      if (!outage.start) {
        return;
      }
      const start = new Date(outage.start);
      const end = outage.end ? new Date(outage.end) : new Date();
      const label = formatRangeLabel(start, end);
      const isPlanned = outage.status?.startsWith('planned');

      calendar.addEvent({
        id: `outage-${index}-bg`,
        start,
        end,
        display: 'background',
        backgroundColor: isPlanned ? 'rgba(59, 130, 246, 0.2)' : 'rgba(220, 38, 38, 0.25)',
        borderColor: isPlanned ? 'rgba(59, 130, 246, 0.45)' : 'rgba(220, 38, 38, 0.4)',
      });

      calendar.addEvent({
        id: `outage-${index}`,
        start,
        end,
        title: isPlanned ? 'Geplant' : 'Offline',
        classNames: ['offline-event', isPlanned ? 'planned-event' : ''],
        extendedProps: {
          label,
          outageIndex: index,
          outage,
        },
      });
    });
  });
}

export function highlightEvent(calendar, eventId) {
  calendar.getEvents().forEach((event) => {
    if (!event.id.startsWith('outage-') || event.id.endsWith('-bg')) {
      return;
    }
    const classNames = ['offline-event'];
    if (event.extendedProps.outage?.status?.startsWith('planned')) {
      classNames.push('planned-event');
    }
    if (event.id === eventId) {
      classNames.push('highlighted');
    }
    event.setProp('classNames', classNames);
  });
}
