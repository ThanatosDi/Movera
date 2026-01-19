/**
 * useRegexPreview Composable 單元測試
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick, ref } from 'vue'
import { useRegexPreview } from '../useRegexPreview'

// Mock useWebSocketService
const mockRequest = vi.fn()
const mockStatus = ref('OPEN')

vi.mock('../useWebSocketService', () => ({
  useWebSocketService: () => ({
    request: mockRequest,
    status: mockStatus,
  }),
}))

// Mock perfect-debounce
vi.mock('perfect-debounce', () => ({
  debounce: (fn: Function) => fn,  // 移除防抖以便測試
}))

describe('useRegexPreview', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockStatus.value = 'OPEN'
  })

  describe('初始狀態', () => {
    it('應該有正確的初始狀態', () => {
      const text = ref('')
      const srcPattern = ref('')
      const dstPattern = ref('')

      const { groups, formattedResult, error } = useRegexPreview(text, srcPattern, dstPattern)

      expect(groups.value).toEqual({ named_group: {}, numbered_group: [] })
      expect(formattedResult.value).toBe('')
      expect(error.value).toBeNull()
    })
  })

  describe('當輸入為空', () => {
    it('不應該發送請求', async () => {
      const text = ref('')
      const srcPattern = ref('')
      const dstPattern = ref('')

      useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(mockRequest).not.toHaveBeenCalled()
    })

    it('應該重置結果', async () => {
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('')

      mockRequest.mockResolvedValueOnce({
        groups: { named_group: { title: 'test' }, numbered_group: ['test'] },
        formatted: 'result',
      })

      const { groups, formattedResult } = useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      // 清空輸入
      text.value = ''
      await nextTick()

      expect(groups.value).toEqual({ named_group: {}, numbered_group: [] })
      expect(formattedResult.value).toBe('')
    })
  })

  describe('WebSocket 連線狀態', () => {
    it('未連線時應該設置錯誤', async () => {
      mockStatus.value = 'CLOSED'
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      const { error } = useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(error.value).toBe('errors.websocket.notConnected')
      expect(mockRequest).not.toHaveBeenCalled()
    })
  })

  describe('成功請求', () => {
    it('應該正確更新結果 (編號群組)', async () => {
      const text = ref('動畫名稱 - 01.mp4')
      const srcPattern = ref(String.raw`(.+) - (\d+)\.mp4`)
      const dstPattern = ref(String.raw`\1 - S01E\2.mp4`)

      const responseData = {
        src_pattern: String.raw`(.+) - (\d+)\.mp4`,
        text: '動畫名稱 - 01.mp4',
        dst_pattern: String.raw`\1 - S01E\2.mp4`,
        groups: {
          named_group: {},
          numbered_group: ['動畫名稱', '01'],
        },
        formatted: '動畫名稱 - S01E01.mp4',
      }
      mockRequest.mockResolvedValueOnce(responseData)

      const { groups, formattedResult, error } = useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(groups.value.numbered_group).toEqual(['動畫名稱', '01'])
      expect(formattedResult.value).toBe('動畫名稱 - S01E01.mp4')
      expect(error.value).toBeNull()
    })

    it('應該正確更新結果 (命名群組)', async () => {
      const text = ref('動畫名稱 - 01.mp4')
      const srcPattern = ref(String.raw`(?P<title>.+) - (?P<ep>\d+)\.mp4`)
      const dstPattern = ref(String.raw`\g<title> - S01E\g<ep>.mp4`)

      const responseData = {
        groups: {
          named_group: { title: '動畫名稱', ep: '01' },
          numbered_group: ['動畫名稱', '01'],
        },
        formatted: '動畫名稱 - S01E01.mp4',
      }
      mockRequest.mockResolvedValueOnce(responseData)

      const { groups } = useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(groups.value.named_group).toEqual({ title: '動畫名稱', ep: '01' })
    })
  })

  describe('請求失敗', () => {
    it('應該設置錯誤訊息', async () => {
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      mockRequest.mockRejectedValueOnce(new Error('無效的正則表達式'))

      const { groups, formattedResult, error } = useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(error.value).toBe('無效的正則表達式')
      expect(groups.value).toEqual({ named_group: {}, numbered_group: [] })
      expect(formattedResult.value).toBe('')
    })
  })

  describe('refetch', () => {
    it('應該能手動重新請求', async () => {
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      mockRequest.mockResolvedValue({
        groups: { named_group: {}, numbered_group: [] },
        formatted: '',
      })

      const { refetch } = useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      mockRequest.mockClear()
      await refetch()

      expect(mockRequest).toHaveBeenCalledTimes(1)
    })
  })

  describe('watch 響應', () => {
    it('srcPattern 變化時應該觸發請求', async () => {
      const text = ref('test')
      const srcPattern = ref('initial')
      const dstPattern = ref('output')

      mockRequest.mockResolvedValue({
        groups: { named_group: {}, numbered_group: [] },
        formatted: '',
      })

      useRegexPreview(text, srcPattern, dstPattern)
      await nextTick()

      mockRequest.mockClear()
      srcPattern.value = 'changed'
      await nextTick()

      expect(mockRequest).toHaveBeenCalled()
    })
  })
})
