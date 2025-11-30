import App from '@/App.vue'
import { createI18nInstance } from '@/locales'
import routers from '@/routers'
import { useSettingStore } from '@/stores/settingStore'
import '@/style.css'
import { createPinia } from 'pinia'
import { createApp } from 'vue'



// 設定預設為暗色模式
if (!localStorage.getItem('vueuse-color-scheme')) {
  localStorage.setItem('vueuse-color-scheme', 'dark')
  document.documentElement.classList.add('dark')
}


async function initializeApp() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // 必須在 app.use(pinia) 之後才能使用 stores
  const settingStore = useSettingStore()


  try {
    // 連線成功後，再從後端載入設定
    await settingStore.initializeSettings()
  } catch (error) {
    console.error('應用程式初始化失敗:', error)
  }

  // 使用載入的 locale 來建立 i18n 實例
  const i18n = createI18nInstance(settingStore.settings.locale)

  app.use(routers)
  app.use(i18n)

  app.mount('#app')
}

initializeApp()
