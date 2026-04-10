/**
 * useDirectoryBrowser Composable 單元測試
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useDirectoryBrowser } from '../useDirectoryBrowser'

// Mock useHttpService
const mockRequest = vi.fn()

vi.mock('../useHttpService', () => ({
  request: (...args: any[]) => mockRequest(...args),
}))

describe('useDirectoryBrowser', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('初始狀態', () => {
    it('應該有正確的初始狀態', () => {
      const { directories, loading, error } = useDirectoryBrowser()

      expect(directories.value).toEqual([])
      expect(loading.value).toBe(false)
      expect(error.value).toBeNull()
    })
  })

  describe('fetchDirectories 無參數', () => {
    it('應該呼叫 GET /api/v1/directories 並回傳根目錄', async () => {
      const mockDirs = {
        directories: [
          { name: 'downloads', path: '/downloads', has_children: true },
        ],
      }
      mockRequest.mockResolvedValue(mockDirs)

      const { directories, fetchDirectories } = useDirectoryBrowser()
      await fetchDirectories()

      expect(mockRequest).toHaveBeenCalledWith('GET', '/api/v1/directories')
      expect(directories.value).toEqual(mockDirs.directories)
    })
  })

  describe('fetchDirectories 帶參數', () => {
    it('應該呼叫 GET /api/v1/directories?path=... 並回傳子目錄', async () => {
      const mockDirs = {
        directories: [
          { name: 'anime', path: '/downloads/anime', has_children: true },
          { name: 'movies', path: '/downloads/movies', has_children: false },
        ],
      }
      mockRequest.mockResolvedValue(mockDirs)

      const { directories, fetchDirectories } = useDirectoryBrowser()
      await fetchDirectories('/downloads')

      expect(mockRequest).toHaveBeenCalledWith(
        'GET',
        '/api/v1/directories?path=%2Fdownloads'
      )
      expect(directories.value).toEqual(mockDirs.directories)
    })
  })

  describe('API 錯誤處理', () => {
    it('應該在 API 錯誤時提供錯誤訊息', async () => {
      mockRequest.mockRejectedValue(new Error('無權存取此目錄'))

      const { error, fetchDirectories } = useDirectoryBrowser()
      await fetchDirectories('/etc/secret')

      expect(error.value).toBe('無權存取此目錄')
    })
  })

  describe('loading 狀態管理', () => {
    it('應該在請求時設為 true，完成後設為 false', async () => {
      let resolvePromise: (value: any) => void
      mockRequest.mockReturnValue(
        new Promise((resolve) => {
          resolvePromise = resolve
        })
      )

      const { loading, fetchDirectories } = useDirectoryBrowser()

      const promise = fetchDirectories()
      expect(loading.value).toBe(true)

      resolvePromise!({ directories: [] })
      await promise

      expect(loading.value).toBe(false)
    })

    it('應該在錯誤時將 loading 設為 false', async () => {
      mockRequest.mockRejectedValue(new Error('error'))

      const { loading, fetchDirectories } = useDirectoryBrowser()
      await fetchDirectories()

      expect(loading.value).toBe(false)
    })
  })
})
