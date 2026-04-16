import { request } from '@/composables/useHttpService'
import type {
  Log,
  Task,
  TaskBatchResult,
  TaskBatchUpdateItem,
  TaskCreate,
  TaskUpdate,
} from '@/schemas'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'


export const useTaskStore = defineStore('taskStore', () => {
  const tasks = ref<Task[]>([])
  const isLoading = ref<boolean>(false)
  const isSaving = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Tag 篩選相關狀態
  const selectedFilterTagIds = ref<Set<string>>(new Set())

  // 選擇模式相關狀態
  const isSelectMode = ref<boolean>(false)
  const selectedTaskIds = ref<Set<string>>(new Set())

  /** Tasks filtered by selected tags (union logic). Returns all tasks when no tags selected. */
  const filteredTasks = computed(() => {
    if (selectedFilterTagIds.value.size === 0) {
      return tasks.value
    }
    return tasks.value.filter(task =>
      task.tags.some(tag => selectedFilterTagIds.value.has(tag.id))
    )
  })

  /** Toggle a tag's filter selection state. */
  function toggleFilterTag(tagId: string) {
    const newSet = new Set(selectedFilterTagIds.value)
    if (newSet.has(tagId)) {
      newSet.delete(tagId)
    } else {
      newSet.add(tagId)
    }
    selectedFilterTagIds.value = newSet
  }

  /** Clear all tag filter selections. */
  function clearFilterTags() {
    selectedFilterTagIds.value = new Set()
  }

  /** Number of currently enabled tasks. */
  const enabledTaskCount = computed(() => {
    return tasks.value.filter(task => task.enabled).length;
  });

  /** Number of currently disabled tasks. */
  const disabledTaskCount = computed(() => {
    return tasks.value.filter(task => !task.enabled).length;
  });

  /**
   * Return a reactive reference to a task by its ID.
   * @param taskId - The unique task identifier.
   * @returns The task object or null if not found.
   */
  const getRefTaskById = (taskId: string) => {
    const task = tasks.value.find(task => task.id === taskId)
    return task ? task : null
  }

  /** Fetch all tasks from the API and replace the local list. */
  async function fetchTasks() {
    isLoading.value = true
    error.value = null
    try {
      const response = await request<Task[]>('GET', '/api/v1/tasks')
      tasks.value = response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Create a new task via the API and append it to the local list.
   * @param taskData - The data for the new task.
   * @returns The created task.
   */
  async function createTask(taskData: TaskCreate) {
    error.value = null
    try {
      const response = await request<Task>('POST', '/api/v1/tasks', taskData)
      tasks.value.push(response)
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  /**
   * Update an existing task by ID.
   * @param taskId - The unique task identifier.
   * @param taskData - The updated task fields.
   * @returns The updated task.
   */
  async function updateTask(taskId: string, taskData: TaskUpdate) {
    isSaving.value = true
    error.value = null
    try {
      const taskIndex = tasks.value.findIndex(task => task.id === taskId)
      if (taskIndex === -1) {
        throw new Error('task not found')
      }
      const response = await request<Task>('PUT', `/api/v1/tasks/${taskId}`, taskData)
      tasks.value[taskIndex] = response
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isSaving.value = false
    }
  }

  /**
   * Fetch logs for a specific task and update the local task object.
   * @param taskId - The unique task identifier.
   * @returns The fetched log entries.
   */
  async function fetchTaskLogByTaskId(taskId: string) {
    error.value = null
    try {
      const response = await request<Log[]>('GET', `/api/v1/tasks/${taskId}/logs`)
      const task = tasks.value.find(task => task.id === taskId)
      if (task) {
        task.logs = response
      }
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  /**
   * Delete a task by ID and remove it from the local list.
   * @param taskId - The unique task identifier.
   */
  async function deleteTask(taskId: string) {
    if (!taskId) {
      return
    }
    error.value = null
    try {
      await request('DELETE', `/api/v1/tasks/${taskId}`)
      const index = tasks.value.findIndex(task => task.id === taskId)
      if (index !== -1) {
        tasks.value.splice(index, 1)
      }
      // 從選中列表中移除已刪除的任務
      const newSet = new Set(selectedTaskIds.value)
      newSet.delete(taskId)
      selectedTaskIds.value = newSet
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  /** Toggle selection mode on/off. Clears selection when exiting. */
  function toggleSelectMode() {
    isSelectMode.value = !isSelectMode.value
    if (!isSelectMode.value) {
      selectedTaskIds.value = new Set()
    }
  }

  /**
   * Toggle whether a specific task is selected.
   * @param taskId - The unique task identifier.
   */
  function toggleTaskSelection(taskId: string) {
    const newSet = new Set(selectedTaskIds.value)
    if (newSet.has(taskId)) {
      newSet.delete(taskId)
    } else {
      newSet.add(taskId)
    }
    selectedTaskIds.value = newSet
  }

  /** Select all filtered tasks, or deselect all if every filtered task is already selected. */
  function selectAllTasks() {
    const target = filteredTasks.value
    if (selectedTaskIds.value.size === target.length) {
      selectedTaskIds.value = new Set()
    } else {
      selectedTaskIds.value = new Set(target.map(t => t.id))
    }
  }

  /**
   * Check if a task is currently selected.
   * @param taskId - The unique task identifier.
   */
  function isTaskSelected(taskId: string) {
    return selectedTaskIds.value.has(taskId)
  }

  /** Number of currently selected tasks. */
  const selectedCount = computed(() => selectedTaskIds.value.size)

  /**
   * Merge a batch result's items back into the local tasks list by id.
   * @param items - Tasks returned by the batch API to replace local counterparts.
   */
  function mergeBatchItems(items: Task[]) {
    for (const item of items) {
      const idx = tasks.value.findIndex(t => t.id === item.id)
      if (idx !== -1) {
        tasks.value[idx] = item
      }
    }
  }

  /**
   * Delete all currently selected tasks in a single batch API call.
   * Local state is only mutated after the request succeeds.
   */
  async function batchDelete() {
    const idsToDelete = Array.from(selectedTaskIds.value)
    if (idsToDelete.length === 0) {
      return
    }
    error.value = null
    try {
      const response = await request<TaskBatchResult>(
        'DELETE',
        '/api/v1/tasks/batch',
        { ids: idsToDelete }
      )
      const deletedSet = new Set(response.deleted_ids)
      tasks.value = tasks.value.filter(t => !deletedSet.has(t.id))
      selectedTaskIds.value = new Set()
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  /**
   * Set enabled state for all selected tasks in a single batch API call.
   * @param enabled - Whether to enable or disable the tasks.
   */
  async function batchSetEnabled(enabled: boolean) {
    const ids = Array.from(selectedTaskIds.value)
    if (ids.length === 0) {
      return
    }
    const items: TaskBatchUpdateItem[] = ids.map(id => ({
      id,
      patch: { enabled },
    }))
    error.value = null
    try {
      const response = await request<TaskBatchResult>(
        'PUT',
        '/api/v1/tasks/batch',
        { items }
      )
      mergeBatchItems(response.items)
      selectedTaskIds.value = new Set()
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  /** Enable all currently selected tasks. */
  async function batchEnable() {
    await batchSetEnabled(true)
  }

  /** Disable all currently selected tasks. */
  async function batchDisable() {
    await batchSetEnabled(false)
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
    // Tag 篩選
    selectedFilterTagIds,
    filteredTasks,
    toggleFilterTag,
    clearFilterTags,
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
