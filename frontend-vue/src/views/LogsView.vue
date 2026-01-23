<template>
  <DeviceLogTable
    :entries="logPageItems"
    :page="logPage"
    :page-count="logPageCount"
    @update:page="setLogPage"
  />
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import type { DeviceLogEntry } from '../api/types';
import DeviceLogTable from '../components/DeviceLogTable.vue';
import { usePagination } from '../composables/usePagination';
import { useStoergelerState } from '../composables/useStoergelerState';

const { state } = useStoergelerState();
const logPaginator = usePagination<DeviceLogEntry>([], 20);

const logPageItems = computed(() => logPaginator.pageItems.value);
const logPage = computed(() => logPaginator.currentPage.value + 1);
const logPageCount = computed(() => logPaginator.totalPages.value);

function setLogPage(page: number) {
  logPaginator.currentPage.value = page - 1;
}

watch(
  () => state.logs,
  (logs) => {
    logPaginator.setItems(logs);
  },
  { immediate: true }
);
</script>
