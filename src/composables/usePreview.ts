import { debounce } from 'perfect-debounce'
import type { Ref } from 'vue'
import { ref, watch } from 'vue'
import { useWebSocketService } from './useWebSocketService'

/**
 * 預覽請求的 payload 結構
 */
interface PreviewPayload {
  src_pattern: string
  text: string
  dst_pattern: string
}

/**
 * 預覽回應的基礎結構
 */
interface PreviewResponse<TGroups> {
  src_pattern: string
  text: string
  dst_pattern: string
  groups: TGroups
  formatted: string
}

/**
 * Preview Composable 的配置選項
 */
interface PreviewConfig<TGroups> {
  /** WebSocket 事件類型 */
  eventType: string
  /** groups 的初始值 */
  initialGroups: TGroups
  /** 日誌前綴，用於錯誤訊息 */
  logPrefix: string
}

/**
 * 通用的預覽功能 Composable
 * 透過 WebSocket 發送請求以預覽解析結果
 *
 * @param text - 要解析的測試檔名或文字
 * @param srcPattern - 來源模式規則
 * @param dstPattern - 目標模式規則
 * @param config - 配置選項
 * @returns 回應式的預覽資料與載入狀態
 */
export function usePreview<TGroups>(
  text: Ref<string>,
  srcPattern: Ref<string>,
  dstPattern: Ref<string>,
  config: PreviewConfig<TGroups>
) {
  const { request, status } = useWebSocketService()
  const groups = ref<TGroups>(config.initialGroups) as Ref<TGroups>
  const formattedResult = ref<string>('')
  const error = ref<string | null>(null)

  /**
   * 透過 WebSocket 從後端取得預覽結果
   */
  const fetchPreview = async () => {
    // 如果必填欄位為空，重置結果
    if (!text.value || !srcPattern.value) {
      groups.value = config.initialGroups
      formattedResult.value = ''
      error.value = null
      return
    }

    // 檢查 WebSocket 連線狀態
    if (status.value !== 'OPEN') {
      error.value = 'errors.websocket.notConnected'
      return
    }

    error.value = null

    try {
      const payload: PreviewPayload = {
        text: text.value,
        src_pattern: srcPattern.value,
        dst_pattern: dstPattern.value
      }

      const response = await request<PreviewResponse<TGroups>>(
        config.eventType,
        payload,
        5000 // 5 秒逾時
      )

      // 更新狀態與結果
      groups.value = response.groups
      formattedResult.value = response.formatted
      error.value = null
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'errors.preview.fetchFailed'
      console.error(`[${config.logPrefix}] 取得預覽失敗:`, err)
      error.value = errorMessage
      groups.value = config.initialGroups
      formattedResult.value = ''
    }
  }

  // 防抖版本，避免過多請求
  const debouncedFetchPreview = debounce(fetchPreview, 500)

  // 監聽輸入變化並觸發預覽
  watch(
    [text, srcPattern, dstPattern],
    () => {
      debouncedFetchPreview()
    },
    { immediate: true }
  )

  return {
    groups,
    formattedResult,
    error,
    refetch: fetchPreview
  }
}
