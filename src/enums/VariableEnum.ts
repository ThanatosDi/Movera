export const VariableEnum = {
  AppName: 'Movera',
  AppVersion: __APP_VERSION__,
  TimeZoneStorageKey: 'movera-timezones',
} as const;

export type VariableEnum = typeof VariableEnum[keyof typeof VariableEnum];