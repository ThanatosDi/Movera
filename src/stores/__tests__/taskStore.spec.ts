/**
 * TaskStore 單元測試
 */

import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useTaskStore } from '../taskStore'
import type { Task } from '@/schemas'

// Mock useWebSocketService
const mockRequest = vi.fn()
vi.mock('@/composables/useWebSocketService', () => ({
  useWebSocketService: () => ({
    request: mockRequest,
    status: { value: 'OPEN' },
    on: vi.fn(),
    off: vi.fn(),
  }),
}))

// 範例任務資料
const sampleTask: Task = {
  id: 'task-1',
  name: '測試任務',
  include: '關鍵字',
  move_to: '/downloads/test',
  src_filename: null,
  dst_filename: null,
  rename_rule: null,
  enabled: true,
  created_at: '2024-01-01T00:00:00Z',
  logs: [],
}

const sampleTask2: Task = {
  id: 'task-2',
  name: '第二個任務',
  include: '另一個關鍵字',
  move_to: '/downloads/anime',
  src_filename: null,
  dst_filename: null,
  rename_rule: null,
  enabled: false,
  created_at: '2024-01-02T00:00:00Z',
  logs: [],
}

describe('TaskStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('初始狀態', () => {
    it('應該有正確的初始狀態', () => {
      const store = useTaskStore()

      expect(store.tasks).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.isSaving).toBe(false)
      expect(store.error).toBeNull()
      expect(store.isSelectMode).toBe(false)
      expect(store.selectedTaskIds.size).toBe(0)
    })
  })

  describe('fetchTasks', () => {
    it('應該成功獲取任務列表', async () => {
      const store = useTaskStore()
      mockRequest.mockResolvedValueOnce([sampleTask, sampleTask2])

      await store.fetchTasks()

      expect(store.tasks).toHaveLength(2)
      expect(store.tasks[0].name).toBe('測試任務')
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('應該在加載時設置 isLoading', async () => {
      const store = useTaskStore()
      mockRequest.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve([]), 100)))

      const promise = store.fetchTasks()
      expect(store.isLoading).toBe(true)

      await promise
      expect(store.isLoading).toBe(false)
    })

    it('應該在錯誤時設置 error', async () => {
      const store = useTaskStore()
      mockRequest.mockRejectedValueOnce(new Error('網路錯誤'))

      await expect(store.fetchTasks()).rejects.toThrow('網路錯誤')
      expect(store.error).toBe('網路錯誤')
      expect(store.isLoading).toBe(false)
    })
  })

  describe('createTask', () => {
    it('應該成功建立任務並加入列表', async () => {
      const store = useTaskStore()
      mockRequest.mockResolvedValueOnce(sampleTask)

      const taskData = {
        name: '測試任務',
        include: '關鍵字',
        move_to: '/downloads/test',
      }
      const result = await store.createTask(taskData)

      expect(result).toEqual(sampleTask)
      expect(store.tasks).toHaveLength(1)
      expect(store.tasks[0].name).toBe('測試任務')
    })

    it('應該在錯誤時拋出異常', async () => {
      const store = useTaskStore()
      mockRequest.mockRejectedValueOnce(new Error('任務已存在'))

      await expect(store.createTask({ name: '測試', include: '', move_to: '' }))
        .rejects.toThrow('任務已存在')
    })
  })

  describe('updateTask', () => {
    it('應該成功更新任務', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }]

      const updatedTask = { ...sampleTask, name: '更新後的名稱' }
      mockRequest.mockResolvedValueOnce(updatedTask)

      const result = await store.updateTask(sampleTask.id, {
        name: '更新後的名稱',
        include: sampleTask.include,
        move_to: sampleTask.move_to,
      })

      expect(result.name).toBe('更新後的名稱')
      expect(store.tasks[0].name).toBe('更新後的名稱')
    })

    it('應該在任務不存在時拋出錯誤', async () => {
      const store = useTaskStore()
      store.tasks = []

      await expect(store.updateTask('non-existent', {
        name: '任何',
        include: '',
        move_to: '',
      })).rejects.toThrow('task not found')
    })

    it('應該在更新時設置 isSaving', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }]
      mockRequest.mockImplementation(() => new Promise(resolve =>
        setTimeout(() => resolve(sampleTask), 100)
      ))

      const promise = store.updateTask(sampleTask.id, {
        name: sampleTask.name,
        include: sampleTask.include,
        move_to: sampleTask.move_to,
      })
      expect(store.isSaving).toBe(true)

      await promise
      expect(store.isSaving).toBe(false)
    })
  })

  describe('deleteTask', () => {
    it('應該成功刪除任務', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }]
      mockRequest.mockResolvedValueOnce(undefined)

      await store.deleteTask(sampleTask.id)

      expect(store.tasks).toHaveLength(0)
    })

    it('應該從選中列表中移除已刪除的任務', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }]
      store.selectedTaskIds = new Set([sampleTask.id])
      mockRequest.mockResolvedValueOnce(undefined)

      await store.deleteTask(sampleTask.id)

      expect(store.selectedTaskIds.has(sampleTask.id)).toBe(false)
    })

    it('空 taskId 不應該執行刪除', async () => {
      const store = useTaskStore()

      await store.deleteTask('')

      expect(mockRequest).not.toHaveBeenCalled()
    })
  })

  describe('computed 屬性', () => {
    it('enabledTaskCount 應該正確計算', () => {
      const store = useTaskStore()
      store.tasks = [sampleTask, sampleTask2]

      expect(store.enabledTaskCount).toBe(1)
    })

    it('disabledTaskCount 應該正確計算', () => {
      const store = useTaskStore()
      store.tasks = [sampleTask, sampleTask2]

      expect(store.disabledTaskCount).toBe(1)
    })
  })

  describe('getRefTaskById', () => {
    it('應該回傳正確的任務', () => {
      const store = useTaskStore()
      store.tasks = [sampleTask, sampleTask2]

      const task = store.getRefTaskById(sampleTask.id)

      expect(task).toEqual(sampleTask)
    })

    it('找不到任務時應該回傳 null', () => {
      const store = useTaskStore()
      store.tasks = [sampleTask]

      const task = store.getRefTaskById('non-existent')

      expect(task).toBeNull()
    })
  })

  describe('選擇模式', () => {
    it('toggleSelectMode 應該切換選擇模式', () => {
      const store = useTaskStore()

      store.toggleSelectMode()
      expect(store.isSelectMode).toBe(true)

      store.toggleSelectMode()
      expect(store.isSelectMode).toBe(false)
    })

    it('關閉選擇模式時應該清空選中列表', () => {
      const store = useTaskStore()
      store.isSelectMode = true
      store.selectedTaskIds = new Set(['task-1', 'task-2'])

      store.toggleSelectMode()

      expect(store.selectedTaskIds.size).toBe(0)
    })

    it('toggleTaskSelection 應該切換任務選中狀態', () => {
      const store = useTaskStore()

      store.toggleTaskSelection('task-1')
      expect(store.selectedTaskIds.has('task-1')).toBe(true)

      store.toggleTaskSelection('task-1')
      expect(store.selectedTaskIds.has('task-1')).toBe(false)
    })

    it('selectAllTasks 應該選中所有任務', () => {
      const store = useTaskStore()
      store.tasks = [sampleTask, sampleTask2]

      store.selectAllTasks()

      expect(store.selectedTaskIds.size).toBe(2)
    })

    it('selectAllTasks 如果全選則取消全選', () => {
      const store = useTaskStore()
      store.tasks = [sampleTask, sampleTask2]
      store.selectedTaskIds = new Set([sampleTask.id, sampleTask2.id])

      store.selectAllTasks()

      expect(store.selectedTaskIds.size).toBe(0)
    })

    it('isTaskSelected 應該正確判斷', () => {
      const store = useTaskStore()
      store.selectedTaskIds = new Set(['task-1'])

      expect(store.isTaskSelected('task-1')).toBe(true)
      expect(store.isTaskSelected('task-2')).toBe(false)
    })

    it('selectedCount 應該正確計算', () => {
      const store = useTaskStore()
      store.selectedTaskIds = new Set(['task-1', 'task-2'])

      expect(store.selectedCount).toBe(2)
    })
  })

  describe('批量操作', () => {
    it('batchDelete 應該刪除所有選中的任務', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }, { ...sampleTask2 }]
      store.selectedTaskIds = new Set([sampleTask.id, sampleTask2.id])
      mockRequest.mockResolvedValue(undefined)

      await store.batchDelete()

      expect(store.tasks).toHaveLength(0)
      expect(store.selectedTaskIds.size).toBe(0)
    })

    it('batchEnable 應該啟用所有選中的停用任務', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask2 }] // sampleTask2.enabled = false
      store.selectedTaskIds = new Set([sampleTask2.id])

      const enabledTask = { ...sampleTask2, enabled: true }
      mockRequest.mockResolvedValueOnce(enabledTask)

      await store.batchEnable()

      expect(mockRequest).toHaveBeenCalled()
    })

    it('batchDisable 應該停用所有選中的啟用任務', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }] // sampleTask.enabled = true
      store.selectedTaskIds = new Set([sampleTask.id])

      const disabledTask = { ...sampleTask, enabled: false }
      mockRequest.mockResolvedValueOnce(disabledTask)

      await store.batchDisable()

      expect(mockRequest).toHaveBeenCalled()
    })
  })

  describe('fetchTaskLogByTaskId', () => {
    it('應該成功獲取任務日誌', async () => {
      const store = useTaskStore()
      store.tasks = [{ ...sampleTask }]

      const logs = [
        { id: 1, task_id: sampleTask.id, level: 'INFO', message: '測試', timestamp: '2024-01-01' }
      ]
      mockRequest.mockResolvedValueOnce(logs)

      const result = await store.fetchTaskLogByTaskId(sampleTask.id)

      expect(result).toEqual(logs)
      expect(store.tasks[0].logs).toEqual(logs)
    })
  })
})
