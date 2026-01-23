<template>
  <NConfigProvider :theme-overrides="themeOverrides" :locale="deDE" :date-locale="dateDeDE">
    <NGlobalStyle />
    <NLayout>
      <AppHeader
        v-model:active-menu="activeMenu"
        :menu-options="menuOptions"
        :is-checking="isChecking"
        :is-refreshing="isRefreshing"
        @check="handleConnectionCheck"
        @refresh="refreshData"
      />
      <NLayoutContent>
        <NSpace vertical size="large">
          <HomeView v-if="activeMenu === 'home'" :is-refreshing="isRefreshing" />
          <OutagesView v-else-if="activeMenu === 'outages'" />
          <LogsView v-else-if="activeMenu === 'logs'" />
        </NSpace>
      </NLayoutContent>
    </NLayout>
  </NConfigProvider>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import {
  NConfigProvider,
  NGlobalStyle,
  NLayout,
  NLayoutContent,
  NSpace,
} from 'naive-ui';
import { deDE, dateDeDE } from 'naive-ui';
import AppHeader from './components/AppHeader.vue';
import HomeView from './views/HomeView.vue';
import LogsView from './views/LogsView.vue';
import OutagesView from './views/OutagesView.vue';
import { useDashboardData } from './composables/useDashboardData';
import { themeOverrides } from './theme';

const { isRefreshing, isChecking, refreshData, handleConnectionCheck } = useDashboardData();
const activeMenu = ref('home');
const menuOptions = [
  { label: 'Home', key: 'home' },
  { label: 'Störungen', key: 'outages' },
  { label: 'Fritz-Logs', key: 'logs' },
];

onMounted(() => {
  refreshData();
});
</script>
