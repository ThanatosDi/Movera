<script lang="ts" setup>
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { WebSocketService } from '@/services/websocketService'
import { CheckCircle, XCircle } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { status: websocketStatus, data } = WebSocketService()
</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto min-h-0 pb-6`">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('homeView.title') }}</h1>
      <p class="text-muted-foreground">{{ t('homeView.description') }}</p>
    </div>

    <!-- WebSocket 狀態卡片 -->
    <Card class="border-border">
      <CardHeader>
        <CardTitle>WebSocket Status</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Status: {{ websocketStatus }}</p>
        <p>Data: {{ data }}</p>
      </CardContent>
    </Card>

    <!-- 統計卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 已啟動任務 -->
      <Card class="border-border">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">{{ t('homeView.enabledTasks') }}</CardTitle>
          <CheckCircle class="size-8 text-green-400" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-400">{{ enabledTasksCount ?? 0 }}</div>
          <p class="text-xs text-muted-foreground">{{ t('homeView.enabledTasksDesc') }}</p>
        </CardContent>
      </Card>

      <!-- 已停用任務 -->
      <Card class="border-border">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">{{ t('homeView.disabledTasks') }}</CardTitle>
          <XCircle class="size-8 text-red-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-red-500">{{ disabledTasksCount ?? 0 }}</div>
          <p class="text-xs text-muted-foreground">{{ t('homeView.disabledTasksDesc') }}</p>
        </CardContent>
      </Card>
    </div>
  </main>
</template>