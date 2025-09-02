<script setup lang="ts">
import LogItem from '@/components/LogItem.vue'
import TaskForm from '@/components/TaskForm.vue'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from "@/components/ui/scroll-area"
import { useNotification } from '@/composables/useNotification'
import type { Log, Task } from '@/schemas'
import { logService } from '@/services/logService'
import { useTaskStore } from '@/stores/taskStore'
import { Play, RefreshCw, Save, Square, Trash2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { nextTick, ref, watch, type ComponentPublicInstance } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Composables
const route = useRoute()
const router = useRouter()

// Store
const taskStore = useTaskStore()
const { isLoading } = storeToRefs(taskStore)

// Local State
const task = ref<Task | null>(null)
const logs = ref<Log[]>([])
const isSaving = ref<boolean>(false)
const isLoadingLogs = ref<boolean>(false)
const logCard = ref<ComponentPublicInstance | null>(null)

// 數據獲取方法
const fetchTaskData = async (taskId: string) => {
  if (!taskId) return
  try {
    // 確保 store 中有最新的 tasks 列表
    if (taskStore.tasks.length === 0) {
      await taskStore.fetchTasks()
    }
    const foundTask = await taskStore.getRefTaskById(taskId)
    if (foundTask) {
      // 建立一個 task 物件的深層複製副本，避免直接修改 Pinia store 中的狀態
      task.value = JSON.parse(JSON.stringify(foundTask))
      logs.value = await logService.getByTaskId(taskId)
    } else {
      throw new Error('找不到指定的任務')
    }
  } catch (error: any) {
    console.error('Failed to fetch task:', error)
    task.value = null // 清空舊資料
    logs.value = []
    router.push({ name: 'Home' })
    useNotification.showError('取得任務資料發生錯誤', `任務 ID: ${taskId}, 錯誤: ${error.message}`)
  }
}

// 監聽路由參數的變化
watch(
  () => route.params.taskId,
  (newTaskId) => {
    if (newTaskId) {
      fetchTaskData(newTaskId as string)
    }
  },
  { immediate: true }
)

// 方法
const btnActionFetchLogs = async () => {
  const taskId = route.params.taskId
  if (!taskId) return
  isLoadingLogs.value = true
  logs.value = []
  try {
    logs.value = await logService.getByTaskId(taskId as string)
  } catch (error: any) {
    console.error('Failed to fetch logs:', error)
    useNotification.showError('取得日誌資料發生錯誤', `任務 ID: ${taskId}, 錯誤: ${error.message}`)
  } finally {
    isLoadingLogs.value = false
    await nextTick()
    const element = logCard.value?.$el as HTMLElement
    element?.scrollIntoView({ behavior: 'smooth' })
  }
}
const btnActionDeleteTask = async () => {
  if (!task.value?.id) return
  isSaving.value = true
  try {
    await taskStore.deleteTask(task.value.id)
    useNotification.showSuccess('任務已刪除', `任務 "${task.value.name}" 已成功刪除。`)
    router.push({ name: 'Home' })
  } catch (error: any) {
    console.error('Failed to delete task:', error)
    useNotification.showError('刪除任務失敗', error.message)
  } finally {
    isSaving.value = false
  }
}
const btnActionUpdateTask = async () => {
  if (!task.value) return
  isSaving.value = true
  const { id, created_at, ...taskData } = task.value
  try {
    await taskStore.updateTask(id, taskData)
    useNotification.showSuccess('任務已更新', `任務 "${task.value.name}" 已成功更新。`)
  } catch (e: any) {
    console.error('Failed to update task:', e)
    useNotification.showError('更新任務失敗', e.message)
  } finally {
    isSaving.value = false
  }
}
const btnActionToggleTaskStatus = async () => {
  if (!task.value) return
  task.value.enabled = !task.value.enabled
  await btnActionUpdateTask()
}
</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6`">
    <div
      v-if="isLoading"
      class="flex items-center justify-center h-full"
    >
      <!-- <p>{{ UI_CONSTANTS.LOADING_TEXT }}</p> -->
    </div>

    <div v-else-if="task">
      <div class="mb-4">
        <h1 class="text-2xl font-bold">{{ task.name }}</h1>
        <p class="text-gray-400">任務ID: {{ task.id }}</p>
      </div>

      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center space-x-2">
          <!-- 啟用/停用按鈕 -->
          <Button
            v-if="!task.enabled"
            @click="btnActionToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-green-500 hover:bg-green-600 text-black font-bold"
          >
            <Play class="size-4 mr-2" />
            啟用任務
          </Button>
          <Button
            v-if="task.enabled"
            @click="btnActionToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
          >
            <Square class="size-4 mr-2" />
            停止任務
          </Button>
          <!-- 刪除按鈕 -->
          <AlertDialog>
            <AlertDialogTrigger as-child>
              <Button
                :disabled="isSaving"
                variant="destructive"
                size="sm"
                class="bg-red-500 hover:bg-red-600 text-white font-bold"
              >
                <Trash2 class="size-4 mr-2" />
                刪除任務
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent class="bg-gray-800 border-gray-700 text-white">
              <AlertDialogHeader>
                <AlertDialogTitle>您確定要刪除此任務嗎？</AlertDialogTitle>
                <AlertDialogDescription class="text-current">
                  此操作無法復原。這將永久刪除任務
                  <span class="font-bold text-white">"{{ task.name }}"</span>
                  並從資料庫中移除其相關資料。
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel class="text-black">取消</AlertDialogCancel>
                <AlertDialogAction @click="btnActionDeleteTask">繼續</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader>
          <CardTitle>任務設定</CardTitle>
          <CardDescription>在這裡編輯任務的詳細設定。</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <TaskForm v-model="task" />
          <div class="flex justify-end">
            <Button
              @click="btnActionUpdateTask"
              :disabled="isSaving"
              class="bg-blue-500 hover:bg-blue-600 font-bold text-white"
            >
              <Save class="size-4 mr-2" />
              {{ isSaving ? '儲存中...' : '儲存變更' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        ref="logCard"
        class="mt-4 bg-gray-800 border-gray-700 text-white"
      >
        <CardHeader class="flex flex-row items-center justify-between">
          <div>
            <CardTitle>日誌紀錄</CardTitle>
            <CardDescription>最近的任務執行紀錄。</CardDescription>
          </div>
          <Button
            @click="btnActionFetchLogs"
            :disabled="isLoadingLogs"
            size="sm"
            variant="outline"
            class="bg-gray-700 hover:bg-gray-600"
          >
            <RefreshCw
              class="size-4 mr-2"
              :class="{ 'animate-spin': isLoadingLogs }"
            />
            {{ isLoadingLogs ? '載入中...' : '重新載入' }}
          </Button>
        </CardHeader>
        <CardContent class="space-y-2">
          <div
            v-if="isLoadingLogs"
            class="text-center text-gray-400 py-4"
          >
            <p>載入日誌中...</p>
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
            <p>沒有可用的資料</p>
          </div>
        </CardContent>
      </Card>
    </div>

    <div
      v-else
      class="flex items-center justify-center h-full"
    >
      <div class="text-center text-gray-400">
        <p class="text-lg mb-2">任務不存在</p>
        <p class="text-sm">請檢查任務 ID 是否正確</p>
      </div>
    </div>
  </main>
</template>
