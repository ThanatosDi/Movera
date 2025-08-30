import { API_ENDPOINTS } from '@/constants'

/**
 * API 基礎類別
 */
class ApiService {
  #baseURL

  constructor(baseURL = 'http://localhost:8080/api/v1') {
    this.#baseURL = baseURL
  }

  /**
   * 設置 API 基礎 URL
   */
  setBaseURL(url) {
    this.#baseURL = url
  }

  /**
   * 通用請求方法
   */
  async #request(endpoint, options = {}) {
    const url = `${this.#baseURL}${endpoint}`

    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    }

    const config = { ...defaultOptions, ...options }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // 穩健地處理可能沒有內容的回應 (例如 DELETE 的 204 回應)
      const text = await response.text()
      return text ? JSON.parse(text) : undefined
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  /**
   * GET 請求
   */
  async #get(endpoint) {
    return this.#request(endpoint, { method: 'GET' })
  }

  /**
   * POST 請求
   */
  async #post(endpoint, data) {
    return this.#request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * PUT 請求
   */
  async #put(endpoint, data) {
    return this.#request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  /**
   * DELETE 請求
   */
  async #delete(endpoint) {
    return this.#request(endpoint, { method: 'DELETE' })
  }

  // 任務相關 API
  async getTasks() {
    return this.#get(API_ENDPOINTS.TASKS)
  }

  async getTask(id) {
    return this.#get(API_ENDPOINTS.TASK_BY_ID(id))
  }

  async createTask(task) {
    return this.#post(API_ENDPOINTS.TASK, task)
  }

  async updateTask(id, task) {
    return this.#put(API_ENDPOINTS.TASK_BY_ID(id), task)
  }

  async deleteTask(id) {
    return this.#delete(API_ENDPOINTS.TASK_BY_ID(id))
  }

  async getTaskStatus() {
    return this.#get(API_ENDPOINTS.TASK_STATUS)
  }

  // 日誌相關 API
  async getLogs(taskId) {
    return this.#get(`${API_ENDPOINTS.LOG}/task/${taskId}`)
  }
}

export default new ApiService()

// export const ApiService = new ApiService()
