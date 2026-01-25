<template>
  <NCard size="small" :bordered="true">
    <NDataTable :columns="columns" :data="entries" :bordered="false" />
    <template #footer v-if="props.pageCount > 1">
      <NPagination
        size="small"
        :page="props.page"
        :page-count="props.pageCount"
        @update:page="(value) => $emit('update:page', value)"
      />
    </template>
  </NCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { NCard, NDataTable, NPagination } from 'naive-ui';
import type { DataTableColumns } from 'naive-ui';
import type { OutageWindow } from '../api/types';
import { formatDate, formatDuration } from '../utils/format';

const props = defineProps<{
  entries: OutageWindow[];
  page: number;
  pageCount: number;
}>();

defineEmits<{
  (event: 'update:page', value: number): void;
}>();

const columns = computed<DataTableColumns<OutageWindow>>(() => [
  {
    title: 'Start',
    key: 'start',
    render: (row) => (row.start ? formatDate(row.start) : 'Unbekannt'),
  },
  {
    title: 'Ende',
    key: 'end',
    render: (row) => (row.end ? formatDate(row.end) : 'läuft...'),
  },
  {
    title: 'Dauer',
    key: 'duration_seconds',
    render: (row) => formatDuration(row.duration_seconds),
  },
  {
    title: 'Kategorie',
    key: 'status',
    render: (row) => row.status ?? 'unbekannt',
  },
]);
</script>
