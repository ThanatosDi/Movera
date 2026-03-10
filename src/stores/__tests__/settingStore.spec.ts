/**
 * SettingStore 單元測試
 */

import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Settings } from '@/schemas'

// Mock functions - 使用 hoisted 變數
const mockRequest = vi.hoisted(() => vi.fn())

// Mock useHttpService
vi.mock('@/composables/useHttpService', () => ({
  request: (...args: any[]) => mockRequest(...args),
}))

// 範例設定資料
const sampleSettings: Settings = {
  timezone: 'Asia/Taipei',
  locale: 'zh-TW',
}

describe('SettingStore', () => {
  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('初始狀態', () => {
    it('應該有正確的初始狀態', async () => {
      const { useSettingStore } = await import('../settingStore')
      const store = useSettingStore()

      expect(store.isSaving).toBe(false)
      expect(store.error).toBeNull()
      // settings 應該有預設值
      expect(store.settings.timezone).toBeDefined()
      expect(store.settings.locale).toBeDefined()
    })
  })

  describe('fetchSettings', () => {
    it('應該成功獲取設定', async () => {
      const { useSettingStore } = await import('../settingStore')
      const store = useSettingStore()
      mockRequest.mockResolvedValueOnce(sampleSettings)

      await store.fetchSettings()

      expect(store.settings.timezone).toBe('Asia/Taipei')
      expect(store.settings.locale).toBe('zh-TW')
    })

    it('應該在錯誤時拋出異常', async () => {
      const { useSettingStore } = await import('../settingStore')
      const store = useSettingStore()
      mockRequest.mockRejectedValueOnce(new Error('連線失敗'))

      await expect(store.fetchSettings()).rejects.toThrow('連線失敗')
    })

    it('應該合併設定而非完全覆蓋', async () => {
      const { useSettingStore } = await import('../settingStore')
      const store = useSettingStore()
      const originalLocale = store.settings.locale

      // 只回傳部分設定
      mockRequest.mockResolvedValueOnce({ timezone: 'UTC' })

      await store.fetchSettings()

      expect(store.settings.timezone).toBe('UTC')
      // 原本的 locale 應該保留
      expect(store.settings.locale).toBe(originalLocale)
    })
  })

  describe('updateSettings', () => {
    it('應該成功更新設定', async () => {
      const { useSettingStore } = await import('../settingStore')
      const store = useSettingStore()
      const updatedSettings = { timezone: 'UTC', locale: 'en-US' }
      mockRequest.mockResolvedValueOnce(updatedSettings)

      await store.updateSettings(updatedSettings)

      expect(store.settings.timezone).toBe('UTC')
      expect(store.settings.locale).toBe('en-US')
    })

    it('應該在錯誤時拋出異常', async () => {
      const { useSettingStore } = await import('../settingStore')
      const store = useSettingStore()
      mockRequest.mockRejectedValueOnce(new Error('更新失敗'))

      await expect(store.updateSettings({ timezone: 'UTC' })).rejects.toThrow('更新失敗')
    })
  })
})
