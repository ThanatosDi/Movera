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
import { ScrollArea } from '@/components/ui/scroll-area'
import { useNotification } from '@/composables/useNotification'
import type { Task } from '@/schemas'
import { useTaskStore } from '@/stores/taskStore'
import { Play, RefreshCw, Save, Square, Trash2 } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { computed, nextTick, ref, watch, type ComponentPublicInstance } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

const { t } = useI18n()
const taskStore = useTaskStore()
const router = useRouter()
const route = useRoute()



const taskId = computed(() => route.params.taskId as string)
const task = ref<Task | null>(null)

const logs = computed(() => task.value?.logs || [])
const initialLoading = computed(() => taskStore.isLoading && !task.value)
const isRenameRuleRequired = computed(() => {
  return task.value && task.value.rename_rule !== null
})

const isLoadingLogs = ref<boolean>(false)
const logCard = ref<ComponentPublicInstance | null>(null)
const { isSaving } = storeToRefs(taskStore)

const initialTaskData = async () => {
  if (taskStore.tasks.length === 0) {
    try {
      await taskStore.fetchTasks()
    } catch (e) {
      // 錯誤處理已在 taskStore.fetchTasks() 中完成
    }
  }
}

// 監聽路由變化並加載任務數據
watch(
  () => route.params.taskId,
  async (newTaskId) => {
    if (newTaskId) {
      await initialTaskData()
      // 從 store 獲取任務並創建深拷貝（允許本地編輯）
      const foundTask = taskStore.getRefTaskById(newTaskId as string)
      task.value = foundTask ? JSON.parse(JSON.stringify(foundTask)) : null
    }
  },
  { immediate: true }
)

// 監聽 store 任務列表變化，確保 F5 重新整理後能載入任務
watch(
  () => taskStore.tasks,
  () => {
    // 只有當 task 為 null 時才從 store 重新獲取（避免覆蓋用戶正在編輯的內容）
    if (taskId.value && !task.value) {
      const foundTask = taskStore.getRefTaskById(taskId.value)
      if (foundTask) {
        task.value = JSON.parse(JSON.stringify(foundTask))
      }
    }
  },
  { deep: true }
)




// onClick 事件處理函式

/**
 * 按點更新任務按鈕
 * @async
 * @description
 *   按點更新任務，將 task 的資料傳遞 taskStore.updateTask()，
 *   並顯示 Success 或 Error 的 Notification
 * @returns {Promise<void>}
 */
const btnActionUpdateTask = async () => {
  if (!task.value) return
  isSaving.value = true
  const { id, created_at, logs, ...taskData } = task.value
  try {
    const updatedTask = await taskStore.updateTask(id, taskData)
    // 保存成功後，從 store 同步最新數據
    if (updatedTask) {
      task.value = JSON.parse(JSON.stringify(updatedTask))
    }
    useNotification.showSuccess(t('notifications.taskUpdateSuccessTitle'), t('notifications.taskUpdateSuccessDesc', { taskName: task.value?.name }))
  } catch (e: any) {
    console.error('Failed to update task:', e)
    useNotification.showError(t('notifications.taskUpdateErrorTitle'), e.message)
  } finally {
    isSaving.value = false
  }
}


const btnActionReloadLogs = async () => {
  const taskId = route.params?.taskId as string
  if (!taskId || !task.value) return
  isLoadingLogs.value = true
  try {
    const logs = await taskStore.fetchTaskLogByTaskId(taskId)
    // 更新本地 task 的 logs
    if (logs && task.value) {
      task.value.logs = logs
    }
  } catch (e: any) {
    console.error('Failed to fetch task log:', e)
    useNotification.showError(t('notifications.taskLogFetchErrorTitle'), e.message)
  } finally {
    isLoadingLogs.value = false
    await nextTick()
    const element = logCard.value?.$el as HTMLElement
    element?.scrollIntoView({ behavior: 'smooth' })
  }
}

const btnActionToggleTaskStatus = async () => {
  if (!task.value) return
  task.value.enabled = !task.value.enabled
  await btnActionUpdateTask()
}

const btnActionDeleteTask = async () => {
  if (!task.value) return
  const taskId = task.value.id
  try {
    await taskStore.deleteTask(taskId)
    router.push({ name: 'Home' })
    useNotification.showSuccess(
      t('notifications.taskDeleteSuccessTitle'),
      t('notifications.taskDeleteSuccessDesc', { taskName: task.value.name })
    )
  } catch (e: any) {
    console.error('Failed to delete task:', e)
    useNotification.showError(t('notifications.taskDeleteErrorTitle'), e.message)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6 bg-background text-foreground`">
    <div
      v-if="initialLoading"
      class="flex items-center justify-center h-full"
    >
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-300 mx-auto mb-4"></div>
        <p>{{ t('common.loading') }}...</p>
      </div>
    </div>

    <div v-else-if="task">
      <div class="mb-4">
        <h1 class="text-2xl font-bold">{{ task.name }}</h1>
        <p>{{ t('taskDetailView.taskId') }}: {{ task.id }}</p>
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
            {{ t('taskDetailView.enableButton') }}
          </Button>
          <Button
            v-if="task.enabled"
            @click="btnActionToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
          >
            <Square class="size-4 mr-2" />
            {{ t('taskDetailView.disableButton') }}
          </Button>
          <!-- 刪除按鈕 -->
          <AlertDialog>
            <AlertDialogTrigger as-child>
              <Button
                :disabled="isSaving"
                variant="destructive"
                size="sm"
                class="dark:bg-red-500 dark:hover:bg-red-600 text-white font-bold"
              >
                <Trash2 class="size-4 mr-2" />
                {{ t('common.delete') }}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent class="bg-background text-foreground normal-border">
              <AlertDialogHeader>
                <AlertDialogTitle>{{ t('taskDetailView.deleteDialogTitle') }}</AlertDialogTitle>
                <AlertDialogDescription class="text-current">
                  {{ t('taskDetailView.deleteDialogDesc', { taskName: task.name }) }}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel class="bg-background text-foreground border dark:border-foreground">{{
                  t('common.cancel') }}
                </AlertDialogCancel>
                <AlertDialogAction
                  class="bg-green-400 hover:bg-green-800 text-black"
                  @click="btnActionDeleteTask"
                >{{ t('common.continue') }}</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <Card class="normal-border">
        <CardHeader>
          <CardTitle>{{ t('taskDetailView.taskCardTitle') }}</CardTitle>
          <CardDescription>{{ t('taskDetailView.taskCardDescription') }}</CardDescription>
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
              {{ isSaving ? t('common.saving') : t('taskDetailView.saveChanges') }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        ref="logCard"
        class="mt-4 normal-border"
      >
        <CardHeader class="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{{ t('taskDetailView.logsCardTitle') }}</CardTitle>
            <CardDescription>{{ t('taskDetailView.logsCardDescription') }}</CardDescription>
          </div>
          <Button
            @click="btnActionReloadLogs"
            :disabled="isLoadingLogs"
            size="sm"
            class="bg-background text-foreground border border-outline btn-hover-bg hover:text-foreground"
          >
            <RefreshCw
              class="size-4 mr-2"
              :class="{ 'animate-spin': isLoadingLogs }"
            />
            {{ isLoadingLogs ? t('common.loading') : t('common.reload') }}
          </Button>
        </CardHeader>
        <CardContent class="space-y-2">
          <div
            v-if="isLoadingLogs"
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
    </div>

    <div
      v-else
      class="flex items-center justify-center h-full"
    >
      <div class="text-center text-gray-400">
        <p class="text-lg mb-2">{{ t('taskDetailView.taskNotFound') }}</p>
        <p class="text-sm">{{ t('taskDetailView.checkTaskId') }}</p>
      </div>
    </div>
  </main>
</template>
