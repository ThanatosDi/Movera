import type { MaybeRef } from 'vue'
import { computed, unref } from 'vue'

/**
 * 將 Python-style backreferences (\1, \2) 轉換為 JS-style ($1, $2)。
 * @param replacement - 包含 backreferences 的替換字串。
 * @returns JS 風格的替換字串。
 */
function convertToJsBackreferences(replacement: string): string {
  // 匹配 \1 到 \99，並轉換為 $1 到 $99
  return replacement.replace(/\\(\d+)/g, '$$$1')
}
/**
 * 根據輸入的正規表示式樣板和替換樣板，對文字進行預覽。
 * @param inputText - 要進行匹配和替換的原始文字。
 * @param pattern -正規表示式樣板。
 * @param replacement - 替換樣板。
 * @returns 一個包含預覽結果的物件。
 */
function evaluateRegexPreview(
  inputText: string,
  pattern: string,
  replacement: string
) {
  // 1. 驗證並建立正規表示式物件
  let regex: RegExp
  try {
    regex = new RegExp(pattern, 'gi')
  }
  catch (e: any) {
    return {
      isValid: false,
      matches: [],
      groups: [],
      renamedFilename: '',
      fullMatch: null,
      error: `正規表示式錯誤: ${e.message}`,
    }
  }

  // 2. 執行匹配
  const matches = [...inputText.matchAll(regex)]
  if (matches.length === 0) {
    return { isValid: false, matches: [], groups: [], renamedFilename: '', fullMatch: null, error: '無匹配結果' }
  }

  // 3. 執行替換 (如果提供了替換樣板)
  let renamedFilename = ''
  if (replacement) {
    try {
      const jsStyleReplacement = convertToJsBackreferences(replacement)
      renamedFilename = inputText.replace(regex, jsStyleReplacement)
    }
    catch (e: any) {
      // 這種錯誤通常發生在替換樣板格式不對時，例如無效的 backreference
      return {
        isValid: true, // 匹配仍然是有效的
        matches,
        groups: matches[0].slice(1),
        renamedFilename: `重新命名格式錯誤: ${e.message}`,
        fullMatch: matches[0][0],
        error: `重新命名格式錯誤: ${e.message}`,
      }
    }
  }

  // 4. 成功回傳
  const firstMatch = matches[0]
  return {
    isValid: true,
    matches,
    groups: firstMatch.slice(1),
    renamedFilename,
    fullMatch: firstMatch[0],
    error: null,
  }
}
/**
 * 將 filename 轉換為 dst_filename 使用 JS 正規表示式,
 * 並將 Python-style backreferences (\1, \2) 轉換為 JS-style ($1, $2)。
 *
 * @example
 * const { preview, highlighted, error } = useRegexPreview(
 *   '公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4',
 *   '公爵千金的家庭教師 - (\d{2})(v2)? .+\.mp4',
 *   '公爵千金的家庭教師 - S01E\1 [1080P][WEB-DL][AAC AVC][CHT].mp4'
 * )
 * // preview: '公爵千金的家庭教師 - S01E01 [1080P][WEB-DL][AAC AVC][CHT].mp4'
 * // highlighted: '<span class="bg-yellow-300 rounded p-0.5">公爵千金的家庭教師 - 01</span> [1080P][WEB-DL][AAC AVC][CHT].mp4'
 * // error: null
 *
 * @param {MaybeRef<string>} filename - 要轉換的檔案名稱
 * @param {MaybeRef<string>} src_filename -正規表示式來源
 * @param {MaybeRef<string>} dst_filename - 正規表示式目標
 * @returns {Object} - 轉換後的結果
 *   - preview: 轉換後的檔案名稱
 *   - highlighted: 轉換後的檔案名稱，並 highlight 了正規表示式的 match 部分
 *   - error: 轉換過程中發生的錯誤訊息
 */
export function useRegexPreview(
  filename: MaybeRef<string>,
  src_filename: MaybeRef<string>,
  dst_filename: MaybeRef<string>
) {
  const regexResult = computed(() => {
    const currentFilename = unref(filename)
    const currentSrc = unref(src_filename)
    const currentDst = unref(dst_filename)
    return evaluateRegexPreview(currentFilename, currentSrc, currentDst)
  })

  const preview = computed(() => regexResult.value.renamedFilename)
  const error = computed(() => regexResult.value.error)

  const highlightedParts = computed(() => {
    const { isValid, fullMatch } = regexResult.value
    const currentFilename = unref(filename)

    // 如果沒有有效的匹配，則回傳整個檔名作為 'before' 部分
    if (!isValid || !fullMatch) {
      return {
        before: currentFilename,
        match: '',
        after: '',
      }
    }

    // 找到匹配文字的起始索引
    const startIndex = currentFilename.indexOf(fullMatch)

    // 再次檢查以防萬一 (雖然在 fullMatch 存在時，indexOf 幾乎不可能為 -1)
    if (startIndex === -1) {
      return { before: currentFilename, match: '', after: '' }
    }

    const endIndex = startIndex + fullMatch.length

    // 將原始字串分割成三個部分
    return {
      before: currentFilename.substring(0, startIndex),
      match: fullMatch, // 或者 currentFilename.substring(startIndex, endIndex)
      after: currentFilename.substring(endIndex),
    }
  })

  return {
    isValid: computed(() => regexResult.value.isValid),
    groups: computed(() => regexResult.value.groups),
    preview,
    highlightedParts,
    error,
  }
}
