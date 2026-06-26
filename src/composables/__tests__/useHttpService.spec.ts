/**
 * useHttpService 測試：Authorization 注入與 401 處理。
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/composables/useHttpService'
import { clearToken, onUnauthorized, setToken } from '@/composables/useAuthToken'

describe('useHttpService', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
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
})
