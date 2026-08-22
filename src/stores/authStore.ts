import { clearToken, discardTokenIfExpired, getToken, setToken } from '@/composables/useAuthToken'
import { request } from '@/composables/useHttpService'
import { sha256Hex } from '@/lib/hash'
import type { AuthStatus, TokenResponse } from '@/schemas'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('authStore', () => {
  // 過期憑證直接丟棄，避免 isAuthenticated 誤判為已登入
  const token = ref<string | null>(discardTokenIfExpired() ? null : getToken())
  const needsSetup = ref<boolean>(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  /** 查詢系統是否尚未建立任何管理員帳號（決定顯示登入或初始化）。 */
  async function fetchStatus(): Promise<boolean> {
    const status = await request<AuthStatus>('GET', '/api/v1/auth/status')
    needsSetup.value = status.needs_setup
    return status.needs_setup
  }

  /** 以使用者名稱與密碼登入。密碼於送出前以 SHA-256 雜湊。 */
  async function login(username: string, password: string): Promise<void> {
    error.value = null
    const passwordHash = await sha256Hex(password)
    const res = await request<TokenResponse>('POST', '/api/v1/auth/login', {
      username,
      password: passwordHash,
    })
    token.value = res.access_token
    setToken(res.access_token)
  }

  /** 初始化建立第一組管理員帳密，成功後即視為已登入。 */
  async function setup(username: string, password: string): Promise<void> {
    error.value = null
    const passwordHash = await sha256Hex(password)
    const res = await request<TokenResponse>('POST', '/api/v1/auth/setup', {
      username,
      password: passwordHash,
    })
    token.value = res.access_token
    setToken(res.access_token)
    needsSetup.value = false
  }

  /** 登出：清除 token。 */
  function logout(): void {
    token.value = null
    clearToken()
  }

  return {
    token,
    needsSetup,
    error,
    isAuthenticated,
    fetchStatus,
    login,
    setup,
    logout,
  }
})
