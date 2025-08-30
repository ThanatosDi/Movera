<script setup="js">
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { CircleAlert, CircleX, Info } from 'lucide-vue-next'
import { computed } from 'vue'

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
  return new Date(props.timestamp).toLocaleString()
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