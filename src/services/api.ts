/**
 * Movera API Service
 *
 * 此檔案根據 openapi.json 自動產生，提供了與後端 API 互動的類型化函式。
 * 所有函式都已設定好端點、請求方法和資料結構。
 */

// 從環境變數讀取 API 的基本 URL，如果未設定則使用預設值
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// #endregion

// #region 通用 API 處理邏輯

/**
 * 處理 API 回應的通用函式。
 *
 * @param response - fetch 回應物件
 * @returns - 有內容則解析 JSON，無內容則回傳 void
 * @throws - 如果回應狀態不是 ok，則拋出錯誤
 */
function handleResponse(response: Response): Promise<void>;
function handleResponse<T>(response: Response): Promise<T>;
async function handleResponse<T>(response: Response): Promise<T | void> {
  if (!response.ok) {
    const errorData = await response
      .json()
      .catch(() => ({ message: response.statusText }));
    throw new Error(errorData.detail || errorData.message || '網路請求失敗');
  }

  // 204 No Content 或空本文
  if (response.status === 204) return;

  const text = await response.text();
  if (!text) return; // 無內容

  return JSON.parse(text) as T;
}

/**
 * 建立帶有通用標頭的 RequestInit 物件。
 *
 * @param method - HTTP 方法
 * @param data - 要傳送的資料（可選）
 * @returns - RequestInit 設定物件
 */
function createRequestOptions(method: string, data?: unknown): RequestInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const options: RequestInit = {
    method,
    headers,
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  return options;
}

/**
 * 執行 API 請求的通用函式。
 *
 * @param method - HTTP 方法
 * @param endpoint - API 端點路徑
 * @param data - 要傳送的資料（可選）
 * @returns - 解析後的回應資料（有內容）或 void（無內容）
 */
export async function request(method: string, endpoint: string, data?: unknown): Promise<void>;
export async function request<T>(method: string, endpoint: string, data?: unknown): Promise<T>;
export async function request<T>(method: string, endpoint: string, data?: unknown): Promise<T | void> {
  const options = createRequestOptions(method, data);
  const response = await fetch(`${BASE_URL}${endpoint}`, options);
  return handleResponse<T>(response);
}

// #endregion
