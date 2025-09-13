import { createI18n } from 'vue-i18n'
import enUS from './en-US.json'
import zhTW from './zh-TW.json'

/**
 * 建立並設定 i18n 實例
 * @param locale - 初始語系
 * @returns i18n 實例
 */
export function createI18nInstance(locale: string) {
  return createI18n({
    legacy: false, // 確保使用 Vue 3 Composition API 模式
    locale, // 使用傳入的參數設定預設語系
    fallbackLocale: 'en-US', // 設定備用語系
    globalInjection: true,
    messages: {
      "en-US": enUS,
      'zh-TW': zhTW,
    },
  })
}
