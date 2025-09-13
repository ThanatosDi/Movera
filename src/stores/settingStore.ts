import type { Settings } from '@/schemas';
import { settingService } from '@/services/settingService';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSettingStore = defineStore('settingStore', () => {
  const settings = ref<Settings>({
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    locale: navigator.language || 'en-US',
    server_address: 'http://127.0.0.1:8000',
  })

  // --- Actions ---
  // 可以在這裡定義 function，等同於 actions 選項
  async function fetchSettings() {
    try {
      const res = await settingService.getAll()
      settings.value = { ...settings.value, ...res }
    } catch (error: any) {
      console.error('獲取設定失敗', error.message)
      throw error
    }
  }

  async function updateSettings(settingsData: Settings) {
    try {
      const res = await settingService.update(settingsData)
      settings.value = { ...settings.value, ...res }
    } catch (error: any) {
      console.error('更新設定失敗', error.message)
      throw error
    }
  }

  return {
    settings,
    fetchSettings,
    updateSettings,
  }
})