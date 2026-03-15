<template>
  <NConfigProvider :theme-overrides="themeOverrides" :locale="deDE" :date-locale="dateDeDE">
    <NGlobalStyle />
    <NMessageProvider>
      <NLayout>
        <AppHeader
          v-model:active-menu="activeMenu"
          :menu-options="menuOptions"
          :is-checking="isChecking"
          :is-refreshing="isRefreshing"
          :ui-version="uiVersion"
          :backend-version="backendVersion"
          @check="handleConnectionCheck"
          @refresh="refreshData"
        />
        <NLayoutContent>
          <NSpace vertical size="large">
            <HomeView v-if="activeMenu === 'home'" :is-refreshing="isRefreshing" />
            <OutagesView v-else-if="activeMenu === 'outages'" />
            <ReportingView v-else-if="activeMenu === 'reporting'" />
            <LogsView v-else-if="activeMenu === 'logs'" />
          </NSpace>
        </NLayoutContent>
      </NLayout>
    </NMessageProvider>
  </NConfigProvider>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import {
  NConfigProvider,
  NSpace,
  NGlobalStyle,
  NLayout,
  NLayoutContent,
  NMessageProvider,
} from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import AppHeader from './components/AppHeader.vue';
import HomeView from './views/HomeView.vue';
import LogsView from './views/LogsView.vue';
import OutagesView from './views/OutagesView.vue';
import ReportingView from './views/ReportingView.vue';
import { useDashboardData } from './composables/useDashboardData';
import { themeOverrides } from './theme';
import { fetchBackendVersion } from './api/client';

const { isRefreshing, isChecking, refreshData, handleConnectionCheck } = useDashboardData();
const activeMenu = ref('home');
const backendVersion = ref<string>('loading…');
const uiVersion = import.meta.env.VITE_APP_VERSION || 'dev';
const menuOptions = [
  { label: 'Home', key: 'home' },
  { label: 'Störungen', key: 'outages' },
  { label: 'Reporting', key: 'reporting' },
  { label: 'Fritz-Logs', key: 'logs' },
];

onMounted(() => {
  refreshData();
  fetchBackendVersion()
    .then((data) => {
      backendVersion.value = data.version ?? 'unknown';
    })
    .catch(() => {
      backendVersion.value = 'unavailable';
    });
});
</script>
