<template>
  <div class="calendar-shell">
    <FullCalendar ref="calendarRef" :options="calendarOptions" />
    <div v-if="!isLoading && outages.length === 0" class="calendar-empty">
      Keine Störungen im ausgewählten Zeitraum.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import timeGridPlugin from '@fullcalendar/timegrid';
import type { EventClickArg, EventInput, EventMountArg } from '@fullcalendar/core';
import deLocale from '@fullcalendar/core/locales/de';
import type { OutageWindow } from '../api/types';
import { formatRangeLabel } from '../utils/format';

const props = defineProps<{
  outages: OutageWindow[];
  selectedEventId: string | null;
  isLoading?: boolean;
}>();

const emit = defineEmits<{
  (event: 'select-outage', payload: { eventId: string; start: Date; end: Date; label: string }): void;
}>();

const events = computed<EventInput[]>(() => {
  const inputs: EventInput[] = [];
  props.outages.forEach((outage, index) => {
    if (!outage.start) {
      return;
    }
    const start = new Date(outage.start);
    const end = outage.end ? new Date(outage.end) : new Date();
    const label = formatRangeLabel(start, end);
    const isPlanned = outage.status?.startsWith('planned');

    inputs.push({
      id: `outage-${index}-bg`,
      start,
      end,
      display: 'background',
      backgroundColor: isPlanned ? 'rgba(59, 130, 246, 0.2)' : 'rgba(220, 38, 38, 0.25)',
      borderColor: isPlanned ? 'rgba(59, 130, 246, 0.45)' : 'rgba(220, 38, 38, 0.4)',
    });

    inputs.push({
      id: `outage-${index}`,
      start,
      end,
      title: isPlanned ? 'Geplant' : 'Offline',
      backgroundColor: isPlanned ? '#3b82f6' : '#dc2626',
      borderColor: isPlanned ? '#2563eb' : '#b91c1c',
      extendedProps: {
        label,
        outageIndex: index,
        outage,
        planned: isPlanned,
      },
    });
  });
  return inputs;
});

function handleEventClick(info: EventClickArg) {
  const { event } = info;
  if (!event.start || event.id.endsWith('-bg')) {
    return;
  }
  const start = event.start;
  const end = event.end ?? new Date();
  const label = event.extendedProps.label ?? formatRangeLabel(start, end);
  emit('select-outage', { eventId: event.id, start, end, label });
}

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin],
  locale: deLocale,
  initialView: 'timeGridWeek',
  headerToolbar: false as const,
  height: 'auto',
  eventMinHeight: 20,
  firstDay: 1,
  nowIndicator: true,
  selectable: false,
  events: events.value,
  eventClick: handleEventClick,
  eventDidMount: (info: EventMountArg) => {
    if (info.event.id.endsWith('-bg')) {
      return;
    }
    const label = info.event.extendedProps.label;
    if (label) {
      info.el.title = label;
    }
    info.el.style.cursor = 'pointer';
  },
  eventClassNames: (arg: { event: { id: string; extendedProps?: { planned?: boolean } } }) => {
    if (arg.event.id.endsWith('-bg')) {
      return [];
    }
    const classNames = ['offline-event'];
    if (arg.event.extendedProps?.planned) {
      classNames.push('planned-event');
    }
    if (props.selectedEventId && arg.event.id === props.selectedEventId) {
      classNames.push('highlighted');
    }
    return classNames;
  },
}));

const calendarRef = ref<InstanceType<typeof FullCalendar> | null>(null);

function getApi() {
  return calendarRef.value?.getApi() ?? null;
}

function goPrev() {
  getApi()?.prev();
}

function goNext() {
  getApi()?.next();
}

function goToday() {
  getApi()?.today();
}

function gotoDate(date: Date) {
  getApi()?.gotoDate(date);
}

function changeView(viewName: string) {
  getApi()?.changeView(viewName);
}

function getCurrentView() {
  return getApi()?.view?.type ?? 'timeGridWeek';
}

function getCurrentDate() {
  return getApi()?.getDate() ?? null;
}

function getTitle() {
  return getApi()?.view?.title ?? '';
}

defineExpose({
  goPrev,
  goNext,
  goToday,
  gotoDate,
  changeView,
  getCurrentView,
  getCurrentDate,
  getTitle,
});
</script>
