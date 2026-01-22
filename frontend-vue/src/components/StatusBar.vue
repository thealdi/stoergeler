<template>
  <NSpace align="center" wrap>
    <NTag :type="type" size="small">{{ message }}</NTag>
    <NButton :disabled="disableCheck" @click="$emit('check')">Verbindung prüfen</NButton>
    <NButton :disabled="disableRefresh" @click="$emit('refresh')">Aktualisieren</NButton>
  </NSpace>
</template>

<script setup lang="ts">
import { NButton, NSpace, NTag } from 'naive-ui';

defineProps<{
  message: string;
  type: 'info' | 'success' | 'error';
  disableCheck?: boolean;
  disableRefresh?: boolean;
}>();

defineEmits<{
  (event: 'check'): void;
  (event: 'refresh'): void;
}>();
</script>
