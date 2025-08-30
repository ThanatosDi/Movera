import { REGEX_TEST_CASES } from '@/constants'
import { highlightMatch, previewRegex } from '@/utils'
import { computed, ref, watch } from 'vue'

/**
 * 正規表達式預覽 Composable
 */
export function useRegexPreview(externalSrcRegex, externalDstRegex) {
  // 狀態
  const testFilename = ref('公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4')
  const srcRegex = ref('')
  const dstRegex = ref('')

  // 如果有外部的 regex refs，則同步它們
  if (externalSrcRegex) {
    watch(
      externalSrcRegex,
      (newValue) => {
        srcRegex.value = newValue
      },
      { immediate: true },
    )
  }

  if (externalDstRegex) {
    watch(
      externalDstRegex,
      (newValue) => {
        dstRegex.value = newValue
      },
      { immediate: true },
    )
  }

  // 計算屬性
  const regexResult = computed(() => {
    return previewRegex(srcRegex.value, dstRegex.value, testFilename.value)
  })

  const highlightedFilename = computed(() => {
    if (!regexResult.value.isValid || !regexResult.value.fullMatch) {
      return { before: testFilename.value, match: '', after: '' }
    }
    return highlightMatch(testFilename.value, regexResult.value.fullMatch)
  })

  const testCases = computed(() => REGEX_TEST_CASES)

  // 方法
  const setTestFilename = (filename) => {
    testFilename.value = filename
  }

  const setSrcRegex = (regex) => {
    srcRegex.value = regex
  }

  const setDstRegex = (regex) => {
    dstRegex.value = regex
  }

  const loadTestCase = (caseKey) => {
    const testCase = REGEX_TEST_CASES[caseKey]
    if (testCase) {
      testFilename.value = testCase.filename
      srcRegex.value = testCase.srcRegex
      dstRegex.value = testCase.dstRegex
    }
  }

  const resetPreview = () => {
    testFilename.value = '公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4'
    srcRegex.value = ''
    dstRegex.value = ''
  }

  return {
    // 狀態
    testFilename,
    srcRegex,
    dstRegex,

    // 計算屬性
    regexResult,
    highlightedFilename,
    testCases,

    // 方法
    setTestFilename,
    setSrcRegex,
    setDstRegex,
    loadTestCase,
    resetPreview,
  }
}
