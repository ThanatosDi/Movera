import { request } from '@/services/api';

// 定義請求的資料結構
export interface ParsePreviewPayload {
  src_pattern: string;
  text: string;
  dst_pattern: string;
}

// 定義預期的回應資料結構
export interface ParsePreviewResponse {
  groups: Record<string, any>;
  formatted: string;
}

// 建立 parsePreviewService 物件
export const parsePreviewService = {
  /**
   * 獲取 Parse 預覽結果
   * @param payload - 包含來源、目標模式和測試文字的資料
   * @returns - 包含解析群組和格式化結果的 Promise
   */
  getPreview(payload: ParsePreviewPayload): Promise<ParsePreviewResponse> {
    return request<ParsePreviewResponse>('POST', '/api/v1/parse-preview', payload);
  },
};
