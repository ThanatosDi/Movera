/**
 * JWT 存取憑證的儲存與未授權處理。
 *
 * 將 token 存於 localStorage，並提供未授權（401）時的回呼註冊，
 * 讓 HTTP 層在收到 401 時可清除 token 並導向登入頁，避免與 store/router
 * 產生循環相依。
 */

const TOKEN_KEY = 'movera_access_token'

/**
 * 允許的時鐘偏移（秒）。
 *
 * 用戶端時鐘可能快於伺服器，若嚴格比對 exp 會造成憑證其實仍有效卻被提前登出，
 * 因此保留一段寬容區間。
 */
const CLOCK_SKEW_LEEWAY_SECONDS = 60

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

/** 解碼 base64url 片段為文字。 */
function decodeBase64Url(segment: string): string {
  const base64 = segment.replace(/-/g, '+').replace(/_/g, '/')
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
  const binary = atob(padded)
  const bytes = Uint8Array.from(binary, char => char.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

/**
 * 讀取 JWT payload 中的 exp（Unix 秒）。
 *
 * 僅解析、不驗證簽章：目的是讓前端提早得知憑證已過期，真正的授權判斷仍由
 * 後端 require_jwt 負責。無法解析時回傳 null。
 */
function readExpiry(token: string): number | null {
  const parts = token.split('.')
  if (parts.length !== 3 || !parts[1]) return null
  try {
    const payload = JSON.parse(decodeBase64Url(parts[1])) as { exp?: unknown }
    return typeof payload.exp === 'number' ? payload.exp : null
  } catch {
    return null
  }
}

/**
 * 判斷憑證是否已失效。
 *
 * 無 token、格式不正確、缺少 exp，或已超過 exp（含時鐘偏移寬容）皆視為失效。
 */
export function isTokenExpired(token: string | null = getToken()): boolean {
  if (!token) return true
  const exp = readExpiry(token)
  if (exp === null) return true
  return Date.now() / 1000 > exp + CLOCK_SKEW_LEEWAY_SECONDS
}

/**
 * 憑證已失效時清除它，並回報是否失效。
 *
 * 供路由守衛與 store 初始化使用：不必等後端回 401 就能發現過期憑證。
 */
export function discardTokenIfExpired(): boolean {
  if (!isTokenExpired()) return false
  clearToken()
  return true
}

/** 註冊收到 401 時要執行的處理（通常為清除 token 並導向登入）。 */
export function onUnauthorized(handler: () => void): void {
  unauthorizedHandler = handler
}

/** 由 HTTP 層在收到 401 時呼叫。 */
export function handleUnauthorized(): void {
  if (unauthorizedHandler) unauthorizedHandler()
}
