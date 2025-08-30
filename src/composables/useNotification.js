import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '@/constants'
import { toast } from 'vue-sonner'
/**
 * 通知系統 Composable
 */
export function useNotification() {
  /**
   * 顯示成功通知。
   * @param {string} message - 成功訊息的主要內容。
   * @param {string} description - 成功訊息的附加描述。
   */
  const showSuccess = (message, description) => {
    toast.success(message, { description })
  }

  /**
   * 顯示錯誤通知。
   * @param {string} message - 錯誤訊息的主要內容。
   * @param {string} description - 錯誤訊息的附加描述。
   */
  const showError = (message, description) => {
    toast.error(message, { description })
  }

  /**
   * 顯示資訊通知。
   * @param {string} message - 信息訊息的主要內容。
   * @param {string} description - 信息訊息的附加描述。
   */

  const showInfo = (message, description) => {
    toast.info(message, { description })
  }

  /**
   * 顯示警告通知。
   * @param {string} message - 警告訊息的主要內容。
   * @param {string} description - 警告訊息的附加描述。
   */
  const showWarning = (message, description) => {
    toast.warning(message, { description })
  }

  // 預定義的通知方法
  const notifyTaskCreated = () => {
    showSuccess(SUCCESS_MESSAGES.TASK_CREATED)
  }

  const notifyTaskUpdated = () => {
    showSuccess(SUCCESS_MESSAGES.TASK_UPDATED)
  }

  const notifyTaskDeleted = () => {
    showSuccess(SUCCESS_MESSAGES.TASK_DELETED)
  }

  const notifyNetworkError = (error) => {
    showError(ERROR_MESSAGES.NETWORK_ERROR, error)
  }

  const notifyValidationError = (error) => {
    showError(ERROR_MESSAGES.VALIDATION_ERROR, error)
  }

  const notifySaveError = (error) => {
    showError(ERROR_MESSAGES.SAVE_ERROR, error)
  }

  const notifyLoadError = (error) => {
    showError(ERROR_MESSAGES.LOAD_ERROR, error)
  }

  const notifyDeleteError = (error) => {
    showError(ERROR_MESSAGES.DELETE_ERROR, error)
  }

  return {
    // 基礎通知方法
    showSuccess,
    showError,
    showInfo,
    showWarning,

    // 預定義的通知方法
    notifyTaskCreated,
    notifyTaskUpdated,
    notifyTaskDeleted,
    notifyNetworkError,
    notifyValidationError,
    notifySaveError,
    notifyLoadError,
    notifyDeleteError
  }
}