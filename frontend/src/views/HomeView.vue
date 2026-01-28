<template>
  <NCard size="small" :bordered="true">
    <template #header>
      <NFlex align="center" justify="space-between" :wrap="isMobile" class="calendar-toolbar">
        <NInputGroup size="small" class="calendar-toolbar__group">
          <NButton size="small" @click="calendarActions.prev">‹</NButton>
          <NDatePicker
            :key="datePickerType"
            size="small"
            :type="datePickerType"
            :value="datePickerValue"
            :style="{ width: isMobile ? '120px' : '160px' }"
            @update:value="handleDatePick"
          />
          <NButton size="small" @click="calendarActions.next">›</NButton>
        </NInputGroup>
        <NButtonGroup size="small" class="calendar-toolbar__views">
          <NButton
            :type="currentView === 'dayGridMonth' ? 'primary' : 'default'"
            @click="calendarActions.view('dayGridMonth')"
          >
            Monat
          </NButton>
          <NButton
            :type="currentView === 'timeGridWeek' ? 'primary' : 'default'"
            @click="calendarActions.view('timeGridWeek')"
          >
            Woche
          </NButton>
          <NButton
            :type="currentView === 'timeGridDay' ? 'primary' : 'default'"
            @click="calendarActions.view('timeGridDay')"
          >
            Tag
          </NButton>
        </NButtonGroup>
      </NFlex>
    </template>
    <CalendarView
      ref="calendarRef"
      :outages="state.outages"
      :selected-event-id="state.selectedEventId"
      :is-loading="isRefreshing"
      @select-outage="handleSelectOutage"
    />
  </NCard>
  <NDrawer v-model:show="drawerOpen" :width="drawerWidth" @update:show="handleDrawerUpdate">
    <NDrawerContent closable>
      <template #header>
        Fritz-Logs{{ drawerTitle ? ` – ${drawerTitle}` : '' }}
      </template>
      <DeviceLogTable
        :entries="drawerPageItems"
        :page="drawerPage"
        :page-count="drawerPageCount"
        @update:page="setDrawerPage"
      />
    </NDrawerContent>
  </NDrawer>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  NButton,
  NButtonGroup,
  NCard,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NFlex,
  NInputGroup,
} from 'naive-ui';
import type { DeviceLogEntry } from '../api/types';
import CalendarView from '../components/CalendarView.vue';
import DeviceLogTable from '../components/DeviceLogTable.vue';
import { useIsMobile } from '../composables/useBreakpoints';
import { useCalendarHeader } from '../composables/useCalendarHeader';
import { usePagination } from '../composables/usePagination';
import { useStoergelerState } from '../composables/useStoergelerState';

const { isRefreshing } = defineProps<{
  isRefreshing: boolean;
}>();

const { state, setSelectedEvent } = useStoergelerState();
const selectedRange = ref<{ start: Date; end: Date; label: string } | null>(null);
const drawerOpen = ref(false);
const calendarRef = ref<InstanceType<typeof CalendarView> | null>(null);
const drawerPaginator = usePagination<DeviceLogEntry>([], 20);
const isMobile = useIsMobile();
const {
  currentView,
  datePickerType,
  datePickerValue,
  handleDatePick,
  calendarActions,
} = useCalendarHeader(calendarRef);

function handleSelectOutage(payload: { eventId: string; start: Date; end: Date; label: string }) {
  setSelectedEvent(payload.eventId);
  selectedRange.value = {
    start: payload.start,
    end: payload.end,
    label: payload.label,
  };
  drawerOpen.value = true;
}

function handleDrawerUpdate(show: boolean) {
  drawerOpen.value = show;
  if (!show) {
    selectedRange.value = null;
    setSelectedEvent(null);
  }
}

function filterLogsByRange(entries: DeviceLogEntry[], start: Date, end: Date) {
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

const filteredLogs = computed(() => {
  if (!selectedRange.value) {
    return state.logs;
  }
  return filterLogsByRange(state.logs, selectedRange.value.start, selectedRange.value.end);
});

const drawerPageItems = computed(() => drawerPaginator.pageItems.value);
const drawerPage = computed(() => drawerPaginator.currentPage.value + 1);
const drawerPageCount = computed(() => drawerPaginator.totalPages.value);
const drawerTitle = computed(() => selectedRange.value?.label ?? '');
const drawerWidth = computed(() => (isMobile.value ? '100%' : 520));

function setDrawerPage(page: number) {
  drawerPaginator.currentPage.value = page - 1;
}

watch(
  filteredLogs,
  (logs) => {
    drawerPaginator.setItems(logs);
  },
  { immediate: true }
);

</script>

<style scoped>
.calendar-toolbar {
  width: 100%;
  gap: 12px;
}

@media (max-width: 768px) {
  .calendar-toolbar {
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .calendar-toolbar__group,
  .calendar-toolbar__views {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
