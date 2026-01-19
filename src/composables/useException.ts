import { useI18n } from 'vue-i18n'
import type { WebSocketError } from '../schemas/wsMessage'

/**
 * WebSocket 錯誤類型對應的 i18n key
 */
const ERROR_I18N_KEYS: Record<string, string> = {
  TaskAlreadyExists: 'exceptions.TaskAlreadyExists',
  TaskNotFound: 'errors.taskNotFound',
  UnHandledWebSocketEvent: 'errors.unhandledEvent',
  PayloadValidationError: 'errors.invalidPayload',
}

/**
 * 錯誤處理 Composable
 * 提供統一的 WebSocket 錯誤訊息轉換
 */
export function useException() {
  const { t, te } = useI18n()

  /**
   * 將 WebSocket 錯誤轉換為本地化的錯誤訊息
   *
   * @param error - WebSocket 錯誤物件
   * @param params - 傳遞給 i18n 的參數（如 taskName）
   * @returns 本地化的錯誤訊息
   */
  function getErrorMessage(error: WebSocketError, params?: Record<string, unknown>): string {
    const i18nKey = ERROR_I18N_KEYS[error.error]

    // 如果有對應的 i18n key 且該 key 存在
    if (i18nKey && te(i18nKey)) {
      return t(i18nKey, params || {})
    }

    // 回傳原始錯誤訊息
    return error.message || error.error || 'Unknown error'
  }

  /**
   * 捕獲並處理 WebSocket 錯誤
   *
   * @param error - WebSocket 錯誤物件
   * @param params - 傳遞給 i18n 的參數
   * @returns 本地化的錯誤訊息
   */
  function catchError(error: WebSocketError, params?: Record<string, unknown>): string {
    return getErrorMessage(error, params)
  }

  return {
    catchError,
    getErrorMessage,
  }
}
