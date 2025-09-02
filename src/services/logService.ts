import type { Log } from "@/schemas";
import { request } from "./api";

/**
 * 任務 (Tasks) 相關 API
 */
export const logService = {
  /**
   * 獲取特定任務的所有日誌。
   * @param taskId - 任務 ID
   */
  getByTaskId(taskId: string): Promise<Log[]> {
    return request<Log[]>('GET', `/api/v1/log/${taskId}`);
  },
};