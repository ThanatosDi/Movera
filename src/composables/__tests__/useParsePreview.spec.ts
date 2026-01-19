/**
 * useParsePreview Composable 單元測試
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick, ref } from 'vue'
import { useParsePreview } from '../useParsePreview'

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

describe('useParsePreview', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockStatus.value = 'OPEN'
  })

  describe('初始狀態', () => {
    it('應該有正確的初始狀態', () => {
      const text = ref('')
      const srcPattern = ref('')
      const dstPattern = ref('')

      const { groups, formattedResult, error } = useParsePreview(text, srcPattern, dstPattern)

      expect(groups.value).toEqual({})
      expect(formattedResult.value).toBe('')
      expect(error.value).toBeNull()
    })
  })

  describe('當輸入為空', () => {
    it('不應該發送請求', async () => {
      const text = ref('')
      const srcPattern = ref('')
      const dstPattern = ref('')

      useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(mockRequest).not.toHaveBeenCalled()
    })

    it('應該重置結果', async () => {
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('')

      mockRequest.mockResolvedValueOnce({
        groups: { title: 'test' },
        formatted: 'result',
      })

      const { groups, formattedResult } = useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      // 清空輸入
      text.value = ''
      await nextTick()

      expect(groups.value).toEqual({})
      expect(formattedResult.value).toBe('')
    })
  })

  describe('WebSocket 連線狀態', () => {
    it('未連線時應該設置錯誤', async () => {
      mockStatus.value = 'CLOSED'
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      const { error } = useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(error.value).toBe('errors.websocket.notConnected')
      expect(mockRequest).not.toHaveBeenCalled()
    })
  })

  describe('成功請求', () => {
    it('應該正確更新結果', async () => {
      const text = ref('動畫名稱 - 01.mp4')
      const srcPattern = ref('{title} - {episode}.mp4')
      const dstPattern = ref('{title} - S01E{episode}.mp4')

      const responseData = {
        src_pattern: '{title} - {episode}.mp4',
        text: '動畫名稱 - 01.mp4',
        dst_pattern: '{title} - S01E{episode}.mp4',
        groups: { title: '動畫名稱', episode: '01' },
        formatted: '動畫名稱 - S01E01.mp4',
      }
      mockRequest.mockResolvedValueOnce(responseData)

      const { groups, formattedResult, error } = useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(groups.value).toEqual({ title: '動畫名稱', episode: '01' })
      expect(formattedResult.value).toBe('動畫名稱 - S01E01.mp4')
      expect(error.value).toBeNull()
    })
  })

  describe('請求失敗', () => {
    it('應該設置錯誤訊息', async () => {
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      mockRequest.mockRejectedValueOnce(new Error('請求失敗'))

      const { groups, formattedResult, error } = useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      expect(error.value).toBe('請求失敗')
      expect(groups.value).toEqual({})
      expect(formattedResult.value).toBe('')
    })
  })

  describe('refetch', () => {
    it('應該能手動重新請求', async () => {
      const text = ref('test')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      mockRequest.mockResolvedValue({
        groups: {},
        formatted: '',
      })

      const { refetch } = useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      mockRequest.mockClear()
      await refetch()

      expect(mockRequest).toHaveBeenCalledTimes(1)
    })
  })

  describe('watch 響應', () => {
    it('輸入變化時應該觸發請求', async () => {
      const text = ref('initial')
      const srcPattern = ref('pattern')
      const dstPattern = ref('output')

      mockRequest.mockResolvedValue({ groups: {}, formatted: '' })

      useParsePreview(text, srcPattern, dstPattern)
      await nextTick()

      mockRequest.mockClear()
      text.value = 'changed'
      await nextTick()

      expect(mockRequest).toHaveBeenCalled()
    })
  })
})
