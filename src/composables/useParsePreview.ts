import { wsEventsEnum } from '@/enums/wsEventsEnum'
import type { Ref } from 'vue'
import { usePreview } from './usePreview'

/**
 * Parse 預覽的 groups 結構
 */
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
  return usePreview<ParseGroups>(text, srcPattern, dstPattern, {
    eventType: wsEventsEnum.previewParse,
    initialGroups: {},
    logPrefix: 'useParsePreview'
  })
}
