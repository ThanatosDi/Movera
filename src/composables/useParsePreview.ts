import { wsEventsEnum } from '@/enums/wsEventsEnum'
import { debounce } from 'perfect-debounce'
import type { Ref } from 'vue'
import { ref, watch } from 'vue'
import { useWebSocketService } from './useWebSocketService'

/**
 * 預覽解析事件的請求資料
 */
interface ParsePreviewPayload {
  src_pattern: string
  text: string
  dst_pattern: string
}

/**
 * 預覽解析事件的回應資料
 */
interface ParsePreviewResponse {
  src_pattern: string
  text: string
  dst_pattern: string
  groups: ParseGroups  // [鍵, 值] 配對的陣列
  formatted: string
}

interface ParseGroups {
  [key: string]: string
}

/**
 * 解析預覽功能的 Composable
 * 透過 WebSocket 發送請求以預覽解析結果
 *
 * @param text - 要解析的測試檔名或文字
 * @param srcPattern - 來源模式規則
 * @param dstPattern - 目標模式規則
 * @returns 回應式的預覽資料與載入狀態
 */
export function useParsePreview(
  text: Ref<string>,
  srcPattern: Ref<string>,
  dstPattern: Ref<string>
) {
  const { request, status } = useWebSocketService()
  const groups = ref<ParseGroups>({})
  const formattedResult = ref<string>('')
  // 錯誤訊息（如果請求失敗）
  const error = ref<string | null>(null)

  /**
   * 透過 WebSocket 從後端取得預覽結果
   */
  const fetchParsePreview = async () => {
    // 如果必填欄位為空，重置結果
    if (!text.value || !srcPattern.value) {
      groups.value = {}
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
      const payload: ParsePreviewPayload = {
        text: text.value,
        src_pattern: srcPattern.value,
        dst_pattern: dstPattern.value
      }

      const response = await request<ParsePreviewResponse>(
        wsEventsEnum.previewParse,
        payload,
        5000 // 5 秒逾時
      )

      // 更新狀態與結果
      groups.value = response.groups
      formattedResult.value = response.formatted
      error.value = null

    } catch (err: any) {
      console.error('[useParsePreview] 取得預覽失敗:', err)
      error.value = err.message || 'errors.preview.fetchFailed'
      groups.value = {}
      formattedResult.value = ''
    } finally {
    }
  }

  // 防抖版本，避免過多請求
  const debouncedFetchPreview = debounce(fetchParsePreview, 500)

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
    refetch: fetchParsePreview
  }
}
