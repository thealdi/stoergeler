<template>
  <NLayoutHeader bordered class="app-header">
    <NFlex align="center" justify="space-between" :wrap="isMobile" class="app-header__row">
      <NFlex align="center" gap="12" :wrap="isMobile" class="app-header__left">
        <NButton text :focusable="false" class="app-header__logo" @click="goHome">
          <div class="app-header__logo-frame">
            <img :src="logoUrl" alt="StoerGeler" class="app-header__logo-img" />
          </div>
        </NButton>
        <NMenu
          v-if="!isMobile"
          mode="horizontal"
          :options="menuOptions"
          v-model:value="menuValue"
          class="app-header__menu"
        />
        <NDropdown
          v-else
          :options="menuOptions"
          :value="menuValue"
          trigger="click"
          @select="(value) => (menuValue = value)"
        >
          <NButton size="small" aria-label="Menü öffnen">
            <NIcon size="18">
              <MenuOutline />
            </NIcon>
          </NButton>
        </NDropdown>
      </NFlex>
      <NFlex align="center" justify="end" gap="12" :wrap="isMobile" class="app-header__actions">
        <NText depth="3" class="app-header__version">
          UI {{ uiVersion }} · API {{ backendVersion }}
        </NText>
        <NButton size="small" :disabled="isChecking" @click="$emit('check')">
          Verbindung prüfen
        </NButton>
        <NButton size="small" :disabled="isRefreshing" @click="$emit('refresh')">
          Aktualisieren
        </NButton>
      </NFlex>
    </NFlex>
  </NLayoutHeader>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { MenuOption } from 'naive-ui';
import { NButton, NDropdown, NFlex, NIcon, NLayoutHeader, NMenu, NText } from 'naive-ui';
import { MenuOutline } from '@vicons/ionicons5';
import logoUrl from '../assets/logo.png';
import { useIsMobile } from '../composables/useBreakpoints';

const props = defineProps<{
  activeMenu: string;
  menuOptions: MenuOption[];
  isChecking: boolean;
  isRefreshing: boolean;
  uiVersion: string;
  backendVersion: string;
}>();

const emit = defineEmits<{
  (event: 'update:activeMenu', value: string): void;
  (event: 'check'): void;
  (event: 'refresh'): void;
}>();

const menuValue = computed({
  get: () => props.activeMenu,
  set: (value: string) => emit('update:activeMenu', value),
});

const isMobile = useIsMobile();

function goHome() {
  emit('update:activeMenu', 'home');
}
</script>

<style scoped>
.app-header {
  min-height: 56px;
  padding: 8px 24px;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.app-header__row {
  flex-wrap: nowrap;
  width: 100%;
}

.app-header__left {
  flex-wrap: nowrap;
}

.app-header__logo {
  padding: 0;
}

.app-header__logo-frame {
  width: 42px;
  height: 42px;
  overflow: hidden;
  display: flex;
  align-items: center;
  flex: 0 0 auto;
}

.app-header__logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  display: block;
}

.app-header__menu {
  flex: none;
  display: flex;
  align-items: center;
}

.app-header__actions {
  flex-wrap: nowrap;
}

.app-header__version {
  font-size: 12px;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .app-header {
    min-height: 52px;
    padding: 8px 16px;
  }

  .app-header__row {
    gap: 12px;
    flex-wrap: wrap;
  }

  .app-header__left {
    width: 100%;
    justify-content: space-between;
  }

  .app-header__logo-frame {
    width: 36px;
    height: 36px;
  }

  .app-header__actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
