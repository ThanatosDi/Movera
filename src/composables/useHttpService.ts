/**
 * Movera API Service
 *
 * 此檔案根據 openapi.json 自動產生，提供了與後端 API 互動的類型化函式。
 * 所有函式都已設定好端點、請求方法和資料結構。
 */

import { ApiError } from '@/schemas/errors'
import type { ApiErrorDetail } from '@/schemas/errors'
import { getToken, handleUnauthorized } from '@/composables/useAuthToken'
import {
  isGatewayBlockPage,
  isGatewayIntercepting,
  reloadForGateway,
} from '@/composables/useAuthGateway'

// 從環境變數讀取 API 的基本 URL，如果未設定則使用預設值
const BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin;

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
    // 收到 401 時清除 token 並導向登入（由 useAuthToken 註冊的處理執行）
    if (response.status === 401) {
      handleUnauthorized();
    }
    // 反向代理 SSO 的阻擋頁：需以整頁重載交還閘道處理
    if (isGatewayBlockPage(response)) {
      reloadForGateway();
    }
    const errorData: ApiErrorDetail = await response
      .json()
      .catch(() => ({ message: response.statusText }));
    throw new ApiError(response.status, errorData);
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
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // 若已登入則附帶 JWT 存取憑證
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

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

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${endpoint}`, options);
  } catch (error) {
    // fetch 在網路層失敗時讀不到狀態碼。被反向代理 302 到跨來源 SSO 而遭 CORS
    // 擋下也是這個路徑，需另行探測才能與單純離線區分。
    if (await isGatewayIntercepting(BASE_URL)) {
      reloadForGateway();
    }
    throw error;
  }

  return handleResponse<T>(response);
}

// #endregion
