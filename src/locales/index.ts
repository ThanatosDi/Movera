import { createI18n } from 'vue-i18n'
// 這是最後的手段：將 JSON 作為原始文字導入，然後手動解析。
// 這可以繞過所有 Vite/Rollup/TypeScript 的模組解析問題。
import enUS from './en-US.json?raw'
import zhTW from './zh-TW.json?raw'

const messages = {
  'en-US': JSON.parse(enUS),
  'zh-TW': JSON.parse(zhTW),
}

// 直接建立並匯出 i18n 實例
const i18n = createI18n({
  legacy: false,
  locale: 'en-US', // 先用一個預設/備用語系啟動
  fallbackLocale: 'en-US',
  globalInjection: true,
  messages,
})

export default i18n
