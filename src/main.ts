import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/style.css'
import i18n from './locales' // 直接匯入 i18n 實例
import router from './router'

function initializeApp() {
  const app = createApp(App)

  // 恢復 Pinia 的初始化
  const pinia = createPinia()
  app.use(pinia)

  app.use(router)
  app.use(i18n) // 立即使用 i18n 實例

  app.mount('#app') // 立即掛載 App

  // --- 決定性測試 (版本 2) ---
  // 保持 Pinia 啟用，但手動觸發 i18n 更新
  setTimeout(() => {
    console.log('延遲測試：準備將語系更新為 zh-TW')
    i18n.global.locale.value = 'zh-TW'
    console.log('延遲測試：i18n 語系已更新為:', i18n.global.locale.value)
  }, 2000)
}

initializeApp()
