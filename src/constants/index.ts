export const Route = {
  HOME: '/',
  CREATE_TASK: '/create',
  TASK_DETAIL: (taskId: string) => `/task/${taskId}`,
  SETTINGS: '/settings',
}

export const APIRoute = {
  TASKS: '/api/v1/tasks',
  CREATE_TASK: '/api/v1/task',
  UPDATE_TASK: (taskId: string) => `/api/v1/task/${taskId}`,
  DELETE_TASK: (taskId: string) => `/api/v1/task/${taskId}`,
  LOGS: '/api/v1/logs',
  HEALTH: '/health',
}

export const Messages = {
  TASK_CREATED: '任務創建成功！',
  TASK_UPDATED: '任務已成功儲存',
  TASK_DELETED: '任務已成功刪除',
  TASK_ERROR: '任務儲存失敗',
  NETWORK_ERROR: '網路連線錯誤',
  VALIDATION_ERROR: '表單驗證失敗',
  SAVE_ERROR: '儲存失敗',
  LOAD_ERROR: '載入失敗',
  DELETE_ERROR: '刪除失敗',
  REGEX_ERROR: '正規表達式格式無效',
}