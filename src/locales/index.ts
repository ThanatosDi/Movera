import { createI18n } from 'vue-i18n'
import en from './en.json'
import zhTW from './zh-TW.json'

const i18n = createI18n({
  legacy: false, // 確保使用 Vue 3 Composition API 模式
  locale: 'zh-TW', // 設定預設語系
  fallbackLocale: 'en', // 設定備用語系
  messages: {
    en,
    'zh-TW': zhTW,
  },
})

export default i18n
