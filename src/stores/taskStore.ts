import { useWebSocketService } from '@/composables/useWebSocketService'
import { wsEventsEnum } from '@/enums/wsEventsEnum'
import type { Log, Task, TaskCreate, TaskUpdate } from '@/schemas'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'


export const useTaskStore = defineStore('taskStore', () => {
  const wsService = useWebSocketService()
  const tasks = ref<Task[]>([])
  const isLoading = ref<boolean>(false)
  const isSaving = ref<boolean>(false)
  const error = ref<string | null>(null)

  const enabledTaskCount = computed(() => {
    return tasks.value.filter(task => task.enabled).length;
  });

  const disabledTaskCount = computed(() => {
    return tasks.value.filter(task => !task.enabled).length;
  });

  const getRefTaskById = (taskId: string) => {
    const task = tasks.value.find(task => task.id === taskId)
    return task ? task : null
  }

  async function fetchTasks() {
    isLoading.value = true
    error.value = null
    try {
      const response = await wsService.request<Task[]>(wsEventsEnum.getTasks)
      tasks.value = response
    } catch (e) {
      error.value = (e as Error).message
      throw e // 重新拋出異常，讓調用者能正確處理
    } finally {
      isLoading.value = false
    }
  }

  async function createTask(taskData: TaskCreate) {
    try {
      const response = await wsService.request<Task>(wsEventsEnum.createTask, taskData)
      tasks.value.push(response)
      return response
    } catch (e) {
      throw e
    }
  }

  async function updateTask(taskId: string, taskData: TaskUpdate) {
    isSaving.value = true
    error.value = null
    try {
      const taskIndex = tasks.value.findIndex(task => task.id === taskId)
      if (taskIndex === -1) {
        throw new Error('task not found')
      }
      const response = await wsService.request<Task>(wsEventsEnum.updateTask, { id: taskId, ...taskData })
      tasks.value[taskIndex] = response
      return response
    } catch (e) {
      throw e
    } finally {
      isSaving.value = false
    }
  }

  async function fetchTaskLogByTaskId(taskId: string) {
    try {
      const response = await wsService.request<Log[]>(wsEventsEnum.getLogs, { id: taskId })
      const task = tasks.value.find(task => task.id === taskId)
      if (task) {
        task.logs = response
      }
      return response
    } catch (e) {
      throw e
    }
  }

  async function deleteTask(taskId: string) {
    if (!taskId) {
      return
    }
    try {
      await wsService.request(wsEventsEnum.deleteTask, { id: taskId })
      const index = tasks.value.findIndex(task => task.id === taskId)
      if (index !== -1) {
        tasks.value.splice(index, 1)
      }
    } catch (e) {
      throw e
    }
  }

  return {
    tasks,
    isLoading,
    isSaving,
    error,
    enabledTaskCount,
    disabledTaskCount,
    getRefTaskById,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    fetchTaskLogByTaskId,
  }
})