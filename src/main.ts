import App from '@/App.vue'
import { createI18nInstance } from '@/locales'
import routers from '@/routers'
import '@/style.css'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

/**
 * 創建 Vue 實例
 */
const app = createApp(App)
const pinia = createPinia()
const i18n = createI18nInstance('zh-TW')

/**
 * 設置 Vue 實例
 */
app.use(routers)
app.use(pinia)
app.use(i18n)
app.mount('#app')