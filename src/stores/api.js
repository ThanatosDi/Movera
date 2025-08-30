import ApiService from '@/services/api'
import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * API 配置 Store
 */
export const useApiStore = defineStore('api', () => {
  // 狀態
  const apiUrl = ref('http://localhost:8080/api/v1')

  // 動作
  const setApiUrl = (url) => {
    apiUrl.value = url
    ApiService.setBaseURL(url)
  }

  // 初始化
  const initialize = () => {
    ApiService.setBaseURL(apiUrl.value)
  }


  return {
    // 狀態
    apiUrl,
    // 動作
    setApiUrl,
    initialize,
  }
})
