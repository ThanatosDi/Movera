import { request } from '@/composables/useHttpService'
import type { PresetRule, PresetRuleCreate, PresetRuleUpdate } from '@/schemas'
import { defineStore } from 'pinia'
import { ref } from 'vue'


export const usePresetRuleStore = defineStore('presetRuleStore', () => {
  const presetRules = ref<PresetRule[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  async function fetchPresetRules(params?: { rule_type?: string; field_type?: string }) {
    isLoading.value = true
    error.value = null
    try {
      const queryParams = new URLSearchParams()
      if (params?.rule_type) queryParams.set('rule_type', params.rule_type)
      if (params?.field_type) queryParams.set('field_type', params.field_type)
      const query = queryParams.toString()
      const url = `/api/v1/preset-rules${query ? `?${query}` : ''}`
      const response = await request<PresetRule[]>('GET', url)
      presetRules.value = response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createPresetRule(data: PresetRuleCreate): Promise<PresetRule> {
    error.value = null
    try {
      const response = await request<PresetRule>('POST', '/api/v1/preset-rules', data)
      presetRules.value.push(response)
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function updatePresetRule(id: string, data: PresetRuleUpdate): Promise<PresetRule> {
    error.value = null
    try {
      const response = await request<PresetRule>('PUT', `/api/v1/preset-rules/${id}`, data)
      const index = presetRules.value.findIndex(r => r.id === id)
      if (index !== -1) {
        presetRules.value[index] = response
      }
      return response
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  async function deletePresetRule(id: string) {
    error.value = null
    try {
      await request('DELETE', `/api/v1/preset-rules/${id}`)
      presetRules.value = presetRules.value.filter(r => r.id !== id)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    }
  }

  return {
    presetRules,
    isLoading,
    error,
    fetchPresetRules,
    createPresetRule,
    updatePresetRule,
    deletePresetRule,
  }
})
