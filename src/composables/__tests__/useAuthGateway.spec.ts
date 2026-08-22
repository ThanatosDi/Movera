/**
 * useAuthGateway 測試：反向代理 SSO 閘道攔截的偵測與重載節流。
 */

import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  isGatewayBlockPage,
  isGatewayIntercepting,
  reloadForGateway,
} from '@/composables/useAuthGateway'

const reload = vi.fn()

beforeEach(() => {
  sessionStorage.clear()
  vi.restoreAllMocks()
  reload.mockClear()
  Object.defineProperty(window, 'location', {
    value: { ...window.location, reload },
    writable: true,
    configurable: true,
  })
})

describe('isGatewayIntercepting', () => {
  it('探測得到 opaqueredirect 時判定為被閘道攔截', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ type: 'opaqueredirect', status: 0 }))

    await expect(isGatewayIntercepting('https://movera.example')).resolves.toBe(true)
  })

  it('探測以 redirect: manual 發出，避免觸發 CORS 錯誤', async () => {
    const fetchFn = vi.fn().mockResolvedValue({ type: 'basic', status: 200 })
    vi.stubGlobal('fetch', fetchFn)

    await isGatewayIntercepting('https://movera.example')

    const [url, init] = fetchFn.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('https://movera.example/api/v1/auth/status')
    expect(init.redirect).toBe('manual')
    expect(init.cache).toBe('no-store')
  })

  it('探測得到正常回應時判定為未被攔截', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ type: 'basic', status: 200 }))

    await expect(isGatewayIntercepting('https://movera.example')).resolves.toBe(false)
  })

  it('探測本身失敗（離線）時不判定為攔截', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(isGatewayIntercepting('https://movera.example')).resolves.toBe(false)
  })
})

describe('isGatewayBlockPage', () => {
  function makeResponse(status: number, contentType: string): Response {
    return { status, headers: new Headers({ 'Content-Type': contentType }) } as Response
  }

  it('403 且非 JSON 時視為閘道阻擋頁', () => {
    expect(isGatewayBlockPage(makeResponse(403, 'text/html'))).toBe(true)
  })

  it('403 但為 JSON 時視為後端的正常錯誤回應', () => {
    expect(isGatewayBlockPage(makeResponse(403, 'application/json'))).toBe(false)
  })

  it('其他狀態碼不視為閘道阻擋頁', () => {
    expect(isGatewayBlockPage(makeResponse(401, 'text/html'))).toBe(false)
    expect(isGatewayBlockPage(makeResponse(500, 'text/html'))).toBe(false)
  })
})

describe('reloadForGateway', () => {
  it('首次呼叫時觸發整頁重載', () => {
    expect(reloadForGateway()).toBe(true)
    expect(reload).toHaveBeenCalledOnce()
  })

  it('節流期間內重複呼叫不再重載，避免無限重載', () => {
    reloadForGateway()
    reload.mockClear()

    expect(reloadForGateway()).toBe(false)
    expect(reload).not.toHaveBeenCalled()
  })
})
