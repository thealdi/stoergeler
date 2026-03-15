<template>
  <NSpace vertical size="large">
    <NCard title="Verfügbarkeit & Stabilitäts-KPIs" :bordered="true">
      <template #header-extra>
        <NFlex align="center">
          <NButton size="small" secondary @click="exportToJson">Export JSON</NButton>
          <NButton size="small" secondary @click="createReport">Wochen-Report</NButton>
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
} from 'naive-ui';
import { InformationCircleOutline } from '@vicons/ionicons5';
import { useStoergelerState } from '../composables/useStoergelerState';
import { useIsMobile } from '../composables/useBreakpoints';
import { formatDuration, formatDate } from '../utils/format';

const { state } = useStoergelerState();
const isMobile = useIsMobile();

const unplannedOutages = computed(() =>
  state.outages.filter((o) => !o.status?.startsWith('planned'))
);

const plannedOutages = computed(() =>
  state.outages.filter((o) => o.status?.startsWith('planned'))
);

const totalTimeSeconds = computed(() => {
  if (state.outages.length === 0) return 0;
  // Compute time from first record until now
  const firstOutage = state.outages[state.outages.length - 1];
  if (!firstOutage || !firstOutage.start) return 0;
  const startMs = new Date(firstOutage.start).getTime();
  const nowMs = Date.now();
  return Math.max(1, (nowMs - startMs) / 1000);
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

function createReport() {
  const now = new Date();
  const monday = new Date(now);
  monday.setDate(now.getDate() - ((now.getDay() + 6) % 7));
  monday.setHours(0, 0, 0, 0);

  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  sunday.setHours(23, 59, 59, 999);

  const weekOutages = state.outages.filter((o) => {
    const start = new Date(o.start);
    return start >= monday && start <= sunday;
  });

  const weekLogs = state.logs.filter((l) => {
    if (!l.timestamp) return false;
    const ts = new Date(l.timestamp);
    return ts >= monday && ts <= sunday;
  });

  const unplanned = weekOutages.filter((o) => !o.status?.startsWith('planned'));
  const planned = weekOutages.filter((o) => o.status?.startsWith('planned'));
  const totalDowntime = unplanned.reduce((acc, o) => acc + (o.duration_seconds || 0), 0);
  const maxDowntime = unplanned.reduce((max, o) => Math.max(max, o.duration_seconds || 0), 0);

  const html = `
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Verbindungs-Report (KW ${getWeekNumber(monday)})</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #333; max-width: 900px; margin: 40px auto; padding: 0 20px; }
        h1, h2 { color: #111; border-bottom: 2px solid #eee; padding-bottom: 8px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
        .kpi-card { border: 1px solid #eee; padding: 15px; border-radius: 8px; background: #fafafa; }
        .kpi-val { font-size: 20px; font-weight: bold; color: #222; }
        .kpi-label { font-size: 12px; color: #666; margin-bottom: 4px; }
        .calendar-week { display: flex; border: 1px solid #ddd; height: 120px; border-radius: 8px; overflow: hidden; margin: 20px 0; }
        .calendar-day { flex: 1; border-right: 1px solid #ddd; padding: 8px; position: relative; background: #fff; }
        .calendar-day:last-child { border-right: none; }
        .day-label { font-size: 11px; font-weight: bold; margin-bottom: 4px; color: #888; text-transform: uppercase; }
        .outage-mark { position: absolute; left: 0; right: 0; height: 4px; background: #ef4444; }
        .outage-mark.planned { background: #3b82f6; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #eee; }
        th { background: #f8f8f8; color: #555; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
        .status-unplanned { background: #fee2e2; color: #991b1b; }
        .status-planned { background: #dbeafe; color: #1e40af; }
    </style>
</head>
<body>
    <h1>StoerGeler Verbindungs-Report</h1>
    <p>Berichtszeitraum: <strong>${monday.toLocaleDateString('de-DE')}</strong> bis <strong>${sunday.toLocaleDateString('de-DE')}</strong></p>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Störungen (Ungeplant)</div>
            <div class="kpi-val">${unplanned.length}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Geplante Wartungen</div>
            <div class="kpi-val">${planned.length}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Gesamte Downtime</div>
            <div class="kpi-val">${formatDuration(totalDowntime)}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Max. Ausfallzeit</div>
            <div class="kpi-val">${formatDuration(maxDowntime)}</div>
        </div>
    </div>

    <h2>Wochen-Überblick</h2>
    <div class="calendar-week">
        ${Array.from({ length: 7 }).map((_, i) => {
          const d = new Date(monday);
          d.setDate(monday.getDate() + i);
          const dayOutages = weekOutages.filter((o) => new Date(o.start).toDateString() === d.toDateString());
          return `
            <div class="calendar-day">
                <div class="day-label">${d.toLocaleDateString('de-DE', { weekday: 'short' })}</div>
                ${dayOutages.map((o) => {
                  const s = new Date(o.start);
                  const top = (s.getHours() * 60 + s.getMinutes()) / 1440 * 100;
                  return `<div class="outage-mark ${o.status?.startsWith('planned') ? 'planned' : ''}" style="top: ${top}%;" title="${formatDuration(o.duration_seconds)}"></div>`;
                }).join('')}
            </div>
          `;
        }).join('')}
    </div>

    <h2>Störungs-Historie (Woche)</h2>
    <table>
        <thead><tr><th>Beginn</th><th>Ende</th><th>Dauer</th><th>Typ</th></tr></thead>
        <tbody>
            ${weekOutages.map((o) => `
                <tr>
                    <td>${formatDate(o.start)}</td>
                    <td>${o.end ? formatDate(o.end) : 'läuft noch'}</td>
                    <td>${formatDuration(o.duration_seconds)}</td>
                    <td><span class="status-badge ${o.status?.startsWith('planned') ? 'status-planned' : 'status-unplanned'}">
                        ${o.status?.startsWith('planned') ? 'Geplant' : 'Ungeplant'}
                    </span></td>
                </tr>
            `).join('')}
            ${weekOutages.length === 0 ? '<tr><td colspan="4">Keine Störungen in dieser Woche.</td></tr>' : ''}
        </tbody>
    </table>

    <h2>Ereignis-Log (Woche)</h2>
    <table>
        <thead><tr><th>Zeitpunkt</th><th>Nachricht</th></tr></thead>
        <tbody>
            ${weekLogs.map((l) => `
                <tr>
                    <td style="white-space: nowrap;">${l.timestamp ? formatDate(l.timestamp) : ''}</td>
                    <td>${l.message || l.raw}</td>
                </tr>
            `).join('')}
            ${weekLogs.length === 0 ? '<tr><td colspan="2">Keine Log-Einträge in dieser Woche.</td></tr>' : ''}
        </tbody>
    </table>
</body>
</html>`;

  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `stoergeler_report_KW${getWeekNumber(monday)}_${monday.getFullYear()}.html`;
  link.click();
  URL.revokeObjectURL(url);
}

function getWeekNumber(d: Date) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNum = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  return Math.ceil((((date.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
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
