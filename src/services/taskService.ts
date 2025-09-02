import type { Task, TaskCreate, TaskStats, TaskUpdate } from "@/schemas";
import { request } from "@/services/api";

export const taskService = {
  /**
   * 更新指定的任務
   * @param task 要更新的任務物件
   * @returns 更新後的任務物件
   */
  // update: async (task: Task): Promise<Task> => {
  //   const response = await apiClient.put<Task>(`/tasks/
  //     ${task.id}`, task)
  //   return response.data
  // },
  /**
     * 獲取所有任務列表。
     */
  getAll(): Promise<Task[]> {
    return request<Task[]>('GET', '/api/v1/tasks');
  },

  /**
   * 獲取指定 ID 的任務。
   * @param taskId - 要獲取的任務 ID
   * @returns - 任務物件
   */
  getById(taskId: string): Promise<Task> {
    return request<Task>('GET', `/api/v1/task/${taskId}`);
  },

  /**
   * 建立一個新任務。
   * @param taskData - 新任務的資料
   */
  create(taskData: TaskCreate): Promise<Task> {
    return request<Task>('POST', '/api/v1/task', taskData);
  },

  /**
   * 更新指定 ID 的任務。
   * @param taskId - 要更新的任務 ID
   * @param taskData - 要更新的任務資料
   */
  update(taskId: string, taskData: TaskUpdate): Promise<Task> {
    return request<Task>('PUT', `/api/v1/task/${taskId}`, taskData);
  },

  /**
   * 刪除指定 ID 的任務。
   * @param taskId - 要刪除的任務 ID
   */
  delete(taskId: string): Promise<void> {
    return request('DELETE', `/api/v1/task/${taskId}`);
  },

  /**
   * 獲取任務統計數據。
   */
  getStats(): Promise<TaskStats> {
    return request<TaskStats>('GET', '/api/v1/tasks/stats');
  },
}