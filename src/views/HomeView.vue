<script lang="ts" setup>
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useWebSocketService } from '@/composables/useWebSocketService';
import { useTaskStore } from '@/stores/taskStore';
import { CheckCircle, LoaderCircle, XCircle } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';


const { t } = useI18n()
const { status: websocketStatus } = useWebSocketService()
const taskStore = useTaskStore()
const { isLoading, enabledTaskCount, disabledTaskCount } = storeToRefs(taskStore)

</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto min-h-0 pb-6`">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('homeView.title') }}</h1>
      <p class="text-muted-foreground">{{ t('homeView.description') }}</p>
    </div>

    <!-- 統計卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 已啟動任務 -->
      <Card class="border-border">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">{{ t('homeView.enabledTasks') }}</CardTitle>
          <CheckCircle class="size-8 text-green-400" />
        </CardHeader>
        <CardContent>
          <div
            v-if="websocketStatus === 'OPEN' && !isLoading"
            class="text-2xl font-bold text-green-400"
          >{{ enabledTaskCount ?? 0 }}</div>
          <LoaderCircle
            v-else
            class="animate-spin"
          />
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
          <div
            v-if="websocketStatus === 'OPEN' && !isLoading"
            class="text-2xl font-bold text-red-500"
          >{{ disabledTaskCount ?? 0 }}</div>
          <LoaderCircle
            v-else
            class="animate-spin"
          />
          <p class="text-xs text-muted-foreground">{{ t('homeView.disabledTasksDesc') }}</p>
        </CardContent>
      </Card>
    </div>
  </main>
</template>