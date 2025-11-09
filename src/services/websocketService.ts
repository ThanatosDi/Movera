import { useWebSocket } from '@vueuse/core'

// 請將 'ws://localhost:8080' 換成您實際的 WebSocket 伺服器 URL
const { status, data, send, open, close } = useWebSocket('ws://localhost:8080/ws', {
  autoReconnect: {
    retries: 3,
    delay: 1000,
    onFailed() {
      console.error('WebSocket connection failed. Please check the server status.')
    },
  }
})

// 匯出單例的 WebSocket 狀態和控制函式
export function WebSocketService() {
  return {
    status,
    data,
    send,
    open,
    close,
  }
}
