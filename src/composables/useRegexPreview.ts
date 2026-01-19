import { wsEventsEnum } from '@/enums/wsEventsEnum'
import type { Ref } from 'vue'
import { usePreview } from './usePreview'

/**
 * Regex 預覽的 groups 結構
 */
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
  return usePreview<RegexGroups>(text, srcPattern, dstPattern, {
    eventType: wsEventsEnum.previewRegex,
    initialGroups: { named_group: {}, numbered_group: [] },
    logPrefix: 'useRegexPreview'
  })
}
