export const LocaleEnum = {
  en: 'en',
  zhTW: 'zh-TW',
  zhCN: 'zh-CN',
} as const;

export type LocaleEnum = typeof LocaleEnum[keyof typeof LocaleEnum];