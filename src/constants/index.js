// API 相關常數
export const API_ENDPOINTS = {
  TASKS: '/tasks',
  TASK_BY_ID: (id) => `/task/${id}`,
  TASK_STATUS: '/tasks/status',
  LOGS: '/logs',
  LOG: '/log',
  TASK: '/task',
}

// 日誌等級常數
export const LOG_LEVELS = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
}

// 路由路徑常數
export const ROUTES = {
  HOME: '/',
  CREATE_TASK: '/create',
  TASK_DETAIL: (taskId) => `/services/${taskId}`,
  SETTINGS: '/settings',
}

// 表單驗證規則
export const VALIDATION_RULES = {
  TASK_NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 50,
    PATTERN: /^[a-zA-Z0-9\u4e00-\u9fa5_\-\s]+$/,
  },
  FILE_NAME_INCLUDE: {
    MAX_LENGTH: 100,
  },
  MOVE_TO: {
    MAX_LENGTH: 500,
    PATTERN: /^[^\<\>\:\"\|\?\*]+$/,
  },
}

// UI 相關常數
export const UI_CONSTANTS = {
  SIDEBAR_WIDTH: 'w-128',
  SCROLL_BAR_CLASS: 'custom-scrollbar',
  LOADING_TEXT: '載入中...',
  NO_DATA_TEXT: '沒有可用的資料',
}

// 正規表達式測試案例
export const REGEX_TEST_CASES = {
  anime1: {
    filename: '公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4',
    srcRegex: '公爵千金的家庭教師 - (\\d{2})(v2)? .+\\.mp4',
    dstRegex: '公爵千金的家庭教師 - S01E\\1 [1080P][WEB-DL][AAC AVC][CHT].mp4'
  },
  anime2: {
    filename: '公爵千金的家庭教師 - 01v2 [1080P][WEB-DL][AAC AVC][CHT].mp4',
    srcRegex: '(.+) - (\\d{2}).+\\.mp4',
    dstRegex: '\\1 - S01E\\2 [1080P][WEB-DL][AAC AVC][CHT].mp4'
  },
  anime3: {
    filename: '[Sakurato] Dan Da Dan (2025) [13][AVC-8bit 1080p AAC][CHT].mp4',
    srcRegex: '.+ Dan Da Dan \\(2025\\) \\[(\\d{2})\\]\\[AVC-8bit 1080p AAC\\]\\[CHT\\]\\.mp4',
    dstRegex: '[Sakurato] Dan Da Dan (2025) [S02E\\1][AVC-8bit 1080p AAC][CHT].mp4'
  },
  movie: {
    filename: 'Movie.Title.2024.1080p.BluRay.x264-GROUP.mkv',
    srcRegex: '(.+)\\.(\\d{4})\\.1080p\\.BluRay\\.x264-(.+)\\.mkv',
    dstRegex: '\\1 (\\2) [1080p BluRay x264-\\3].mkv'
  }
}

// 錯誤訊息
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '網路連線錯誤',
  VALIDATION_ERROR: '表單驗證失敗',
  SAVE_ERROR: '儲存失敗',
  LOAD_ERROR: '載入失敗',
  DELETE_ERROR: '刪除失敗',
  REGEX_ERROR: '正規表達式格式無效',
}

// 成功訊息
export const SUCCESS_MESSAGES = {
  TASK_CREATED: '任務創建成功！',
  TASK_UPDATED: '任務已成功儲存',
  TASK_DELETED: '任務已成功刪除',
}
