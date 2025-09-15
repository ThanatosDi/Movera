import App from '@/App.vue'
import '@/assets/style.css'
import { createI18nInstance } from '@/locales'
import router from '@/router'
import { useSettingStore } from '@/stores/settingStore'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

async function initializeApp() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // 必須在 app.use(pinia) 之後才能使用 useSettingStore
  const settingStore = useSettingStore()

  // 等待設定從後端載入完成
  await settingStore.fetchSettings()

  // 使用載入的 locale 來建立 i18n 實例
  const i18n = createI18nInstance(settingStore.settings.locale)

  app.use(router)
  app.use(i18n)

  app.mount('#app')
}

initializeApp()
