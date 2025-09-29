import { parsePreviewService, type ParsePreviewPayload } from '@/services/parsePreviewService';
import { ref, watch, type Ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n()

// 定義解析後的欄位結構
interface ParsedFields {
  [key: string]: any;
}

/**
 * @description 一個簡易的 debounce 工具函式
 * @param fn 要延遲執行的函式
 * @param delay 延遲的毫秒數
 */
function useDebounce<T extends (...args: any[]) => void>(fn: T, delay: number) {
  let timeoutId: number | undefined;
  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = window.setTimeout(() => {
      fn(...args);
    }, delay);
  };
}

/**
 * @description 用於即時預覽 'parse' 規則解析檔名結果的 Vue Composable。
 *              此版本透過呼叫後端 API 來獲取結果。
 * @param filename - Ref<string | null>：要測試的原始檔名。
 * @param srcRule - Ref<string | null>：來源解析規則。
 * @param dstRule - Ref<string | null>：目標格式化規則。
 * @returns - { parsedFields, formattedResult, error, isLoading }：包含結果、錯誤和載入狀態的響應式物件。
 */
export function useParsePreview(
  filename: Ref<string | null>,
  srcRule: Ref<string | null>,
  dstRule: Ref<string | null>
) {
  const parsedFields = ref<ParsedFields | null>(null);
  const formattedResult = ref<string | null>(null);
  const error = ref<string | null>(null);
  const isLoading = ref(false);

  const fetchPreview = async () => {
    const payload: ParsePreviewPayload = {
      text: filename.value || '',
      src_pattern: srcRule.value || '',
      dst_pattern: dstRule.value || '',
    };

    // 如果沒有填寫所有欄位，則清除結果，不發送請求
    if (!payload.text || !payload.src_pattern) {
      parsedFields.value = null;
      formattedResult.value = null;
      error.value = null;
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await parsePreviewService.getPreview(payload);
      parsedFields.value = response.groups;
      formattedResult.value = response.formatted;

      // 如果後端沒有回傳任何群組，可能表示不匹配
      if (Object.keys(response.groups).length === 0 && !response.formatted) {
        error.value = t('notifications.formValidation.parseNoMatch');
      }

    } catch (e: any) {
      console.error('獲取 Parse 預覽失敗:', e);
      error.value = e.message || '發生未知錯誤。';
      parsedFields.value = null;
      formattedResult.value = null;
    } finally {
      isLoading.value = false;
    }
  };

  // 建立一個帶有 debounce 功能的 fetch 函式
  const debouncedFetchPreview = useDebounce(fetchPreview, 400);

  // 監聽所有輸入的變化，並在變化時呼叫 debounced 函式
  watch([filename, srcRule, dstRule], debouncedFetchPreview, { immediate: true });

  return {
    parsedFields,
    formattedResult,
    error,
    isLoading,
  };
}
