import { request } from '@/composables/useHttpService';
import type { Settings } from '@/schemas';
import { defineStore } from 'pinia';
import { ref } from 'vue';


export const useSettingStore = defineStore('settingStore', () => {
  const isSaving = ref<boolean>(false)
  const error = ref<string | null>(null)
  const settings = ref<Settings>({
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    locale: navigator.language || 'en',
  })

  async function fetchSettings() {
    error.value = null
    try {
      const response = await request<Settings>('GET', '/api/v1/settings')
      settings.value = { ...settings.value, ...response }
    } catch (e) {
      error.value = (e as Error).message
      console.error('Failed to fetch settings:', e)
      throw e
    }
  }

  async function updateSettings(settingsData: Settings) {
    error.value = null
    isSaving.value = true
    try {
      const res = await request<Settings>('PUT', '/api/v1/settings', settingsData)
      settings.value = { ...settings.value, ...res }
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isSaving.value = false
    }
  }

  return {
    settings,
    isSaving,
    error,
    fetchSettings,
    updateSettings,
  }
})
