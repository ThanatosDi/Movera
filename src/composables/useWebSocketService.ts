import type { Events, WebSocketMessage } from '@/schemas/wsMessage'
import { useWebSocket } from '@vueuse/core'
import mitt from 'mitt'
import { v4 as uuidv4 } from 'uuid'
import { watch } from 'vue'

// --- 核心邏輯 ---

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const wsUrl = import.meta.env.VITE_WEBSOCKET_BASE_URL || `${wsProtocol}//${window.location.host}/ws`

// 待處理的請求映射表
const pendingRequests = new Map<string, { resolve: (value: any) => void; reject: (reason?: any) => void }>()
// 事件總線，用於處理伺服器主動推送的訊息
const eventBus = mitt<Events>()

const {
  status,
  data: rawData,
  send: rawSend,
  open,
  close
} = useWebSocket(wsUrl, {
  autoReconnect: { retries: 3, delay: 1000 },
  // heartbeat: {
  //   message: () => JSON.stringify({ event: 'system:ping', payload: {}, timestamp: Date.now() }),
  //   interval: 5000
  // }
})

// 監聽所有傳入的訊息
watch(rawData, (newRawData) => {
  if (!newRawData || typeof newRawData !== 'string') return

  try {
    const message = JSON.parse(newRawData) as WebSocketMessage

    // 如果訊息包含 requestId，則是對某個請求的回應
    if (message.requestId && pendingRequests.has(message.requestId)) {
      const promise = pendingRequests.get(message.requestId)!
      // 根據後端的回應決定是 resolve 還是 reject
      if (message.event.startsWith('error:') || (message.payload && message.success === false)) {
        promise.reject(message.payload)
      } else {
        promise.resolve(message.payload)
      }
      pendingRequests.delete(message.requestId)
    } else {
      // 否則，是伺服器主動推送的事件，透過事件總線發布
      eventBus.emit(message.event, message.payload)
    }
  } catch (error) {
    console.error('[WebSocket] Failed to parse or handle message:', error)
  }
})

/**
 * 向後端發送一個請求，並等待回應。
 * @param event 事件名稱
 * @param payload 資料負載
 * @param timeout 超時時間 (ms)
 * @returns Promise<T> 回應的 payload
 */
async function request<T = any>(event: string, payload: any = {}, timeout = 10000): Promise<T> {
  if (status.value !== 'OPEN') {
    return Promise.reject(new Error('WebSocket connection is not open.'))
  }

  const requestId = uuidv4()

  return new Promise((resolve, reject) => {
    pendingRequests.set(requestId, { resolve, reject })

    const messageToSend: WebSocketMessage = {
      event,
      payload,
      timestamp: Date.now(),
      requestId
    }
    rawSend(JSON.stringify(messageToSend))

    // 設定超時處理
    setTimeout(() => {
      if (pendingRequests.has(requestId)) {
        pendingRequests.delete(requestId)
        reject(new Error(`Request timed out for event: ${event}`))
      }
    }, timeout)
  })
}

// --- 匯出的服務 ---

/**
 * 確保 WebSocket 已連線
 * @param timeout 超時時間 (ms)
 * @returns
 */
function ensureConnected(timeout = 10000): Promise<void> {
  if (status.value === 'OPEN') {
    return Promise.resolve()
  }

  return new Promise((resolve, reject) => {
    const timeoutTimer = setTimeout(() => {
      unwatch()
      reject(new Error('WebSocket connection timed out.'))
    }, timeout)

    const unwatch = watch(status, (newStatus) => {
      if (newStatus === 'OPEN') {
        clearTimeout(timeoutTimer)
        unwatch()
        resolve()
      } else if (newStatus === 'CLOSED') {
        clearTimeout(timeoutTimer)
        unwatch()
        reject(new Error('WebSocket connection failed to open.'))
      }
    }, { immediate: true }) // immediate: true 確保即使狀態已經是 OPEN 或 CLOSED 也能立即觸發
  })
}


export function useWebSocketService() {
  return {
    status,
    request, // 新的請求-回應函式
    on: eventBus.on, // 監聽伺服器推送事件
    off: eventBus.off, // 取消監聽
    open,
    close,
    ensureConnected, // 新增的函式
  }
}
