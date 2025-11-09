<script setup lang="ts">
import { WebSocketService } from '@/services/websocketService';
// import { Toaster } from '@/components/ui/sonner';
// import { toastPosition, toastDuration } from '@/stores/sonnerStore'; // 一個全域 ref
import { VariableEnum } from '@/enums/VariableEnum';
import { getTimeZones } from '@vvo/tzdb';
import { RouterView } from 'vue-router';
// import 'vue-sonner/style.css';

// 初始化 WebSocket 連線
WebSocketService();

// Check if timezones are already in localStorage
const existingTimezones = localStorage.getItem(VariableEnum.TimeZoneStorageKey)

if (!existingTimezones) {
  // If not, generate and store them
  const timezones = getTimeZones().map((tz) => {
    const offset = tz.currentTimeOffsetInMinutes
    const offsetHours = Math.floor(Math.abs(offset) / 60)
    const offsetMinutes = Math.abs(offset) % 60
    const sign = offset >= 0 ? '+' : '-'
    const formattedOffset = `UTC${sign}${String(offsetHours).padStart(2, '0')}:${String(
      offsetMinutes,
    ).padStart(2, '0')}`

    return {
      value: tz.name,
      label: `${tz.name} (${formattedOffset})`,
    }
  })
  localStorage.setItem(VariableEnum.TimeZoneStorageKey, JSON.stringify(timezones))
}
</script>

<template>
  <RouterView />
  <!-- <Toaster
    :duration="toastDuration"
    richColors
    :position="toastPosition"
  /> -->
</template>
