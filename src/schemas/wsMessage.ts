export interface WebSocketMessage<T = any> {
  event: string
  payload: T | WebSocketError
  timestamp: number
  requestId?: string // requestId 是可選的
  success?: boolean
}

export type Events = {
  [key: string]: any // 允許任何事件名稱和任何負載
}

export interface WebSocketError {
  error: string
  message: string
}