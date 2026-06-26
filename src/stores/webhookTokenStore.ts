import { request } from '@/composables/useHttpService'
import type { WebhookToken, WebhookTokenCreated } from '@/schemas'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWebhookTokenStore = defineStore('webhookTokenStore', () => {
  const tokens = ref<WebhookToken[]>([])
  const error = ref<string | null>(null)
  const isLoading = ref<boolean>(false)

  /** 載入所有 webhook token。 */
  async function fetchTokens(): Promise<void> {
    error.value = null
    isLoading.value = true
    try {
      tokens.value = await request<WebhookToken[]>('GET', '/api/v1/webhook-tokens')
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /** 建立新 token，回傳含一次性明文的結果。 */
  async function createToken(name: string): Promise<WebhookTokenCreated> {
    error.value = null
    const created = await request<WebhookTokenCreated>(
      'POST',
      '/api/v1/webhook-tokens',
      { name },
    )
    await fetchTokens()
    return created
  }

  /** 撤銷指定 token。 */
  async function revokeToken(id: string): Promise<void> {
    error.value = null
    await request('DELETE', `/api/v1/webhook-tokens/${id}`)
    await fetchTokens()
  }

  /** 永久刪除已撤銷的 token。 */
  async function deleteToken(id: string): Promise<void> {
    error.value = null
    await request('DELETE', `/api/v1/webhook-tokens/${id}/permanent`)
    await fetchTokens()
  }

  return {
    tokens,
    error,
    isLoading,
    fetchTokens,
    createToken,
    revokeToken,
    deleteToken,
  }
})
