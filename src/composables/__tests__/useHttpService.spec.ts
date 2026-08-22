/**
 * useHttpService 測試：Authorization 注入、401 處理與閘道攔截處理。
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/composables/useHttpService'
import { clearToken, onUnauthorized, setToken } from '@/composables/useAuthToken'

const reload = vi.fn()

describe('useHttpService', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    vi.restoreAllMocks()
    reload.mockClear()
    Object.defineProperty(window, 'location', {
      value: { ...window.location, origin: 'https://movera.example', reload },
      writable: true,
      configurable: true,
    })
  })

  afterEach(() => {
    clearToken()
  })

  function mockFetch(status: number, body: unknown = {}) {
    const fn = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(body), {
        status,
        headers: { 'Content-Type': 'application/json' },
      }),
    )
    vi.stubGlobal('fetch', fn)
    return fn
  }

  it('已登入時自動附帶 Authorization 標頭', async () => {
    setToken('jwt-token')
    const fetchFn = mockFetch(200, { ok: true })

    await request('GET', '/api/v1/tags')

    const init = fetchFn.mock.calls[0]![1] as RequestInit
    expect((init.headers as Record<string, string>)['Authorization']).toBe('Bearer jwt-token')
  })

  it('未登入時不附帶 Authorization 標頭', async () => {
    const fetchFn = mockFetch(200, { ok: true })

    await request('GET', '/api/v1/tags')

    const init = fetchFn.mock.calls[0]![1] as RequestInit
    expect((init.headers as Record<string, string>)['Authorization']).toBeUndefined()
  })

  it('收到 401 時觸發未授權處理並拋出錯誤', async () => {
    setToken('jwt-token')
    mockFetch(401, { detail: 'unauthorized' })
    const handler = vi.fn()
    onUnauthorized(handler)

    await expect(request('GET', '/api/v1/tags')).rejects.toThrow()
    expect(handler).toHaveBeenCalledOnce()
  })

  it('fetch 因閘道跨來源轉址而失敗時整頁重載並拋出原錯誤', async () => {
    setToken('jwt-token')
    // 第一次是實際請求（被 CORS 擋下），第二次是閘道探測
    const fetchFn = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce({ type: 'opaqueredirect', status: 0 })
    vi.stubGlobal('fetch', fetchFn)

    await expect(request('GET', '/api/v1/tags')).rejects.toThrow('Failed to fetch')

    const probeUrl = fetchFn.mock.calls[1]![0] as string
    expect(probeUrl).toContain('/api/v1/auth/status')
    expect(reload).toHaveBeenCalledOnce()
  })

  it('fetch 因離線而失敗時不重載，僅拋出原錯誤', async () => {
    setToken('jwt-token')
    // 實際請求與探測都失敗：屬於網路問題而非閘道攔截
    const fetchFn = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'))
    vi.stubGlobal('fetch', fetchFn)

    await expect(request('GET', '/api/v1/tags')).rejects.toThrow('Failed to fetch')
    expect(reload).not.toHaveBeenCalled()
  })

  it('收到非 JSON 的 403 閘道阻擋頁時整頁重載', async () => {
    setToken('jwt-token')
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response('<html>Access denied</html>', {
          status: 403,
          headers: { 'Content-Type': 'text/html' },
        }),
      ),
    )

    await expect(request('GET', '/api/v1/tags')).rejects.toThrow()
    expect(reload).toHaveBeenCalledOnce()
  })
})
