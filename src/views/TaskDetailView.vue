<script setup lang="ts">
import TaskDeleteDialog from '@/components/TaskDeleteDialog.vue'
import TaskEditForm from '@/components/TaskEditForm.vue'
import TaskLogsPanel from '@/components/TaskLogsPanel.vue'
import { Button } from '@/components/ui/button'
import { useNotification } from '@/composables/useNotification'
import type { Task } from '@/schemas'
import { ApiError } from '@/schemas/errors'
import { useTaskStore } from '@/stores/taskStore'
import { Play, Square } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { computed, nextTick, ref, toRaw, watch } from 'vue'
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

const isLoadingLogs = ref<boolean>(false)
const logsPanel = ref<InstanceType<typeof TaskLogsPanel> | null>(null)
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
      const foundTask = taskStore.getRefTaskById(newTaskId as string)
      task.value = foundTask ? structuredClone(toRaw(foundTask)) : null
    }
  },
  { immediate: true }
)

// 監聽 store 任務列表變化，確保 F5 重新整理後能載入任務
watch(
  () => taskStore.tasks,
  () => {
    if (taskId.value && !task.value) {
      const foundTask = taskStore.getRefTaskById(taskId.value)
      if (foundTask) {
        task.value = structuredClone(toRaw(foundTask))
      }
    }
  },
  { deep: true }
)

const handleUpdateTask = async () => {
  if (!task.value) return
  isSaving.value = true
  const { id, created_at, logs, tags, ...taskData } = task.value
  if (!taskData.tag_ids) {
    taskData.tag_ids = tags?.map((t: { id: string }) => t.id) || []
  }
  try {
    const updatedTask = await taskStore.updateTask(id, taskData)
    if (updatedTask) {
      task.value = structuredClone(toRaw(updatedTask))
    }
    useNotification.showSuccess(t('notifications.taskUpdateSuccessTitle'), t('notifications.taskUpdateSuccessDesc', { taskName: task.value?.name }))
  } catch (e: unknown) {
    console.error('Failed to update task:', e)
    const message = e instanceof ApiError || e instanceof Error ? e.message : 'Unknown error'
    useNotification.showError(t('notifications.taskUpdateErrorTitle'), message)
  } finally {
    isSaving.value = false
  }
}

const handleReloadLogs = async () => {
  const currentTaskId = route.params?.taskId as string
  if (!currentTaskId || !task.value) return
  isLoadingLogs.value = true
  try {
    const fetchedLogs = await taskStore.fetchTaskLogByTaskId(currentTaskId)
    if (fetchedLogs && task.value) {
      task.value.logs = fetchedLogs
    }
  } catch (e: unknown) {
    console.error('Failed to fetch task log:', e)
    const message = e instanceof ApiError || e instanceof Error ? e.message : 'Unknown error'
    useNotification.showError(t('notifications.taskLogFetchErrorTitle'), message)
  } finally {
    isLoadingLogs.value = false
    await nextTick()
    logsPanel.value?.scrollIntoView()
  }
}

const handleToggleTaskStatus = async () => {
  if (!task.value) return
  task.value.enabled = !task.value.enabled
  await handleUpdateTask()
}

const handleDeleteTask = async () => {
  if (!task.value) return
  const currentTaskId = task.value.id
  try {
    await taskStore.deleteTask(currentTaskId)
    router.push({ name: 'Home' })
    useNotification.showSuccess(
      t('notifications.taskDeleteSuccessTitle'),
      t('notifications.taskDeleteSuccessDesc', { taskName: task.value.name })
    )
  } catch (e: unknown) {
    console.error('Failed to delete task:', e)
    const message = e instanceof ApiError || e instanceof Error ? e.message : 'Unknown error'
    useNotification.showError(t('notifications.taskDeleteErrorTitle'), message)
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
          <Button
            v-if="!task.enabled"
            @click="handleToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-green-500 hover:bg-green-600 text-black font-bold"
          >
            <Play class="size-4 mr-2" />
            {{ t('taskDetailView.enableButton') }}
          </Button>
          <Button
            v-if="task.enabled"
            @click="handleToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
          >
            <Square class="size-4 mr-2" />
            {{ t('taskDetailView.disableButton') }}
          </Button>
          <TaskDeleteDialog
            :taskName="task.name"
            :disabled="isSaving"
            @confirm="handleDeleteTask"
          />
        </div>
      </div>

      <TaskEditForm
        v-model="task"
        :isSaving="isSaving"
        @save="handleUpdateTask"
      />

      <TaskLogsPanel
        ref="logsPanel"
        :logs="logs"
        :isLoading="isLoadingLogs"
        @reload="handleReloadLogs"
      />
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
