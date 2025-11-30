<script lang="ts" setup>
import { Toaster } from '@/components/ui/sonner';
import { useWebSocketService } from '@/composables/useWebSocketService';
import { toastDuration, toastPosition } from '@/stores/sonnerStore'; // 一個全域 ref
import { initializeTimeZones } from '@/utils/timeZone';
import { RouterView } from 'vue-router';
import 'vue-sonner/style.css';

// 初始化 WebSocket 連線
useWebSocketService();
// 初始化時區資料
initializeTimeZones();
</script>

<template>
  <RouterView />
  <Toaster
    :duration="toastDuration"
    richColors
    :position="toastPosition"
  />
</template>
