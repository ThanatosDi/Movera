/**
 * AuthStore 單元測試
 */

import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockRequest = vi.hoisted(() => vi.fn())
vi.mock('@/composables/useHttpService', () => ({
  request: (...args: any[]) => mockRequest(...args),
}))

// 以可預期的雜湊取代 sha256，方便斷言「送出的是雜湊而非明文」
vi.mock('@/lib/hash', () => ({
  sha256Hex: vi.fn(async (text: string) => `hashed:${text}`),
}))

describe('AuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('login', () => {
    it('應該以雜湊後的密碼送出，且不含明文', async () => {
      const { useAuthStore } = await import('../authStore')
      const store = useAuthStore()
      mockRequest.mockResolvedValueOnce({ access_token: 'jwt-1', token_type: 'bearer' })

      await store.login('admin', 'plaintext-pw')

      expect(mockRequest).toHaveBeenCalledWith('POST', '/api/v1/auth/login', {
        username: 'admin',
        password: 'hashed:plaintext-pw',
      })
      // payload 不應包含明文
      const payload = mockRequest.mock.calls[0]![2] as { password: string }
      expect(payload.password).not.toBe('plaintext-pw')
    })

    it('登入成功後儲存 token 並標記為已驗證', async () => {
      const { useAuthStore } = await import('../authStore')
      const store = useAuthStore()
      mockRequest.mockResolvedValueOnce({ access_token: 'jwt-1', token_type: 'bearer' })

      await store.login('admin', 'pw')

      expect(store.token).toBe('jwt-1')
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.getItem('movera_access_token')).toBe('jwt-1')
    })
  })

  describe('setup', () => {
    it('初始化成功後儲存 token 並清除 needsSetup', async () => {
      const { useAuthStore } = await import('../authStore')
      const store = useAuthStore()
      mockRequest.mockResolvedValueOnce({ access_token: 'jwt-2', token_type: 'bearer' })

      await store.setup('admin', 'pw')

      expect(store.token).toBe('jwt-2')
      expect(store.needsSetup).toBe(false)
    })
  })

  describe('logout', () => {
    it('應該清除 token', async () => {
      const { useAuthStore } = await import('../authStore')
      const store = useAuthStore()
      mockRequest.mockResolvedValueOnce({ access_token: 'jwt-1', token_type: 'bearer' })
      await store.login('admin', 'pw')

      store.logout()

      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(localStorage.getItem('movera_access_token')).toBeNull()
    })
  })

  describe('fetchStatus', () => {
    it('應該回傳 needs_setup', async () => {
      const { useAuthStore } = await import('../authStore')
      const store = useAuthStore()
      mockRequest.mockResolvedValueOnce({ needs_setup: true })

      const result = await store.fetchStatus()

      expect(result).toBe(true)
      expect(store.needsSetup).toBe(true)
    })
  })
})
