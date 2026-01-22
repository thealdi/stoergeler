<template>
  <NConfigProvider :theme-overrides="themeOverrides" :locale="deDE" :date-locale="dateDeDE">
    <NGlobalStyle />
    <NLayout>
      <NLayoutHeader bordered :style="{ padding: '16px 24px' }">
        <NFlex align="center" justify="space-between" :wrap="false" :style="{ flexWrap: 'nowrap' }">
          <NFlex align="center" gap="12" :wrap="false" :style="{ flexWrap: 'nowrap' }">
            <NButton
              text
              :focusable="false"
              @click="activeMenu = 'home'"
              style="padding: 0;"
            >
              <div
                style="width: 180px; height: 50px; overflow: hidden; display: flex; align-items: center; flex: 0 0 auto;"
              >
                <img
                  :src="logoUrl"
                  alt="StoerGeler"
                  style="width: 100%; height: 100%; object-fit: cover; object-position: left center; display: block;"
                />
              </div>
            </NButton>
            <NMenu
              mode="horizontal"
              :options="menuOptions"
              v-model:value="activeMenu"
              :style="{ flex: 'none', display: 'flex', alignItems: 'center' }"
            />
          </NFlex>
          <NFlex align="center" justify="end" gap="12" :wrap="false" :style="{ flexWrap: 'nowrap' }">
            <NButton size="small" :disabled="isChecking" @click="handleConnectionCheck">
              Verbindung prüfen
            </NButton>
            <NButton size="small" :disabled="isRefreshing" @click="refreshData">
              Aktualisieren
            </NButton>
          </NFlex>
        </NFlex>
      </NLayoutHeader>
      <NLayoutContent>
        <NSpace vertical size="large">
          <template v-if="activeMenu === 'home'">
            <NCard size="small" :bordered="true">
              <template #header>
                <NFlex align="center" justify="space-between" :wrap="false">
                  <NInputGroup size="small">
                    <NButton size="small" @click="calendarActions.prev">‹</NButton>
                    <NDatePicker
                      :key="datePickerType"
                      size="small"
                      :type="datePickerType"
                      :value="datePickerValue"
                      :style="{ width: '160px' }"
                      @update:value="handleDatePick"
                    />
                    <NButton size="small" @click="calendarActions.next">›</NButton>
                  </NInputGroup>
                  <NButtonGroup size="small">
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
            <NDrawer v-model:show="drawerOpen" :width="520" @update:show="handleDrawerUpdate">
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

          <template v-else-if="activeMenu === 'outages'">
            <OutageTable
              :entries="outagePageItems"
              :page="outagePage"
              :page-count="outagePageCount"
              @update:page="setOutagePage"
            />
          </template>

          <template v-else-if="activeMenu === 'logs'">
            <DeviceLogTable
              :entries="logPageItems"
              :page="logPage"
              :page-count="logPageCount"
              @update:page="setLogPage"
            />
          </template>
        </NSpace>
      </NLayoutContent>
    </NLayout>
  </NConfigProvider>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  NButton,
  NButtonGroup,
  NCard,
  NConfigProvider,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NFlex,
  NGlobalStyle,
  NInputGroup,
  NLayout,
  NLayoutContent,
  NLayoutHeader,
  NMenu,
  NSpace,
  createDiscreteApi,
} from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import { fetchConnectionStatus, fetchDeviceLog, fetchOutages } from './api/client';
import type { ConnectivityStatus, DeviceLogEntry, OutageWindow } from './api/types';
import logoUrl from './assets/logo.png';
import CalendarView from './components/CalendarView.vue';
import DeviceLogTable from './components/DeviceLogTable.vue';
import OutageTable from './components/OutageTable.vue';
import { usePagination } from './composables/usePagination';
import { useStoergelerState } from './composables/useStoergelerState';

const { state, setOutages, setLogs, setSelectedEvent } = useStoergelerState();
const selectedRange = ref<{ start: Date; end: Date; label: string } | null>(null);
const drawerOpen = ref(false);
const calendarRef = ref<InstanceType<typeof CalendarView> | null>(null);
const currentView = ref('timeGridWeek');
const datePickerValue = ref<number | null>(null);
const isRefreshing = ref(false);
const isChecking = ref(false);
const outagePaginator = usePagination<OutageWindow>([], 20);
const logPaginator = usePagination<DeviceLogEntry>([], 20);
const drawerPaginator = usePagination<DeviceLogEntry>([], 20);
const activeMenu = ref('home');
const menuOptions = [
  { label: 'Home', key: 'home' },
  { label: 'Störungen', key: 'outages' },
  { label: 'Fritz-Logs', key: 'logs' },
];

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

const datePickerType = computed(() => {
  switch (currentView.value) {
    case 'dayGridMonth':
      return 'month';
    case 'timeGridWeek':
      return 'week';
    case 'timeGridDay':
      return 'date';
    default:
      return 'date';
  }
});

function syncCalendarHeader() {
  const currentDate = calendarRef.value?.getCurrentDate() ?? new Date();
  datePickerValue.value = currentDate.getTime();
}

function handleDatePick(value: number | null) {
  if (!value) {
    return;
  }
  calendarRef.value?.gotoDate(new Date(value));
  syncCalendarHeader();
}

const calendarActions = {
  prev: () => {
    calendarRef.value?.goPrev();
    syncCalendarHeader();
  },
  next: () => {
    calendarRef.value?.goNext();
    syncCalendarHeader();
  },
  view: (viewName: string) => {
    calendarRef.value?.changeView(viewName);
    currentView.value = viewName;
    syncCalendarHeader();
  },
};

const themeOverrides = {
  common: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif',
    primaryColor: '#4a4f55',
    primaryColorHover: '#5a6067',
    primaryColorPressed: '#3f454b',
    primaryColorSuppl: '#4a4f55',
    borderRadius: '2px',
  },
  Button: {
    borderRadiusMedium: '2px',
    borderRadiusSmall: '2px',
  },
  Card: {
    borderRadius: '2px',
  },
  Pagination: {
    buttonBorderRadius: '2px',
  },
  Tag: {
    borderRadius: '2px',
  },
  DataTable: {
    borderRadius: '2px',
  },
  Menu: {
    itemTextColorActiveHorizontal: '#3b82f6',
    itemTextColorActiveHoverHorizontal: '#3b82f6',
    itemTextColorHoverHorizontal: '#3b82f6',
  },
};

const { message } = createDiscreteApi(['message'], {
  configProviderProps: {
    themeOverrides,
  },
  messageProviderProps: {
    placement: 'top',
    keepAliveOnHover: true,
  },
});

const outagePageItems = computed(() => outagePaginator.pageItems.value);
const logPageItems = computed(() => logPaginator.pageItems.value);
const drawerPageItems = computed(() => drawerPaginator.pageItems.value);
const outagePage = computed(() => outagePaginator.currentPage.value + 1);
const logPage = computed(() => logPaginator.currentPage.value + 1);
const drawerPage = computed(() => drawerPaginator.currentPage.value + 1);
const outagePageCount = computed(() => outagePaginator.totalPages.value);
const logPageCount = computed(() => logPaginator.totalPages.value);
const drawerPageCount = computed(() => drawerPaginator.totalPages.value);
const drawerTitle = computed(() => selectedRange.value?.label ?? '');

function setOutagePage(page: number) {
  outagePaginator.currentPage.value = page - 1;
}

function setLogPage(page: number) {
  logPaginator.currentPage.value = page - 1;
}

function setDrawerPage(page: number) {
  drawerPaginator.currentPage.value = page - 1;
}

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
    outagePaginator.setItems(sortedOutages);
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

watch(
  () => state.logs,
  (logs) => {
    logPaginator.setItems(logs);
  },
  { immediate: true }
);

watch(
  filteredLogs,
  (logs) => {
    drawerPaginator.setItems(logs);
  },
  { immediate: true }
);

watch(currentView, () => {
  syncCalendarHeader();
});

onMounted(() => {
  refreshData();
  currentView.value = calendarRef.value?.getCurrentView() ?? 'timeGridWeek';
  syncCalendarHeader();
});
</script>
