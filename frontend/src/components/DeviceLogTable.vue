<template>
  <NCard size="small" :bordered="true">
    <div class="data-table-wrap">
      <NDataTable :columns="columns" :data="sortedEntries" :bordered="false" />
    </div>
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
import type { DeviceLogEntry } from '../api/types';
import { formatDate } from '../utils/format';

const props = defineProps<{
  entries: DeviceLogEntry[];
  page: number;
  pageCount: number;
}>();

defineEmits<{
  (event: 'update:page', value: number): void;
}>();

const sortedEntries = computed(() =>
  props.entries
    .slice()
    .sort((a, b) => {
      const timeA = a.timestamp ? new Date(a.timestamp).getTime() : -Infinity;
      const timeB = b.timestamp ? new Date(b.timestamp).getTime() : -Infinity;
      return timeB - timeA;
    })
);

const columns = computed<DataTableColumns<DeviceLogEntry>>(() => [
  {
    title: 'Zeit',
    key: 'timestamp',
    minWidth: 100,
    render: (row) => formatTimestamp(row.timestamp),
  },
  {
    title: 'Meldung',
    key: 'message',
    render: (row) => row.message ?? row.raw ?? '',
  },
]);

function formatTimestamp(timestamp?: string | null) {
  if (!timestamp) {
    return 'Unbekannt';
  }
  return formatDate(timestamp);
}
</script>

<style scoped>
.data-table-wrap {
  width: 100%;
}

@media (max-width: 768px) {
  .data-table-wrap {
    overflow-x: auto;
  }
}
</style>
