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
    try {
      const response = await wsService.request<{ Settings: Settings }>(wsEventsEnum.getSettings)
      settings.value = { ...settings.value, ...response }
    } catch (e) {
      console.error('Failed to fetch settings:', e)
      throw e
    }
  }

  async function updateSettings(settingsData: Settings) {
    try {
      const res = await wsService.request<{ Settings: Settings }>(wsEventsEnum.updateSetting, settingsData)
      settings.value = { ...settings.value, ...res }
    } catch (error: any) {
      throw error
    }
  }

  async function initializeSettings() {
    try {
      const res = await httpRequest<Settings>('GET', `/api/v1/settings`);
      console.log(res)
      settings.value = { ...settings.value, ...res }
    } catch (error: any) {
      console.error('獲取設定失敗', error.message)
      throw error
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