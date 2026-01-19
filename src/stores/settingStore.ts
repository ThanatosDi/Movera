import { request as httpRequest } from "@/composables/useHttpService";
import { useWebSocketService } from '@/composables/useWebSocketService';
import { wsEventsEnum } from '@/enums/wsEventsEnum';
// import { t } from '@/locales';
import type { Settings } from '@/schemas';
import { defineStore } from 'pinia';
import { ref } from 'vue';


export const useSettingStore = defineStore('settingStore', () => {
  const wsService = useWebSocketService()
  const isSaving = ref<boolean>(false)
  const error = ref<string | null>(null)
  const settings = ref<Settings>({
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    locale: navigator.language || 'en',
  })

  async function fetchSettings() {
    error.value = null
    try {
      const response = await wsService.request<{ Settings: Settings }>(wsEventsEnum.getSettings)
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
      const res = await wsService.request<{ Settings: Settings }>(wsEventsEnum.updateSetting, settingsData)
      settings.value = { ...settings.value, ...res }
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      isSaving.value = false
    }
  }

  async function initializeSettings() {
    error.value = null
    try {
      const res = await httpRequest<Settings>('GET', `/api/v1/settings`);
      settings.value = { ...settings.value, ...res }
    } catch (e) {
      error.value = (e as Error).message
      console.error('獲取設定失敗', (e as Error).message)
      throw e
    }
  }

  return {
    settings,
    isSaving,
    error,
    fetchSettings,
    updateSettings,
    initializeSettings,
  }
})