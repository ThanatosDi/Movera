/**
 * WebhookTokenStore 單元測試
 */

import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockRequest = vi.hoisted(() => vi.fn())
vi.mock('@/composables/useHttpService', () => ({
  request: (...args: any[]) => mockRequest(...args),
}))

describe('WebhookTokenStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchTokens 應載入清單', async () => {
    const { useWebhookTokenStore } = await import('../webhookTokenStore')
    const store = useWebhookTokenStore()
    mockRequest.mockResolvedValueOnce([
      { id: '1', name: 'qb', created_at: 'x', revoked_at: null },
    ])

    await store.fetchTokens()

    expect(store.tokens).toHaveLength(1)
    expect(store.tokens[0]!.name).toBe('qb')
  })

  it('createToken 回傳一次性明文並重新載入清單', async () => {
    const { useWebhookTokenStore } = await import('../webhookTokenStore')
    const store = useWebhookTokenStore()
    // 第一次：create 回傳含明文
    mockRequest.mockResolvedValueOnce({
      id: '1',
      name: 'qb',
      created_at: 'x',
      revoked_at: null,
      token: 'movera_abc123',
    })
    // 第二次：fetchTokens
    mockRequest.mockResolvedValueOnce([
      { id: '1', name: 'qb', created_at: 'x', revoked_at: null },
    ])

    const created = await store.createToken('qb')

    expect(created.token).toBe('movera_abc123')
    expect(mockRequest).toHaveBeenCalledWith('POST', '/api/v1/webhook-tokens', { name: 'qb' })
  })

  it('revokeToken 呼叫 DELETE 並重新載入', async () => {
    const { useWebhookTokenStore } = await import('../webhookTokenStore')
    const store = useWebhookTokenStore()
    mockRequest.mockResolvedValueOnce(undefined) // delete
    mockRequest.mockResolvedValueOnce([]) // fetch

    await store.revokeToken('1')

    expect(mockRequest).toHaveBeenCalledWith('DELETE', '/api/v1/webhook-tokens/1')
  })

  it('deleteToken 呼叫永久刪除端點並重新載入', async () => {
    const { useWebhookTokenStore } = await import('../webhookTokenStore')
    const store = useWebhookTokenStore()
    mockRequest.mockResolvedValueOnce(undefined) // delete permanent
    mockRequest.mockResolvedValueOnce([]) // fetch

    await store.deleteToken('1')

    expect(mockRequest).toHaveBeenCalledWith('DELETE', '/api/v1/webhook-tokens/1/permanent')
  })
})
