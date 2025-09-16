<script setup lang="ts">
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useSettingStore } from '@/stores/settingStore'
import { CircleAlert, CircleX, Info } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

// 1. 直接從 Pinia Store 獲取狀態並保持響應性
const settingStore = useSettingStore()
const { settings } = storeToRefs(settingStore)

const props = defineProps({
  timestamp: {
    type: String,
    required: true
  },
  level: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  }
})

const levelIcon = computed(() => {
  switch (props.level.toLowerCase()) {
    case 'info':
      return Info
    case 'warning':
      return CircleAlert
    case 'error':
      return CircleX
    default:
      return Info
  }
})

const levelClass = computed(() => {
  switch (props.level.toLowerCase()) {
    case 'warning':
      return 'text-yellow-600'
    case 'error':
      return 'text-red-600'
    default:
      return 'text-blue-600'
  }
})

const formattedTimestamp = computed(() => {
  const isoUtcString = props.timestamp.replace(' ', 'T').substring(0, 23) + 'Z';
  const options = {
    timeZone: settings.value.timezone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false, // 使用 24 小時制
  } as const;

  return new Date(isoUtcString).toLocaleString('sv-SE', options)
})
</script>

<template>
  <Alert
    class="mb-2"
    :class="`${levelClass}`"
  >
    <component
      :is="levelIcon"
      :class="`size-6 ${levelClass}`"
    />
    <AlertTitle>{{ formattedTimestamp }}</AlertTitle>
    <AlertDescription class="text-current">
      {{ message }}
    </AlertDescription>
  </Alert>
</template>