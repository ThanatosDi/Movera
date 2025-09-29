export const Route = {
  HOME: '/',
  CREATE_TASK: '/create',
  TASKS: '/tasks',
  TASK_DETAIL: (taskId: string) => `/task/${taskId}`,
  SETTING: '/setting',
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

export const RegexExamples = [
  {
    label: '動漫案例1', key: 'anime1',
    filename: '公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4',
    src_filename: '公爵千金的家庭教師 - (\\d{2})(v2)? .+\\.mp4',
    dst_filename: '公爵千金的家庭教師 - S01E\\1 [1080P][WEB-DL][AAC AVC][CHT].mp4'
  },
  {
    label: '動漫案例2', key: 'anime2',
    filename: '公爵千金的家庭教師 - 01v2 [1080P][WEB-DL][AAC AVC][CHT].mp4',
    src_filename: '(.+) - (\\d{2}).+\\.mp4',
    dst_filename: '\\1 - S01E\\2 [1080P][WEB-DL][AAC AVC][CHT].mp4'
  },
  {
    label: '動漫案例3', key: 'anime3',
    filename: '[Sakurato] Dan Da Dan (2025) [13][AVC-8bit 1080p AAC][CHT].mp4',
    src_filename: '.+ Dan Da Dan \\(2025\\) \\[(\\d{2})\\]\\[AVC-8bit 1080p AAC\\]\\[CHT\\]\\.mp4',
    dst_filename: '[Sakurato] Dan Da Dan (2025) [S02E\\1][AVC-8bit 1080p AAC][CHT].mp4'
  },
  {
    label: '電影案例', key: 'movie',
    filename: 'Movie.Title.2024.1080p.BluRay.x264-GROUP.mkv',
    src_filename: '(.+)\\.(\\d{4})\\.1080p\\.BluRay\\.x264-(.+)\\.mkv',
    dst_filename: '\\1 (\\2) [1080p BluRay x264-\\3].mkv'
  },
]

export const ParseExamples = [
  {
    label: '動漫案例1', key: 'anime1',
    filename: '公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4',
    src_filename: '{title} - {episode} {tags}.mp4',
    dst_filename: '{title} - S01E{episode} {tags}.mp4'
  },
  {
    label: '電影案例', key: 'movie',
    filename: 'Movie.Title.2024.1080p.BluRay.x264-GROUP.mkv',
    src_filename: '{title:11}.{year}.{resolution}.BluRay.{codec}-GROUP.mkv',
    dst_filename: '{title} ({year}) [{resolution}][{codec}].mkv'
  }
]


export const Locales = [
  { value: 'en-US', label: 'English' },
  { value: 'zh-TW', label: '繁體中文' },
]