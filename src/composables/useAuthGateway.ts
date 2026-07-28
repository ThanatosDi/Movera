/**
 * 反向代理 SSO 閘道攔截的偵測與處理。
 *
 * Why: 當 Movera 部署在帶 SSO 的反向代理之後（Pangolin、Cloudflare Zero Trust 等），
 * 閘道 session 過期後會把 /api/* 請求 302 到另一個來源的登入頁。瀏覽器因跨來源
 * 而以 CORS 擋下該回應，fetch 是以 TypeError 失敗而非回傳 401，因此既有的 401
 * 處理永遠不會觸發，使用者會停留在畫面上、看到空資料而不被導向登入頁。
 *
 * 閘道的重新認證必須經由 top-level 導覽才能顯示 IdP 頁面，所以偵測到攔截時
 * 以整頁重載把控制權交還閘道。
 */

/**
 * 探測用端點。
 *
 * 選用後端公開端點（不需 JWT），且 workbox 對 /api/ 採 NetworkOnly，
 * 探測不會被 service worker 快取遮蔽而誤判。
 */
const PROBE_ENDPOINT = '/api/v1/auth/status'

/** 重載節流：閘道未攔截導覽時避免陷入無限重載。 */
const RELOAD_GUARD_KEY = 'movera_gateway_reload_at'
const RELOAD_GUARD_MS = 30_000

/**
 * 探測請求是否被閘道攔截。
 *
 * 以 redirect: 'manual' 發出探測：被 302 到其他來源時會得到 opaqueredirect
 * （status 0）而不觸發 CORS 錯誤；閘道正常放行時則得到可讀取的回應。
 *
 * 僅用於探測，一般 API 請求維持預設的 redirect: 'follow' —— 全域改成 manual
 * 會讓同源的 307/308（例如 FastAPI 的 trailing slash 轉址）也變成
 * opaqueredirect 而被誤判為閘道攔截。
 */
export async function isGatewayIntercepting(baseUrl: string): Promise<boolean> {
  try {
    const response = await fetch(`${baseUrl}${PROBE_ENDPOINT}`, {
      method: 'GET',
      cache: 'no-store',
      redirect: 'manual',
    })
    return response.type === 'opaqueredirect'
  } catch {
    // 探測本身也失敗：離線或後端不可用，並非閘道攔截。
    return false
  }
}

/**
 * 判斷回應是否為閘道的阻擋頁。
 *
 * 部分閘道（如某些 Cloudflare Access 設定）不回 302 而是直接回 403 加上 HTML
 * 阻擋頁。這是真實回應，會走到一般錯誤處理，但因為不是 401 而不會清除憑證，
 * 症狀與被 302 攔截相同，故一併視為需要重新認證。
 */
export function isGatewayBlockPage(response: Response): boolean {
  if (response.status !== 403) return false
  const contentType = response.headers.get('Content-Type') ?? ''
  return !contentType.includes('json')
}

/**
 * 以整頁重載把重新認證交還閘道處理。
 *
 * @returns 是否實際觸發重載（受節流限制時為 false）。
 */
export function reloadForGateway(): boolean {
  const last = Number(sessionStorage.getItem(RELOAD_GUARD_KEY) ?? '0')
  const now = Date.now()
  if (Number.isFinite(last) && now - last < RELOAD_GUARD_MS) return false

  sessionStorage.setItem(RELOAD_GUARD_KEY, String(now))
  window.location.reload()
  return true
}
