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
import { computed, nextTick, ref, watch, type ComponentPublicInstance } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

const { t } = useI18n()

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
      throw new Error(t('views.taskDetail.taskNotFound'))
    }
  } catch (error: any) {
    console.error('Failed to fetch task:', error)
    task.value = null // 清空舊資料
    logs.value = []
    router.push({ name: 'Home' })
    useNotification.showError(t('views.taskDetail.fetchError'), `${t('views.taskDetail.taskId')}: ${taskId}, ${t('common.error')}: ${error.message}`)
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
    useNotification.showError(t('notifications.fetchLogError'), `${t('views.taskDetail.taskId')}: ${taskId}, ${t('common.error')}: ${error.message}`)
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
    useNotification.showSuccess(t('notifications.taskDeleteSuccessTitle'), t('notifications.taskDeleteSuccessDesc', { taskName: task.value.name }))
    router.push({ name: 'Home' })
  } catch (error: any) {
    console.error('Failed to delete task:', error)
    useNotification.showError(t('notifications.taskDeleteErrorTitle'), error.message)
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
    useNotification.showSuccess(t('notifications.taskUpdateSuccessTitle'), t('notifications.taskUpdateSuccessDesc', { taskName: task.value.name }))
  } catch (e: any) {
    console.error('Failed to update task:', e)
    useNotification.showError(t('notifications.taskUpdateErrorTitle'), e.message)
  } finally {
    isSaving.value = false
  }
}
const btnActionToggleTaskStatus = async () => {
  if (!task.value) return
  task.value.enabled = !task.value.enabled
  await btnActionUpdateTask()
}

const isRenameRuleRequired = computed(() => {
  return task.value && task.value.rename_rule !== null
})
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
        <p class="text-gray-400">{{ t('views.taskDetail.taskId') }}: {{ task.id }}</p>
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
            {{ t('views.taskDetail.enableButton') }}
          </Button>
          <Button
            v-if="task.enabled"
            @click="btnActionToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
          >
            <Square class="size-4 mr-2" />
            {{ t('views.taskDetail.disableButton') }}
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
                {{ t('common.delete') }}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent class="bg-gray-800 border-gray-700 text-white">
              <AlertDialogHeader>
                <AlertDialogTitle>{{ t('views.taskDetail.deleteDialogTitle') }}</AlertDialogTitle>
                <AlertDialogDescription class="text-current">
                  {{ t('views.taskDetail.deleteDialogDesc', { taskName: task.name }) }}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel class="hover:bg-stone-400 text-black">{{ t('common.cancel') }}</AlertDialogCancel>
                <AlertDialogAction class="bg-green-400 hover:bg-green-800 text-black" @click="btnActionDeleteTask">{{ t('common.continue') }}</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader>
          <CardTitle>{{ t('views.taskDetail.cardTitle') }}</CardTitle>
          <CardDescription>{{ t('views.taskDetail.cardDescription') }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <TaskForm
            v-model="task"
            :isRenameRuleRequired="isRenameRuleRequired ?? false"
          />
          <div class="flex justify-end">
            <Button
              @click="btnActionUpdateTask"
              :disabled="isSaving"
              class="bg-blue-500 hover:bg-blue-600 font-bold text-white"
            >
              <Save class="size-4 mr-2" />
              {{ isSaving ? t('common.saving') : t('views.taskDetail.saveChanges') }}
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
            <CardTitle>{{ t('views.taskDetail.logsTitle') }}</CardTitle>
            <CardDescription>{{ t('views.taskDetail.logsDescription') }}</CardDescription>
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
            {{ isLoadingLogs ? t('common.loading') : t('views.taskDetail.reload') }}
          </Button>
        </CardHeader>
        <CardContent class="space-y-2">
          <div
            v-if="isLoadingLogs"
            class="text-center text-gray-400 py-4"
          >
            <p>{{ t('views.taskDetail.loadingLogs') }}</p>
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
            <p>{{ t('views.taskDetail.noLogs') }}</p>
          </div>
        </CardContent>
      </Card>
    </div>

    <div
      v-else
      class="flex items-center justify-center h-full"
    >
      <div class="text-center text-gray-400">
        <p class="text-lg mb-2">{{ t('views.taskDetail.taskNotFound') }}</p>
        <p class="text-sm">{{ t('views.taskDetail.checkTaskId') }}</p>
      </div>
    </div>
  </main>
</template>
