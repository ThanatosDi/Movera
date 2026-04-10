import { useI18n } from 'vue-i18n'

/**
 * API 錯誤介面
 */
export interface ApiError {
  message: string
}

/**
 * 錯誤處理 Composable
 * 提供統一的 API 錯誤訊息轉換
 */
export function useException() {
  const { t, te } = useI18n()

  /**
   * 將 API 錯誤轉換為本地化的錯誤訊息
   *
   * @param error - 錯誤物件（Error 或 ApiError）
   * @param params - 傳遞給 i18n 的參數（如 taskName）
   * @returns 本地化的錯誤訊息
   */
  function getErrorMessage(error: Error | ApiError, params?: Record<string, unknown>): string {
    const message = error.message || 'Unknown error'

    // 嘗試用錯誤訊息作為 i18n key
    if (te(message)) {
      return t(message, params || {})
    }

    return message
  }

  /**
   * 捕獲並處理錯誤
   *
   * @param error - 錯誤物件
   * @param params - 傳遞給 i18n 的參數
   * @returns 本地化的錯誤訊息
   */
  function catchError(error: Error | ApiError, params?: Record<string, unknown>): string {
    return getErrorMessage(error, params)
  }

  return {
    catchError,
    getErrorMessage,
  }
}
