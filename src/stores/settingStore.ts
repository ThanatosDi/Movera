import type { Settings } from '@/schemas';
import { settingService } from '@/services/settingService';
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSettingStore = defineStore('settingStore', ()=>{
  const settings = ref<Settings>({
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    locale: navigator.language || 'en-US',
    server_address: 'http://127.0.0.1:8000',
  })

  // --- Actions ---
  // 可以在這裡定義 function，等同於 actions 選項
  async function fetchSettings(){
    try {
      settingService.getAll().then((res)=>{
        settings.value = {...settings.value, ...res}
      })
    }catch(error:any){
      console.error('獲取設定失敗', error.message)
      throw error
    }
  }

  async function updateSettings(settingsData: Settings){
    try {
      settingService.update(settingsData).then((res)=>{
        settings.value = {...settings.value, ...res}
      })
    }catch(error:any){
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
// // 1. 定義設定的結構類型 (符合 API 的新格式)
// export interface Settings {
//   timezone: string
//   locale: string
//   server_address: string
// }

// // 2. 預設設定值
// const defaultSettings: Settings = {
//   timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, // 使用瀏覽器當前時區
//   locale: navigator.language || 'en-US', // 使用瀏覽器語言作為預設值
//   server_address: 'http://127.0.0.1:8000',
// }

// // localStorage 的儲存鍵
// const STORAGE_KEY = 'app_settings'

// export const useSettingStore = defineStore('setting', () => {
//   // 3. State: 使用 ref 定義響應式狀態
//   const settings = ref<Settings>(JSON.parse(JSON.stringify(defaultSettings)))

//   // 4. Actions: 定義修改狀態的方法

//   /**
//    * 從 API 取得最新設定並更新狀態。
//    * 成功後會自動儲存到 localStorage。
//    */
//   async function fetchSettings() {
//     try {
//       // TODO: 將 '/api/settings' 替換為您真實的 API 端點
//       const response = await fetch('/api/settings')
//       if (!response.ok) {
//         throw new Error('Network response was not ok')
//       }
//       const apiSettings: Settings = await response.json()

//       // 更新 store 中的 settings
//       settings.value = { ...settings.value, ...apiSettings }
      
//       // 將更新後的設定存到 localStorage
//       saveSettings()
//     } catch (error) {
//       console.error('Failed to fetch settings from API:', error)
//       // 發生錯誤時，可以選擇載入本地儲存的設定作為備用
//       loadSettings()
//     }
//   }

//   /**
//    * 從 localStorage 載入設定。
//    * 如果 localStorage 中沒有，則使用預設值。
//    */
//   function loadSettings() {
//     const storedSettings = localStorage.getItem(STORAGE_KEY)
//     if (storedSettings) {
//       // 合併儲存的設定與預設值，以防未來新增設定項
//       settings.value = {
//         ...defaultSettings,
//         ...JSON.parse(storedSettings),
//       }
//     } else {
//       // 如果沒有儲存的設定，則使用預設值
//       settings.value = JSON.parse(JSON.stringify(defaultSettings))
//     }
//   }

//   /**
//    * 將當前設定儲存到 localStorage。
//    */
//   function saveSettings() {
//     localStorage.setItem(STORAGE_KEY, JSON.stringify(settings.value))
//   }

//   /**
//    * 將設定重設為預設值並儲存。
//    */
//   function resetSettings() {
//     settings.value = JSON.parse(JSON.stringify(defaultSettings))
//     saveSettings()
//   }

//   // 5. 返回 State 和 Actions
//   return {
//     settings,
//     fetchSettings,
//     loadSettings,
//     saveSettings,
//     resetSettings,
//   }
// })
