import { useSettingStore } from '@/stores/settingStore'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import './assets/style.css'
import i18n from './locales'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

const settingStore = useSettingStore(pinia)
settingStore.fetchSettings()

app.mount('#app')
