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

  // 選擇模式相關狀態
  const isSelectMode = ref<boolean>(false)
  const selectedTaskIds = ref<Set<string>>(new Set())

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
      // 從選中列表中移除已刪除的任務
      const newSet = new Set(selectedTaskIds.value)
      newSet.delete(taskId)
      selectedTaskIds.value = newSet
    } catch (e) {
      throw e
    }
  }

  // 選擇模式操作
  function toggleSelectMode() {
    isSelectMode.value = !isSelectMode.value
    if (!isSelectMode.value) {
      selectedTaskIds.value = new Set()
    }
  }

  function toggleTaskSelection(taskId: string) {
    const newSet = new Set(selectedTaskIds.value)
    if (newSet.has(taskId)) {
      newSet.delete(taskId)
    } else {
      newSet.add(taskId)
    }
    selectedTaskIds.value = newSet
  }

  function selectAllTasks() {
    if (selectedTaskIds.value.size === tasks.value.length) {
      selectedTaskIds.value = new Set()
    } else {
      selectedTaskIds.value = new Set(tasks.value.map(t => t.id))
    }
  }

  function isTaskSelected(taskId: string) {
    return selectedTaskIds.value.has(taskId)
  }

  const selectedCount = computed(() => selectedTaskIds.value.size)

  // 批量操作
  async function batchDelete() {
    const idsToDelete = Array.from(selectedTaskIds.value)
    for (const id of idsToDelete) {
      await deleteTask(id)
    }
    selectedTaskIds.value = new Set()
  }

  async function batchEnable() {
    const idsToEnable = Array.from(selectedTaskIds.value)
    for (const id of idsToEnable) {
      const task = getRefTaskById(id)
      if (task && !task.enabled) {
        const { id: _, created_at, logs, ...taskData } = task
        await updateTask(id, { ...taskData, enabled: true })
      }
    }
  }

  async function batchDisable() {
    const idsToDisable = Array.from(selectedTaskIds.value)
    for (const id of idsToDisable) {
      const task = getRefTaskById(id)
      if (task && task.enabled) {
        const { id: _, created_at, logs, ...taskData } = task
        await updateTask(id, { ...taskData, enabled: false })
      }
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
    // 選擇模式
    isSelectMode,
    selectedTaskIds,
    selectedCount,
    toggleSelectMode,
    toggleTaskSelection,
    selectAllTasks,
    isTaskSelected,
    // 批量操作
    batchDelete,
    batchEnable,
    batchDisable,
  }
})