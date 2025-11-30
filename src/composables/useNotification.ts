import type { NotificationOptions, ToastType } from '@/schemas'
import { h } from 'vue'
import { toast } from 'vue-sonner'

/**
 * 內部輔助函式，用於顯示通知
 * @param type - 通知類型
 * @param message - 訊息標題
 * @param description - 訊息內容
 * @param options - 其他選項
 */
function showToast(type: ToastType, message: string, description?: string, options?: NotificationOptions) {
  // 建立一個乾淨的 toastOptions 物件
  const toastOptions: Record<string, any> = {
    description: options?.html && description ? h('div', { innerHTML: description }) : description,
    // 直接使用每則 toast 的 position 覆蓋顯示位置
    position: options?.position,
    duration: options?.duration || 3000,
  }

  // 根據類型呼叫對應的 toast 函式
  toast[type](message, toastOptions)
}

/**
 * 通知系統 Composable
 */
export const useNotification = {
  /**
   * 顯示一個成功的訊息
   * @param message - 訊息的標題
   * @param description - 訊息的內容
   * @param options - 其他選項，例如 { html: true, position: 'top-center' }
   */
  showSuccess(message: string, description?: string, options?: NotificationOptions) {
    showToast('success', message, description, options)
  },

  /**
   * 顯示一個失敗的訊息
   * @param message - 訊息的標題
   * @param description - 訊息的內容
   * @param options - 其他選項，例如 { html: true, position: 'top-center' }
   */
  showError(message: string, description?: string, options?: NotificationOptions) {
    showToast('error', message, description, options)
  },

  /**
   * 顯示一個信息的訊息
   * @param message - 訊息的標題
   * @param description - 訊息的內容
   * @param options - 其他選項，例如 { html: true, position: 'top-center' }
   */
  showInfo(message: string, description?: string, options?: NotificationOptions) {
    showToast('info', message, description, options)
  },

  /**
   * 顯示一個警告的訊息
   * @param message - 訊息的標題
   * @param description - 訊息的內容
   * @param options - 其他選項，例如 { html: true, position: 'top-center' }
   */
  showWarning(message: string, description?: string, options?: NotificationOptions) {
    showToast('warning', message, description, options)
  },
}
