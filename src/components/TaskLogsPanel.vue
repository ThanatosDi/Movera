<script setup lang="ts">
import LogItem from '@/components/LogItem.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Log } from '@/schemas'
import { RefreshCw } from 'lucide-vue-next'
import { ref, type ComponentPublicInstance } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

defineProps<{
  logs: Log[]
  isLoading: boolean
}>()

const emit = defineEmits<{
  (e: 'reload'): void
}>()

const logCard = ref<ComponentPublicInstance | null>(null)

const handleReload = () => {
  emit('reload')
}

defineExpose({
  scrollIntoView: () => {
    const element = logCard.value?.$el as HTMLElement
    element?.scrollIntoView({ behavior: 'smooth' })
  }
})
</script>

<template>
  <Card
    ref="logCard"
    class="mt-4 border border-border"
  >
    <CardHeader class="flex flex-row items-center justify-between">
      <div>
        <CardTitle>{{ t('taskDetailView.logsCardTitle') }}</CardTitle>
        <CardDescription>{{ t('taskDetailView.logsCardDescription') }}</CardDescription>
      </div>
      <Button
        @click="handleReload"
        :disabled="isLoading"
        size="sm"
        class="bg-background text-foreground border-foreground hover:bg-accent hover:text-foreground"
      >
        <RefreshCw
          class="size-4 mr-2"
          :class="{ 'animate-spin': isLoading }"
        />
        {{ isLoading ? t('common.loading') : t('common.reload') }}
      </Button>
    </CardHeader>
    <CardContent class="space-y-2">
      <div
        v-if="isLoading"
        class="text-center text-gray-400 py-4"
      >
        <p>{{ t('taskDetailView.loadingLogs') }}</p>
      </div>
      <div
        v-else-if="logs.length > 0"
        class="space-y-2"
      >
        <ScrollArea class="h-72 rounded-md">
          <LogItem
            v-for="log in logs"
            :key="log.id"
            :timestamp="log.timestamp"
            :level="log.level"
            :message="log.message"
          />
        </ScrollArea>
      </div>
      <div
        v-else
        class="text-center text-gray-400 py-4"
      >
        <p>{{ t('taskDetailView.noLogs') }}</p>
      </div>
    </CardContent>
  </Card>
</template>
