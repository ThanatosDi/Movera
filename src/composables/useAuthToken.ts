/**
 * JWT 存取憑證的儲存與未授權處理。
 *
 * 將 token 存於 localStorage，並提供未授權（401）時的回呼註冊，
 * 讓 HTTP 層在收到 401 時可清除 token 並導向登入頁，避免與 store/router
 * 產生循環相依。
 */

const TOKEN_KEY = 'movera_access_token'

let unauthorizedHandler: (() => void) | null = null

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

/** 註冊收到 401 時要執行的處理（通常為清除 token 並導向登入）。 */
export function onUnauthorized(handler: () => void): void {
  unauthorizedHandler = handler
}

/** 由 HTTP 層在收到 401 時呼叫。 */
export function handleUnauthorized(): void {
  if (unauthorizedHandler) unauthorizedHandler()
}
