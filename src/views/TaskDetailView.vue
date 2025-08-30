<script setup lang="js">
import LogItem from '@/components/LogItem.vue'
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from "@/components/ui/scroll-area"
import { useNotification } from '@/composables/useNotification'
import { UI_CONSTANTS } from '@/constants'
import ApiService from "@/services/api"
import { useTasksStore } from '@/stores/tasks'
import { Play, RefreshCw, Save, Square, Trash2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// Composables
const route = useRoute()
const router = useRouter()
const { notifyTaskUpdated, notifyLoadError, notifySaveError, notifyTaskDeleted } = useNotification()

// Store
const tasksStore = useTasksStore()
const { loading } = storeToRefs(tasksStore)

// Local State
const task = ref(null)
const logs = ref([])
const isSaving = ref(false)
const isLoadingLogs = ref(false)

// Computed Properties
const isLoading = computed(() => loading.value || !task.value)

// Methods
const fetchTask = async (taskId) => {
  if (!taskId) return
  try {
    const apiTask = await ApiService.getTask(taskId)
    task.value = apiTask
  } catch (err) {
    console.error('Failed to fetch task:', err)
    notifyLoadError(err instanceof Error ? err.message : '載入任務失敗')
  }
}

const fetchLogs = async (taskId) => {
  if (!taskId) return
  try {
    isLoadingLogs.value = true
    const apiLogs = await ApiService.getLogs(taskId)
    logs.value = apiLogs
  } catch (err) {
    console.error('Failed to fetch logs:', err)
  } finally {
    isLoadingLogs.value = false
  }
}

const updateTask = async () => {
  if (!task.value?.id) return
  isSaving.value = true
  try {
    await tasksStore.updateTask(task.value.id, task.value)
    notifyTaskUpdated()
  } catch (err) {
    console.error('Failed to update task:', err)
    notifySaveError(err instanceof Error ? err.message : '儲存任務失敗')
  } finally {
    isSaving.value = false
  }
}

const toggleTaskStatus = async () => {
  if (!task.value) return
  task.value.enabled = !task.value.enabled
  console.log(task.value)
  await updateTask()
}

const deleteTask = async () => {
  if (!task.value?.id) return
  const confirmed = window.confirm(`您確定要刪除任務 "${task.value.name}" 嗎？此操作無法復原。`)
  if (!confirmed) return
  isSaving.value = true
  try {
    await tasksStore.deleteTask(task.value.id)
    notifyTaskDeleted()
    router.push({ name: 'Home' })
  } catch (error) {
    console.error('Failed to delete task:', error)
    notifySaveError(error instanceof Error ? error.message : '刪除任務失敗')
  } finally {
    isSaving.value = false
  }
}

// Lifecycle & Watchers
onMounted(async () => {
  const taskId = route.params.taskId
  if (taskId) {
    await Promise.all([fetchTask(taskId), fetchLogs(taskId)])
  }
})

watch(() => route.params.taskId, async (newTaskId) => {
  if (newTaskId && typeof newTaskId === 'string') {
    await Promise.all([fetchTask(newTaskId), fetchLogs(newTaskId)])
  }
})
</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6 ${UI_CONSTANTS.SCROLL_BAR_CLASS}`">
    <div
      v-if="isLoading"
      class="flex items-center justify-center h-full"
    >
      <p>{{ UI_CONSTANTS.LOADING_TEXT }}</p>
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
            @click="toggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-green-500 hover:bg-green-600 text-black font-bold"
          >
            <Play class="size-4 mr-2" />
            啟用任務
          </Button>
          <Button
            v-if="task.enabled"
            @click="toggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
          >
            <Square class="size-4 mr-2" />
            停止任務
          </Button>
          <!-- 刪除按鈕 -->
          <Button
            @click="deleteTask"
            :disabled="isSaving"
            variant="destructive"
            size="sm"
            class="bg-red-500 hover:bg-red-600 text-white font-bold"
          >
            <Trash2 class="size-4 mr-2" />
            刪除任務
          </Button>
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
              @click="updateTask"
              :disabled="isSaving"
              class="bg-blue-500 hover:bg-blue-600 font-bold text-white"
            >
              <Save class="size-4 mr-2" />
              {{ isSaving ? '儲存中...' : '儲存變更' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card class="mt-4 bg-gray-800 border-gray-700 text-white">
        <CardHeader class="flex flex-row items-center justify-between">
          <div>
            <CardTitle>日誌紀錄</CardTitle>
            <CardDescription>最近的任務執行紀錄。</CardDescription>
          </div>
          <Button
            @click="fetchLogs(task.id)"
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