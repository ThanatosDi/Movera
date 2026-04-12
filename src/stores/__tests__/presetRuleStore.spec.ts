/**
 * PresetRuleStore 單元測試
 */

import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { usePresetRuleStore } from '../presetRuleStore'
import type { PresetRule } from '@/schemas'

const mockRequest = vi.fn()
vi.mock('@/composables/useHttpService', () => ({
  request: (...args: any[]) => mockRequest(...args),
}))

const sampleRule: PresetRule = {
  id: 'rule-1',
  name: '動畫季番命名',
  rule_type: 'parse',
  field_type: 'src',
  pattern: '{title} - {episode}.mp4',
  created_at: '2024-01-01T00:00:00Z',
}

const sampleRule2: PresetRule = {
  id: 'rule-2',
  name: '電影字幕重命名',
  rule_type: 'regex',
  field_type: 'dst',
  pattern: '\\1 - S01E\\2.mp4',
  created_at: '2024-01-02T00:00:00Z',
}

describe('PresetRuleStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('fetchPresetRules', () => {
    it('應該成功獲取所有常用規則', async () => {
      const store = usePresetRuleStore()
      mockRequest.mockResolvedValueOnce([sampleRule, sampleRule2])

      await store.fetchPresetRules()

      expect(store.presetRules).toHaveLength(2)
      expect(mockRequest).toHaveBeenCalledWith('GET', '/api/v1/preset-rules')
    })

    it('應該支援 rule_type 和 field_type 篩選', async () => {
      const store = usePresetRuleStore()
      mockRequest.mockResolvedValueOnce([sampleRule])

      await store.fetchPresetRules({ rule_type: 'parse', field_type: 'src' })

      expect(mockRequest).toHaveBeenCalledWith('GET', '/api/v1/preset-rules?rule_type=parse&field_type=src')
    })
  })

  describe('createPresetRule', () => {
    it('應該成功建立常用規則', async () => {
      const store = usePresetRuleStore()
      mockRequest.mockResolvedValueOnce(sampleRule)

      const result = await store.createPresetRule({
        name: '動畫季番命名',
        rule_type: 'parse',
        field_type: 'src',
        pattern: '{title} - {episode}.mp4',
      })

      expect(result).toEqual(sampleRule)
      expect(store.presetRules).toHaveLength(1)
    })
  })

  describe('updatePresetRule', () => {
    it('應該成功更新常用規則', async () => {
      const store = usePresetRuleStore()
      store.presetRules = [{ ...sampleRule }]
      const updated = { ...sampleRule, name: '新名稱' }
      mockRequest.mockResolvedValueOnce(updated)

      const result = await store.updatePresetRule(sampleRule.id, {
        name: '新名稱',
        rule_type: 'parse',
        field_type: 'src',
        pattern: sampleRule.pattern,
      })

      expect(result.name).toBe('新名稱')
      expect(store.presetRules[0]!.name).toBe('新名稱')
    })
  })

  describe('deletePresetRule', () => {
    it('應該成功刪除常用規則', async () => {
      const store = usePresetRuleStore()
      store.presetRules = [{ ...sampleRule }]
      mockRequest.mockResolvedValueOnce(undefined)

      await store.deletePresetRule(sampleRule.id)

      expect(store.presetRules).toHaveLength(0)
    })
  })
})
