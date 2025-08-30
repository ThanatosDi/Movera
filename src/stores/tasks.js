import { useNotification } from "@/composables/useNotification"
import ApiService from "@/services/api"
import { Task } from "@/types"
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const { notifyLoadError } = useNotification()

export const useTasksStore = defineStore('tasks', () => {
  // 狀態
  const tasks = ref([])
  const loading = ref(false)
  const error = ref(null)

  const enabledTasksCount = computed(() => {
    return tasks.value.filter(task => task.enabled).length
  })

  const disabledTasksCount = computed(() => {
    return tasks.value.filter(task => !task.enabled).length
  })
  // 動作

  /**
   * 設定 loading 狀態
   * @param {boolean} isLoading - loading state
   */
  const setLoading = (isLoading) => {
    loading.value = isLoading
  }

  /**
   * 設定錯誤訊息
   * @param {String} errorMessage - 錯誤訊息
   */
  const setError = (errorMessage) => {
    error.value = errorMessage
  }

  /**
   * 從 API 獲取任務列表
   *  - 設定 loading 狀態為 true
   *  - 清除錯誤訊息
   *  - 使用 ApiService.getTasks() 獲取任務列表
   *  - 將獲取的任務列表設為 tasks.value
   *  - 如果獲取失敗，設 error.value 為錯誤訊息
   *  - 最後，將 loading 狀態設為 false
   */
  const fetchTasks = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await ApiService.getTasks()
      tasks.value = data.map(item => new Task(item))
    } catch (err) {
      setError(err instanceof Error ? err.message : '獲取任務列表失敗')
      console.error('Failed to fetch tasks:', err)
      notifyLoadError('獲取任務列表失敗')
    } finally {
      setLoading(false)
    }
  }

  

  /**
   * 根據任務 ID 獲取特定的任務
   * @param {String} id - 任務的唯一識別碼
   * @returns {Task|undefined} - 找到的任務物件，如果沒有找到則返回 undefined
   */
  const getTaskById = (id) => {
    const taskData = tasks.value.find(task => task.id === id)
    console.log(taskData)
    return taskData ? new Task(taskData) : undefined
  }

  /**
   * 根據任務 ID 獲取日誌
   * @param {String} taskId - 任務的唯一識別碼
   * @returns {Promise<Array<Object>>} - 日誌列表
   */
  const fetchLogs = async (taskId) => {
    try {
      return await ApiService.getLogs(taskId)
    } catch (err) {
      console.error('Failed to fetch logs:', err)
      return []
    }
  }

  /**
   * 創建一個新的任務
   *  - 設定 loading 狀態為 true
   *  - 清除錯誤訊息
   *  - 使用 ApiService.createTask() 創建一個新的任務
   *  - 將創建的任務加入 tasks.value
   *  - 如果創建失敗，設 error.value 為錯誤訊息
   *  - 最後，將 loading 狀態設為 false
   *
   * @param {Object} taskData - 任務的資料，包含 name, include, move_to, src_filename_regex, dst_filename_regex 等欄位
   * @returns {Task} - 創建的任務物件的 Promise
   */
  const createTask = async (taskData) => {
    setLoading(true)
    setError(null)

    try {
      const newTaskData = await ApiService.createTask(taskData)
      const newTask = new Task(newTaskData)
      tasks.value.push(newTask)
      return newTask
    } catch (err) {
      setError(err instanceof Error ? err.message : '創建任務失敗')
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * 更新一個已經存在的任務
   *  - 設定 loading 狀態為 true
   *  - 清除錯誤訊息
   *  - 使用 ApiService.updateTask() 更新一個已經存在的任務
   *  - 將更新的任務加入 tasks.value
   *  - 如果更新失敗，設 error.value 為錯誤訊息
   *  - 最後，將 loading 狀態設為 false
   *
   * @param {String} id - 任務的唯一識別碼
   * @param {Object} taskData - 任務的資料，包含 name, include, move_to, src_filename_regex, dst_filename_regex 等欄位
   * @returns {Promise<Object>} - 更新的任務物件的 Promise
   */
  const updateTask = async (id, taskData) => {
    setLoading(true)
    setError(null)

    try {
      const updatedTaskData = await ApiService.updateTask(id, taskData)
      // const updatedTask = new Task(updatedTaskData)
      const index = tasks.value.findIndex(task => task.id === id)
      console.log(index)
      if (index !== -1) {
        tasks.value[index] = taskData
      }
      return taskData
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新任務失敗')
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * 刪除一個已經存在的任務
   *  - 設定 loading 狀態為 true
   *  - 清除錯誤訊息
   *  - 使用 ApiService.deleteTask() 刪除一個已經存在的任務
   *  - 將已經刪除的任務從 tasks.value 中移除
   *  - 如果刪除失敗，設 error.value 為錯誤訊息
   *  - 最後，將 loading 狀態設為 false
   *
   * @param {String} id - 任務的唯一識別碼
   * @returns {Promise<void>} - 刪除任務的 Promise
   */
  const deleteTask = async (id) => {
    setLoading(true)
    setError(null)

    try {
      await ApiService.deleteTask(id)
      tasks.value = tasks.value.filter(task => task.id !== id)
    } catch (err) {
      setError(err instanceof Error ? err.message : '刪除任務失敗')
      throw err
    } finally {
      setLoading(false)
    }
  }

  /**
   * 初始化 tasks store
   *  - 同時 fetchTasks() 和 fetchTags() 並行執行
   *  - 等待所有 Promise 都 resolve 才會 resolve
   * @returns {Promise<void>} - 初始化的 Promise
   */
  const initialize = async () => {
    await Promise.all([fetchTasks()])
  }

  return {
    // 狀態
    tasks,
    loading,
    error,

    // 計算屬性
    enabledTasksCount,
    disabledTasksCount,

    // 動作
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    getTaskById,
    initialize,
    fetchLogs,
  }
})
