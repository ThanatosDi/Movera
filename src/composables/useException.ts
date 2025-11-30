import type { WebSocketError } from "../schemas/wsMessage";

function matchError(e: WebSocketError) {
  switch (e.error) {
    case 'TaskAlreadyExists':
      break
    case 'TaskNotFound':
      break
    case 'UnHandledWebSocketEvent':
      break
    case 'PayloadValidationError':
      break
  }
}

export const useException = {
  catchError(e: WebSocketError) {
    matchError(e)
  }
}