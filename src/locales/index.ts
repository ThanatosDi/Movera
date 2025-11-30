import { createI18n } from 'vue-i18n'
import en from './en.json'
import zhTW from './zh-TW.json'

export function createI18nInstance(locale: string) {
  return createI18n({
    legacy: false, // 確保使用 Vue 3 Composition API 模式
    locale, // 使用傳入的參數設定預設語系
    fallbackLocale: 'en', // 設定備用語系
    globalInjection: true,
    messages: {
      "en": en,
      'zh-TW': zhTW,
    },
  })
}
