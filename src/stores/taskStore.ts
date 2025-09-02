import { useNotification } from '@/composables/useNotification';
import type { Task, TaskCreate, TaskUpdate } from '@/schemas';
import { taskService } from '@/services/taskService';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

// 使用 defineStore 定義一個 store
// 第一個參數是 store 的唯一 ID，Pinia 會用它來連接開發者工具
export const useTaskStore = defineStore('taskStore', () => {
  // --- State ---
  // 使用 ref() 來定義 state 屬性，等同於 state 選項
  const tasks = ref<Task[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // --- Getters ---
  // 使用 computed() 來定義 getters，等同於 getters 選項
  // 計算已啟用的任務數量
  const enabledTasksCount = computed(() => {
    return tasks.value.filter(task => task.enabled).length;
  });

  // 計算未啟用的任務數量
  const disabledTasksCount = computed(() => {
    return tasks.value.filter(task => !task.enabled).length;
  });

  /**
   * 根據 ID 查找並回傳單一任務。
   * 這是一個 getter 方法，由於它需要傳入參數，所以它是一個函式而不是一個 computed 屬性。
   * @param taskId - 要尋找的任務 ID
   * @returns - 找到的任務物件，如果找不到則為 null
   */
  const getRefTaskById = (taskId: string): Task | null => {
    const task = tasks.value.find(task => task.id === taskId)
    return task ? task : null
  };

  // --- Actions ---
  // 可以在這裡定義 function，等同於 actions 選項


  /**
   * 從 API 獲取所有任務，並將其存到 state 中。
   * 如果獲取失敗，則顯示錯誤訊息。
   */
  async function fetchTasks() {
    isLoading.value = true;
    error.value = null;
    try {
      // 呼叫我們在 api.ts 中定義的 service
      const data = await taskService.getAll();
      tasks.value = data;
    } catch (e: any) {
      useNotification.showError('獲取任務列表失敗')
      error.value = e.message || '獲取任務列表失敗';
      console.error('Failed to fetch tasks:', e);
      throw e
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchTaskById(taskId: string) {
    isLoading.value = true;
    error.value = null;
    try {
      // 呼叫我們在 api.ts 中定義的 service
      const data = await taskService.getById(taskId);
      return data
    } catch (e: any) {
      useNotification.showError('獲取任務失敗')
      error.value = e.message || '獲取任務失敗';
      console.error('Failed to fetch task:', e);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * 使用 taskService 來建立一個新任務。
   * 如果建立成功，則將新任務物件加入 tasks 陣列中。
   * @param taskData - 要建立的任務資料
   * @returns - 剛才建立的任務物件
   */
  async function createTask(taskData: TaskCreate ) {
    try {
      const newTask = await taskService.create(taskData);
      tasks.value.push(newTask);
      return newTask
    } catch (e: any) {
      console.error('Failed to create task in store:', e.message)
      throw e
    }
  }

  /**
   * 使用 taskService 來更新指定 ID 的任務。
   * 如果更新成功，則將更新的任務物件更新到 tasks 陣列中。
   * @param taskId - 要更新的任務 ID
   * @param taskData - 要更新的任務資料
   * @returns - 更新後的任務物件
   */
  async function updateTask(taskId: string, taskData: TaskUpdate) {
    try {
      const updatedTask = await taskService.update(taskId, taskData);
      const index = tasks.value.findIndex(task => task.id === updatedTask.id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (e: any) {
      console.error('Failed to update task in store:', e.message)
      throw e
    }
  }

  /**
   * 使用 taskService 來刪除指定 ID 的任務。
   * 如果刪除成功，則將刪除的任務物件從 tasks 陣列中刪除。
   * @param taskId - 要刪除的任務 ID
   * @throws {Error} - 如果刪除失敗，則拋出一個 Error
   */
  async function deleteTask(taskId: string) {
    try {
      await taskService.delete(taskId)
      const index = tasks.value.findIndex(task => task.id === taskId)
      if (index !== -1) {
        tasks.value.splice(index, 1)
      }
    } catch (e: any) {
      console.error('Failed to delete task in store:', e.message)
      throw e
    }
  }

  // --- Return ---
  // 需要明確地將 state, getters, 和 actions 回傳，
  // 這樣它們才能在外部被使用
  return {
    // State
    tasks,
    isLoading,
    error,
    // Getters
    enabledTasksCount,
    disabledTasksCount,
    // Actions
    fetchTasks,
    fetchTaskById,
    getRefTaskById,
    createTask,
    updateTask,
    deleteTask,
  };
});
