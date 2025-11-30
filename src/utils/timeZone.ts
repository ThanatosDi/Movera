import { getTimeZones } from '@vvo/tzdb'
import { VariableEnum } from '@/enums/VariableEnum'

/**
 * Initializes and stores the timezone list in localStorage if it doesn't already exist.
 */
export function initializeTimeZones(): void {
  const existingTimezones = localStorage.getItem(VariableEnum.TimeZoneStorageKey)

  if (!existingTimezones) {
    const timezones = getTimeZones().map((tz) => {
      const offset = tz.currentTimeOffsetInMinutes
      const offsetHours = Math.floor(Math.abs(offset) / 60)
      const offsetMinutes = Math.abs(offset) % 60
      const sign = offset >= 0 ? '+' : '-'
      const formattedOffset = `UTC${sign}${String(offsetHours).padStart(2, '0')}:${String(
        offsetMinutes,
      ).padStart(2, '0')}`

      return {
        value: tz.name,
        label: `${tz.name} (${formattedOffset})`,
      }
    })
    localStorage.setItem(VariableEnum.TimeZoneStorageKey, JSON.stringify(timezones))
  }
}
