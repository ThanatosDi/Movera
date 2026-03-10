# Vue 前端設計規範

## 1. 專案結構

```
src/
├── main.ts                    # 應用程式入口
├── App.vue                    # 根元件
├── components/                # 可重用元件
│   ├── ui/                    # UI 基礎元件 (shadcn-vue)
│   │   ├── button/
│   │   ├── card/
│   │   ├── dialog/
│   │   └── ...
│   ├── ParsePreview.vue       # Parse 預覽元件
│   ├── RegexPreview.vue       # Regex 預覽元件
│   ├── TaskForm.vue           # 任務表單元件
│   └── ...
├── composables/               # 組合式函式
│   ├── useWebSocketService.ts # WebSocket 服務
│   ├── useHttpService.ts      # HTTP 請求服務
│   ├── useNotification.ts     # 通知服務
│   ├── useException.ts        # 錯誤處理
│   ├── usePreview.ts          # 預覽共用邏輯
│   ├── useParsePreview.ts     # Parse 預覽邏輯
│   └── useRegexPreview.ts     # Regex 預覽邏輯
├── stores/                    # Pinia 狀態管理
│   ├── taskStore.ts           # 任務狀態
│   └── settingStore.ts        # 設定狀態
├── views/                     # 頁面元件
│   ├── HomeView.vue
│   ├── CreateTaskView.vue
│   ├── TaskDetailView.vue
│   ├── TasksListView.vue
│   └── SettingView.vue
├── schemas/                   # TypeScript 類型定義
│   ├── index.ts
│   ├── task.ts
│   ├── log.ts
│   ├── settings.ts
│   └── wsMessage.ts
├── enums/                     # 列舉定義
│   └── wsEventsEnum.ts
├── locales/                   # 國際化
│   ├── zh-TW.json
│   └── en.json
└── router/                    # Vue Router 配置
    └── index.ts
```

## 2. 架構模式

### 2.1 元件分層

```
┌─────────────────────────────────────┐
│  Views (頁面元件)                    │  ← 路由對應的頁面
├─────────────────────────────────────┤
│  Components (功能元件)               │  ← 可重用的功能元件
├─────────────────────────────────────┤
│  UI Components (UI 元件)            │  ← shadcn-vue 基礎元件
├─────────────────────────────────────┤
│  Composables (組合式函式)            │  ← 可重用的邏輯
├─────────────────────────────────────┤
│  Stores (Pinia 狀態)                │  ← 全域狀態管理
└─────────────────────────────────────┘
```

### 2.2 Composable 設計模式
使用工廠函式和泛型實現可重用邏輯：

```typescript
// usePreview.ts - 通用預覽邏輯
export interface PreviewConfig<TGroups, TResponse> {
  storageKey: string
  wsEvent: wsEventsEnum
  extractGroups: (response: TResponse) => TGroups
  extractResult: (response: TResponse) => string
}

export function usePreview<TGroups, TResponse>(
  srcFilename: Ref<string | null>,
  dstFilename: Ref<string | null>,
  config: PreviewConfig<TGroups, TResponse>
) {
  // 共用狀態和邏輯
  const testFilename = useSessionStorage(config.storageKey, '')
  const groups = ref<TGroups | null>(null)
  const result = ref<string>('')

  // 共用 watch 和 debounce 邏輯
  watchDebounced([testFilename, srcFilename, dstFilename], async () => {
    // 執行預覽
  }, { debounce: 300 })

  return { testFilename, groups, result, isMatch, errorMessage }
}
```

### 2.3 Store 設計模式

```typescript
export const useTaskStore = defineStore('taskStore', () => {
  // 狀態
  const tasks = ref<Task[]>([])
  const error = ref<string | null>(null)

  // Getters (computed)
  const enabledTasks = computed(() => tasks.value.filter(t => t.enabled))

  // Actions
  async function fetchTasks() {
    error.value = null
    try {
      const response = await wsService.request<Task[]>(wsEventsEnum.getTasks)
      tasks.value = response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  return { tasks, error, enabledTasks, fetchTasks }
})
```

## 3. 命名規範

### 3.1 檔案命名
- **元件**: `PascalCase.vue` (例: `TaskForm.vue`, `ParsePreview.vue`)
- **Composables**: `useCamelCase.ts` (例: `useWebSocketService.ts`)
- **Stores**: `camelCaseStore.ts` (例: `taskStore.ts`)
- **Types/Schemas**: `camelCase.ts` (例: `task.ts`, `wsMessage.ts`)
- **Enums**: `camelCaseEnum.ts` (例: `wsEventsEnum.ts`)

### 3.2 元件命名規範
- 使用 PascalCase
- 名稱應描述元件用途
- 基礎元件放在 `ui/` 目錄

```vue
<!-- 正確 -->
<TaskForm />
<ParsePreview />
<RegexPreview />

<!-- 避免 -->
<task-form />
<Form />
```

### 3.3 Composable 命名規範
- 以 `use` 前綴開頭
- 使用 camelCase
- 名稱描述功能

```typescript
// 正確
useWebSocketService()
useNotification()
useException()

// 避免
webSocketService()
notification()
```

### 3.4 變數與函式命名
- **ref/reactive**: `camelCase`
- **computed**: `camelCase`
- **函式**: `camelCase`，動詞開頭
- **常數**: `UPPER_SNAKE_CASE`
- **介面/類型**: `PascalCase`

```typescript
// 變數
const tasks = ref<Task[]>([])
const isLoading = ref(false)

// 函式
async function fetchTasks() { ... }
function handleSubmit() { ... }

// 常數
const ERROR_I18N_KEYS: Record<string, string> = { ... }

// 介面
interface TaskCreate { ... }
interface WebSocketMessage<T> { ... }
```

## 4. TypeScript 規範

### 4.1 類型定義

```typescript
// schemas/task.ts
export interface Task {
  id: string
  name: string
  include: string
  move_to: string
  rename_rule: 'regex' | 'parse' | null
  src_filename: string | null
  dst_filename: string | null
  enabled: boolean
  created_at: string
  logs?: Log[]
}

export interface TaskCreate extends Omit<Task, 'id' | 'created_at' | 'logs'> {}
export interface TaskUpdate extends Partial<TaskCreate> {}
```

### 4.2 泛型使用

```typescript
// WebSocket 訊息泛型
export interface WebSocketMessage<T = any> {
  event: string
  payload: T | WebSocketError
  timestamp: number
  requestId?: string
  success?: boolean
}

// Composable 泛型
export function usePreview<TGroups, TResponse>(
  srcFilename: Ref<string | null>,
  dstFilename: Ref<string | null>,
  config: PreviewConfig<TGroups, TResponse>
)
```

### 4.3 錯誤處理類型

```typescript
// 避免 any
} catch (e: unknown) {
  const errorMessage = e instanceof Error ? e.message : 'Unknown error'
  error.value = errorMessage
  throw e
}

// WebSocket 錯誤類型
interface WebSocketError {
  error: string    // 錯誤類型識別碼
  message: string  // 人類可讀訊息
}
```

## 5. 元件設計規範

### 5.1 Script Setup 結構順序

```vue
<script setup lang="ts">
// 1. 類型引入
import type { Task, TaskCreate } from '@/schemas'

// 2. 外部套件引入
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

// 3. 內部模組引入
import { useTaskStore } from '@/stores/taskStore'
import { useNotification } from '@/composables/useNotification'

// 4. 元件引入
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'

// 5. Props 定義
const props = defineProps<{
  taskId: string
}>()

// 6. Emits 定義
const emit = defineEmits<{
  (e: 'update', task: Task): void
}>()

// 7. Composables 使用
const { t } = useI18n()
const router = useRouter()
const taskStore = useTaskStore()

// 8. 響應式狀態
const isLoading = ref(false)
const task = ref<Task | null>(null)

// 9. Computed
const isValid = computed(() => ...)

// 10. 方法
async function handleSubmit() { ... }

// 11. 生命週期 / Watch
watch(() => props.taskId, fetchTask)
</script>
```

### 5.2 深拷貝規範
使用 `structuredClone` 配合 `toRaw` 處理響應式物件：

```typescript
import { toRaw } from 'vue'

// 正確：先轉換為原始物件再拷貝
task.value = structuredClone(toRaw(foundTask))

// 錯誤：直接拷貝響應式物件會報錯
task.value = structuredClone(foundTask)  // DataCloneError!

// 避免：效能較差
task.value = JSON.parse(JSON.stringify(foundTask))
```

### 5.3 v-model 雙向綁定

```vue
<!-- 父元件 -->
<TaskForm v-model="taskData" />

<!-- 或分離的 v-model -->
<RegexPreview
  v-model:src-filename="task.src_filename"
  v-model:dst-filename="task.dst_filename"
/>

<!-- 子元件 -->
<script setup lang="ts">
const srcFilename = defineModel<string | null>('srcFilename')
const dstFilename = defineModel<string | null>('dstFilename')
</script>
```

## 6. 狀態管理規範

### 6.1 Store 結構

```typescript
export const useTaskStore = defineStore('taskStore', () => {
  // ===== 狀態 =====
  const tasks = ref<Task[]>([])
  const error = ref<string | null>(null)
  const selectedTaskIds = ref<Set<string>>(new Set())

  // ===== Getters =====
  const enabledTasks = computed(() =>
    tasks.value.filter(t => t.enabled)
  )

  const getTaskById = (id: string) =>
    tasks.value.find(t => t.id === id)

  // ===== Actions =====
  async function fetchTasks() {
    error.value = null
    try {
      const response = await wsService.request<Task[]>(wsEventsEnum.getTasks)
      tasks.value = response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  // ===== 批量操作 =====
  async function batchSetEnabled(enabled: boolean) {
    const ids = Array.from(selectedTaskIds.value)
    for (const id of ids) {
      const task = getRefTaskById(id)
      if (task && task.enabled !== enabled) {
        await updateTask(id, { ...taskData, enabled })
      }
    }
  }

  return {
    // 狀態
    tasks, error, selectedTaskIds,
    // Getters
    enabledTasks, getTaskById,
    // Actions
    fetchTasks, createTask, updateTask, deleteTask,
    batchSetEnabled
  }
})
```

### 6.2 錯誤處理一致性
所有 async actions 統一設置 error：

```typescript
async function createTask(taskData: TaskCreate) {
  error.value = null  // 清除先前錯誤
  try {
    const response = await wsService.request<Task>(wsEventsEnum.createTask, taskData)
    tasks.value.push(response)
    return response
  } catch (e) {
    error.value = (e as Error).message  // 設置錯誤
    throw e  // 重新拋出供呼叫端處理
  }
}
```

## 7. 錯誤處理規範

### 7.1 useException Composable

```typescript
// composables/useException.ts
const ERROR_I18N_KEYS: Record<string, string> = {
  TaskAlreadyExists: 'exceptions.TaskAlreadyExists',
  TaskNotFound: 'errors.taskNotFound',
  UnHandledWebSocketEvent: 'errors.unhandledEvent',
  PayloadValidationError: 'errors.invalidPayload',
}

export function useException() {
  const { t, te } = useI18n()

  function getErrorMessage(error: WebSocketError, params?: Record<string, unknown>): string {
    const i18nKey = ERROR_I18N_KEYS[error.error]

    if (i18nKey && te(i18nKey)) {
      return t(i18nKey, params || {})
    }

    return error.message || error.error || 'Unknown error'
  }

  return { getErrorMessage, catchError }
}
```

### 7.2 View 層錯誤處理

```typescript
const btnActionCreateTask = async () => {
  isSaving.value = true
  try {
    const response = await tasksStore.createTask(createTaskData.value)
    router.push({ name: 'taskDetail', params: { taskId: response.id } })
    useNotification.showSuccess(
      t('notifications.taskCreateSuccessTitle'),
      t('notifications.taskCreateSuccessDesc', { taskName: response.name })
    )
  } catch (e: unknown) {
    const wsError = e as { error?: string; message?: string }
    if (wsError.error === 'TaskAlreadyExists') {
      error_message.value = t('exceptions.TaskAlreadyExists', {
        taskName: createTaskData.value.name
      })
    } else {
      error_message.value = wsError.message || (e as Error).message || 'Unknown error'
    }
    useNotification.showError(t('notifications.taskCreateErrorTitle'), error_message.value)
  } finally {
    isSaving.value = false
  }
}
```

## 8. 測試規範

### 8.1 測試檔案結構

```
src/
├── components/
│   └── __tests__/
│       └── TaskForm.spec.ts
├── composables/
│   └── __tests__/
│       ├── usePreview.spec.ts
│       └── useException.spec.ts
├── stores/
│   └── __tests__/
│       ├── taskStore.spec.ts
│       └── settingStore.spec.ts
└── views/
    └── __tests__/
        └── TaskDetailView.spec.ts
```

### 8.2 測試命名規範

```typescript
describe('TaskStore', () => {
  describe('fetchTasks', () => {
    it('should fetch all tasks from WebSocket', async () => { ... })
    it('should set error when request fails', async () => { ... })
  })

  describe('createTask', () => {
    it('should create task and add to list', async () => { ... })
    it('should throw TaskAlreadyExists for duplicate name', async () => { ... })
  })
})
```

---

*文件版本: 1.0*
*最後更新: 2026-01-19*
