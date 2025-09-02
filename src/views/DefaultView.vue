<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTaskStore } from '@/stores/taskStore';
import { CheckCircle, LoaderCircle, XCircle } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { onMounted } from 'vue';


// Store
const taskStore = useTaskStore()
const { isLoading, enabledTasksCount, disabledTasksCount } = storeToRefs(taskStore)
// 生命週期
onMounted(async () => {
  // await getTaskStatus()
})
</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto min-h-0 pb-6`">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">首頁</h1>
      <p class="text-gray-400">歡迎使用 Movera 自動化檔案管理系統</p>
    </div>

    <!-- 載入狀態 -->
    <div
      v-if="isLoading"
      class="grid grid-cols-1 md:grid-cols-2 gap-4"
    >
      <!-- 已啟動任務 -->
      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">已啟動任務</CardTitle>
          <CheckCircle class="size-8 text-green-400" />
        </CardHeader>
        <CardContent>
          <LoaderCircle class="animate-spin" />
        </CardContent>
      </Card>

      <!-- 已停用任務 -->
      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">已停用任務</CardTitle>
          <XCircle class="size-8 text-red-500" />
        </CardHeader>
        <CardContent>
          <LoaderCircle class="animate-spin" />
        </CardContent>
      </Card>
    </div>

    <!-- 統計卡片 -->
    <div
      v-else
      class="grid grid-cols-1 md:grid-cols-2 gap-4"
    >
      <!-- 已啟動任務 -->
      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">已啟動任務</CardTitle>
          <CheckCircle class="size-8 text-green-400" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-green-400">{{ enabledTasksCount ?? 0 }}</div>
          <p class="text-xs text-gray-400">個任務已啟動</p>
        </CardContent>
      </Card>

      <!-- 已停用任務 -->
      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader class="flex flex-row items-center justify-between pb-2">
          <CardTitle class="text-sm font-medium">已停用任務</CardTitle>
          <XCircle class="size-8 text-red-500" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold text-red-500">{{ disabledTasksCount ?? 0 }}</div>
          <p class="text-xs text-gray-400">個任務已暫停</p>
        </CardContent>
      </Card>
    </div>
  </main>
</template>