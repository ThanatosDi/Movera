export const wsEventsEnum = {
  // 系統狀態事件
  status: 'system:status',
  ping: 'system:ping',
  // 任務事件
  getTasks: 'get:tasks',
  getTask: 'get:task',
  createTask: 'create:task',
  deleteTask: 'delete:task',
  updateTask: 'update:task',
  statsTasks: 'stats:tasks',
  // 日誌事件
  getLogs: 'get:logs',
  // 設定事件
  getSettings: 'get:settings',
  getSetting: 'get:setting',
  updateSetting: 'update:settings',
  // 預覽事件
  previewParse: 'preview:parse',
} as const;

export type wsEventsEnum = typeof wsEventsEnum[keyof typeof wsEventsEnum];