<template>
  <OutageTable
    :entries="outagePageItems"
    :page="outagePage"
    :page-count="outagePageCount"
    @update:page="setOutagePage"
  />
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import type { OutageWindow } from '../api/types';
import OutageTable from '../components/OutageTable.vue';
import { usePagination } from '../composables/usePagination';
import { useStoergelerState } from '../composables/useStoergelerState';

const { state } = useStoergelerState();
const outagePaginator = usePagination<OutageWindow>([], 20);

const outagePageItems = computed(() => outagePaginator.pageItems.value);
const outagePage = computed(() => outagePaginator.currentPage.value + 1);
const outagePageCount = computed(() => outagePaginator.totalPages.value);

function setOutagePage(page: number) {
  outagePaginator.currentPage.value = page - 1;
}

watch(
  () => state.outages,
  (outages) => {
    outagePaginator.setItems(outages);
  },
  { immediate: true }
);
</script>
