<template>
  <NSpace vertical size="large">
    <NCard title="Verfügbarkeit & Stabilitäts-KPIs" :bordered="true">
      <template #header-extra>
        <NFlex align="center">
          <NButton size="small" secondary @click="handleSendTestEmail">Test-Email</NButton>
          <NButton size="small" secondary @click="exportToJson">Export JSON</NButton>
          <NButton size="small" secondary @click="handleCreateReport">Wochen-Report</NButton>
        </NFlex>
      </template>
      <NGrid :cols="isMobile ? 1 : 4" :x-gap="12" :y-gap="12">
        <NGi>
          <NCard size="small" :bordered="false" class="kpi-card">
            <NStatistic :value="availabilityFormatted">
              <template #label>
                <NFlex align="center" :size="4">
                  Uptime (%)
                  <NTooltip trigger="click">
                    <template #trigger>
                      <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                    </template>
                    Anteil der Zeit, in der die Verbindung ohne ungeplante Unterbrechungen aktiv war (bezogen auf den gesamten Erfassungszeitraum).
                  </NTooltip>
                </NFlex>
              </template>
              <template #suffix> % </template>
            </NStatistic>
            <NProgress
              type="line"
              status="success"
              :percentage="parseFloat(availabilityFormatted)"
              :show-indicator="false"
              class="kpi-progress"
            />
          </NCard>
        </NGi>
        <NGi>
          <NCard size="small" :bordered="false" class="kpi-card">
            <NStatistic :value="totalDowntimeFormatted">
              <template #label>
                <NFlex align="center" :size="4">
                  Total Downtime (Ungeplant)
                  <NTooltip trigger="click">
                    <template #trigger>
                      <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                    </template>
                    Gesamte Zeitspanne aller Ausfälle, die nicht als geplant (z.B. Wartung) markiert wurden.
                  </NTooltip>
                </NFlex>
              </template>
            </NStatistic>
          </NCard>
        </NGi>
        <NGi>
          <NCard size="small" :bordered="false" class="kpi-card">
            <NStatistic :value="incidentCount">
              <template #label>
                <NFlex align="center" :size="4">
                  Störungen (Anzahl)
                  <NTooltip trigger="click">
                    <template #trigger>
                      <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                    </template>
                    Die Anzahl der einzelnen, ungeplanten Verbindungsunterbrechungen.
                  </NTooltip>
                </NFlex>
              </template>
            </NStatistic>
          </NCard>
        </NGi>
        <NGi>
          <NCard size="small" :bordered="false" class="kpi-card">
            <NStatistic :value="longestOutageFormatted">
              <template #label>
                <NFlex align="center" :size="4">
                  Max. Ausfallzeit
                  <NTooltip trigger="click">
                    <template #trigger>
                      <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                    </template>
                    Die längste einzelne, ungeplante Verbindungsunterbrechung im Erfassungszeitraum.
                  </NTooltip>
                </NFlex>
              </template>
            </NStatistic>
          </NCard>
        </NGi>
      </NGrid>
    </NCard>

    <NGrid :cols="isMobile ? 1 : 2" :x-gap="12" :y-gap="12">
      <NGi>
        <NCard title="Wartung & Planung" size="small">
          <NGrid :cols="2">
            <NGi>
              <NStatistic :value="plannedCount">
                <template #label>
                  <NFlex align="center" :size="4">
                    Geplante Wartungen
                    <NTooltip trigger="click">
                      <template #trigger>
                        <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                      </template>
                      Anzahl der Ausfälle, die durch bekannte Muster (z.B. Zwangstrennung) als geplant erkannt wurden.
                    </NTooltip>
                  </NFlex>
                </template>
              </NStatistic>
            </NGi>
            <NGi>
              <NStatistic :value="plannedDowntimeFormatted">
                <template #label>
                  <NFlex align="center" :size="4">
                    Geplante Downtime
                    <NTooltip trigger="click">
                      <template #trigger>
                        <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                      </template>
                      Gesamte Zeitspanne aller geplanten Unterbrechungen.
                    </NTooltip>
                  </NFlex>
                </template>
              </NStatistic>
            </NGi>
          </NGrid>
        </NCard>
      </NGi>
      <NGi>
        <NCard title="Durchschnittswerte" size="small">
          <NGrid :cols="2">
            <NGi>
              <NStatistic :value="mttrFormatted">
                <template #label>
                  <NFlex align="center" :size="4">
                    MTTR (Reparaturzeit)
                    <NTooltip trigger="click">
                      <template #trigger>
                        <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                      </template>
                      Mean Time To Repair: Die durchschnittliche Dauer einer ungeplanten Störung.
                    </NTooltip>
                  </NFlex>
                </template>
              </NStatistic>
            </NGi>
            <NGi>
              <NStatistic :value="mtbfFormatted">
                <template #label>
                  <NFlex align="center" :size="4">
                    MTBF (Betriebszeit)
                    <NTooltip trigger="click">
                      <template #trigger>
                        <NIcon size="14" class="info-icon"><InformationCircleOutline /></NIcon>
                      </template>
                      Mean Time Between Failures: Die durchschnittliche Zeit zwischen zwei ungeplanten Störungen.
                    </NTooltip>
                  </NFlex>
                </template>
              </NStatistic>
            </NGi>
          </NGrid>
        </NCard>
      </NGi>
    </NGrid>

    <NCard v-if="state.outages.length === 0" :bordered="false">
      <NEmpty description="Keine Daten für eine Auswertung verfügbar." />
    </NCard>
  </NSpace>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import {
  NCard,
  NGrid,
  NGi,
  NStatistic,
  NProgress,
  NSpace,
  NEmpty,
  NTooltip,
  NIcon,
  NFlex,
  NButton,
  useMessage,
} from 'naive-ui';
import { InformationCircleOutline } from '@vicons/ionicons5';
import { useStoergelerState } from '../composables/useStoergelerState';
import { useIsMobile } from '../composables/useBreakpoints';
import { formatDuration } from '../utils/format';
import { fetchWeeklyReport, sendTestEmail } from '../api/client';

const { state } = useStoergelerState();
const isMobile = useIsMobile();
const message = useMessage();

const unplannedOutages = computed(() =>
  state.outages.filter((o) => !o.status?.startsWith('planned'))
);

const plannedOutages = computed(() =>
  state.outages.filter((o) => o.status?.startsWith('planned'))
);

const totalTimeSeconds = computed(() => {
  if (state.outages.length === 0) return 0;
  // Find the truly oldest record (min start time) regardless of array order
  const timestamps = state.outages.map(o => new Date(o.start).getTime());
  const minTs = Math.min(...timestamps);
  const nowMs = Date.now();
  return Math.max(1, (nowMs - minTs) / 1000);
});


const totalDowntimeSeconds = computed(() =>
  unplannedOutages.value.reduce((acc, o) => acc + (o.duration_seconds || 0), 0)
);

const totalDowntimeFormatted = computed(() => formatDuration(totalDowntimeSeconds.value));

const plannedDowntimeSeconds = computed(() =>
  plannedOutages.value.reduce((acc, o) => acc + (o.duration_seconds || 0), 0)
);

const plannedDowntimeFormatted = computed(() => formatDuration(plannedDowntimeSeconds.value));

const incidentCount = computed(() => unplannedOutages.value.length);
const plannedCount = computed(() => plannedOutages.value.length);

const availability = computed(() => {
  if (totalTimeSeconds.value === 0) return 100;
  const uptime = totalTimeSeconds.value - totalDowntimeSeconds.value;
  return (uptime / totalTimeSeconds.value) * 100;
});

const availabilityFormatted = computed(() => availability.value.toFixed(3));

const longestOutageSeconds = computed(() =>
  unplannedOutages.value.reduce((max, o) => Math.max(max, o.duration_seconds || 0), 0)
);

const longestOutageFormatted = computed(() => formatDuration(longestOutageSeconds.value));

const mttrSeconds = computed(() => {
  if (incidentCount.value === 0) return 0;
  return totalDowntimeSeconds.value / incidentCount.value;
});

const mttrFormatted = computed(() => formatDuration(mttrSeconds.value));

const mtbfSeconds = computed(() => {
  if (incidentCount.value === 0) return totalTimeSeconds.value;
  // MTBF = (Total Time - Total Downtime) / Number of failures
  return (totalTimeSeconds.value - totalDowntimeSeconds.value) / incidentCount.value;
});

const mtbfFormatted = computed(() => formatDuration(mtbfSeconds.value));

function exportToJson() {
  const blob = new Blob([JSON.stringify(state.outages, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `stoergeler_outages_${new Date().toISOString().split('T')[0]}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

async function handleCreateReport() {
  try {
    const html = await fetchWeeklyReport('current');
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `stoergeler_report_${new Date().toISOString().split('T')[0]}.html`;
    link.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    message.error('Fehler beim Erstellen des Reports');
  }
}

async function handleSendTestEmail() {
  try {
    await sendTestEmail();
    message.success('Test-Email wurde versendet');
  } catch (err) {
    message.error('Fehler beim Senden der Test-Email');
  }
}

</script>

<style scoped>
.kpi-card {
  background-color: var(--n-card-color);
  transition: transform 0.2s ease-in-out;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-progress {
  margin-top: 12px;
}

.info-icon {
  cursor: pointer;
  color: var(--n-text-color-3);
  transition: color 0.2s ease-in-out;
  margin-left: 4px;
}

.info-icon:hover {
  color: var(--n-primary-color);
}
</style>
