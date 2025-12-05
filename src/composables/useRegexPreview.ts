import { wsEventsEnum } from '@/enums/wsEventsEnum'
import { debounce } from 'perfect-debounce'
import type { Ref } from 'vue'
import { ref, watch } from 'vue'
import { useWebSocketService } from './useWebSocketService'

/**
 * 預覽解析事件的請求資料
 */
interface RegexPreviewPayload {
  src_pattern: string
  text: string
  dst_pattern: string
}

/**
 * 預覽解析事件的回應資料
 */
interface RegexPreviewResponse {
  src_pattern: string
  text: string
  dst_pattern: string
  groups: RegexGroups
  formatted: string
}

interface RegexGroups {
  named_group: Record<string, string>  // 具名群組，例如 { title: "...", episode: "..." }
  numbered_group: (string | null)[]     // 編號群組，可能包含 null
}

/**
 * 正則表達式預覽功能的 Composable
 * 透過 WebSocket 發送請求以預覽正則表達式解析結果
 *
 * @param text - 要解析的測試檔名或文字
 * @param srcPattern - 來源正則表達式模式
 * @param dstPattern - 目標格式化模式
 * @returns 回應式的預覽資料與載入狀態
 */
export function useRegexPreview(
  text: Ref<string>,
  srcPattern: Ref<string>,
  dstPattern: Ref<string>
) {
  const { request, status } = useWebSocketService()
  const groups = ref<RegexGroups>({ named_group: {}, numbered_group: [] })
  const formattedResult = ref<string>('')
  // 錯誤訊息（如果請求失敗）
  const error = ref<string | null>(null)

  /**
   * 透過 WebSocket 從後端取得預覽結果
   */
  const fetchRegexPreview = async () => {
    // 如果必填欄位為空，重置結果
    if (!text.value || !srcPattern.value) {
      groups.value = { named_group: {}, numbered_group: [] }
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
      const payload: RegexPreviewPayload = {
        text: text.value,
        src_pattern: srcPattern.value,
        dst_pattern: dstPattern.value
      }

      const response = await request<RegexPreviewResponse>(
        wsEventsEnum.previewRegex,
        payload,
        5000 // 5 秒逾時
      )

      // 更新狀態與結果
      groups.value = response.groups
      formattedResult.value = response.formatted
      error.value = null

    } catch (err: any) {
      console.error('[useRegexPreview] 取得預覽失敗:', err)
      error.value = err.message || 'errors.preview.fetchFailed'
      groups.value = { named_group: {}, numbered_group: [] }
      formattedResult.value = ''
    }
  }

  // 防抖版本，避免過多請求
  const debouncedFetchPreview = debounce(fetchRegexPreview, 500)

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
    refetch: fetchRegexPreview
  }
}
