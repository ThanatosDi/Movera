<script setup lang="ts">
import LocaleSelect from '@/components/LocaleSelect.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Combobox,
  ComboboxAnchor,
  ComboboxEmpty,
  ComboboxGroup,
  ComboboxInput,
  ComboboxItem,
  ComboboxItemIndicator,
  ComboboxList,
  ComboboxTrigger,
} from '@/components/ui/combobox'
import { Label } from '@/components/ui/label'
import { useNotification } from '@/composables/useNotification'
import { cn } from '@/lib/utils'
import { useSettingStore } from '@/stores/settingStore'
import { getTimeZones } from '@vvo/tzdb'
import { Check, ChevronsUpDown, Info, Save } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

// 1. 直接從 Pinia Store 獲取狀態並保持響應性
const settingStore = useSettingStore()
const { settings } = storeToRefs(settingStore)

// 監聽 settings.locale 的變化，並更新 i18n 的 locale
watch(() => settings.value.locale, (newLocale, oldLocale) => {
  if (newLocale !== oldLocale) {
    locale.value = newLocale
    updateSettingsEvent()
  }
})

// 2. 在組件掛載時，從 localStorage 載入設定
onMounted(() => {
  loadTimezones()
})

// 時區列表的載入邏輯
const timezones = ref<{ value: string; label: string }[]>([])
const loadTimezones = () => {
  // 模擬一個載入延遲，讓使用者能看到載入狀態
  setTimeout(() => {
    timezones.value = getTimeZones().map((tz) => {
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
  }, 0) // 延遲 500 毫秒
}

const appVersion = __APP_VERSION__
const isSaving = ref(false)

const updateSettingsEvent = async () => {
  try {
    isSaving.value = true
    await settingStore.updateSettings(settings.value)
    isSaving.value = false
    useNotification.showSuccess(t('notifications.saveSuccessTitle'), t('notifications.saveSuccessDesc'))
  } catch (error: any) {
    console.error('Failed to save settings:', error)
    useNotification.showError(t('notifications.saveErrorTitle'), error.message)
  } finally {
    isSaving.value = false
  }

}
</script>

<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('views.settings.title') }}</h1>
      <p class="text-gray-400">{{ t('views.settings.description') }}</p>
    </div>

    <!-- 一般設定卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Info class="size-5" />
          {{ t('views.settings.general.title') }}
        </CardTitle>
        <CardDescription>{{ t('views.settings.general.description') }}</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="flex flex-col space-y-2">
          <Label>{{ t('common.language') }}</Label>
          <LocaleSelect v-model:locale="settings.locale" />

          <Label>{{ t('common.timezone') }}</Label>
          <Combobox
            v-model="settings.timezone"
            class="w-full"
          >
            <ComboboxAnchor as-child>
              <ComboboxTrigger as-child>
                <Button
                  variant="outline"
                  class="w-full justify-between bg-gray-700 border-gray-600 hover:bg-gray-600 hover:text-white"
                  :disabled="timezones.length === 0"
                >
                  <span v-if="timezones.length === 0">{{ t('views.settings.timezoneLoading') }}</span>
                  <span v-else>
                    {{
                      settings.timezone
                        ? timezones.find((tz) => tz.value === settings.timezone)?.label
                        : t('views.settings.timezonePlaceholder')
                    }}
                  </span>
                  <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </ComboboxTrigger>
            </ComboboxAnchor>

            <ComboboxList
              align="start"
              class="w-[--radix-combobox-trigger-width] bg-gray-800 border-gray-700 text-white"
            >
              <div class="relative w-full max-w-sm items-center p-1">
                <ComboboxInput
                  class="pl-9 focus-visible:ring-0 border-0 rounded-none h-10 bg-transparent"
                  :placeholder="t('views.settings.timezoneSearch')"
                />
              </div>

              <ComboboxEmpty>{{ t('views.settings.timezoneNotFound') }}</ComboboxEmpty>

              <ComboboxGroup class="max-h-64 overflow-y-auto">
                <ComboboxItem
                  v-for="tz in timezones"
                  :key="tz.value"
                  :value="tz.value"
                  class="hover:bg-gray-700 text-white"
                >
                  {{ tz.label }}
                  <ComboboxItemIndicator>
                    <Check :class="cn('ml-auto h-4 w-4')" />
                  </ComboboxItemIndicator>
                </ComboboxItem>
              </ComboboxGroup>
            </ComboboxList>
          </Combobox>
        </div>
      </CardContent>
    </Card>

    <!-- 關於卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle>{{ t('common.about') }}</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-gray-400">{{ t('common.version') }}: {{ appVersion }}</p>
      </CardContent>
    </Card>

    <!-- 儲存按鈕 -->
    <div class="flex justify-end mt-4">
      <Button
        :disabled="isSaving"
        @click="updateSettingsEvent"
        class="bg-green-400 hover:bg-green-800 font-bold text-black"
      >
        <Save class="size-4 mr-2" />
        {{ isSaving ? t('common.saving') : t('common.save') }}
      </Button>
    </div>
  </main>
</template>
