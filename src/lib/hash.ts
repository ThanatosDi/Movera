/**
 * 前端密碼雜湊工具。
 *
 * 密碼在 POST 至後端前先以 SHA-256 雜湊，避免明文密碼於網路傳輸。
 * 後端會再以每帳號 salt 進行雜湊後儲存。
 */

/** 對字串計算 SHA-256，回傳小寫 hex 字串。 */
export async function sha256Hex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text)
  const digest = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}
