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
import { VariableEnum } from '@/enums/VariableEnum'
import { cn } from '@/lib/utils'
import { Check, ChevronsUpDown, Info, Save } from 'lucide-vue-next'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const timezones = ref<{ value: string, label: string }[]>(JSON.parse(localStorage.getItem(VariableEnum.TimeZoneStorageKey) || '[]'))

const isSaving = ref(false)
const settings = ref({
  locale: locale.value,
  timezone: '',
})
</script>

<template>
  <main class="bg-background text-foreground flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('settingView.title') }}</h1>
      <p class="">{{ t('settingView.description') }}</p>
    </div>

    <!-- 一般設定卡片 -->
    <Card class="border-gray-700 ">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Info class="size-5" />
          {{ t('settingView.generalCard.title') }}
        </CardTitle>
        <CardDescription>{{ t('settingView.generalCard.description') }}</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="flex flex-col space-y-2">
          <Label>{{ t('common.language') }}</Label>
          <LocaleSelect v-model:locale="settings.locale" />
          <Label>{{ t('common.timezone') }}</Label>
          <Combobox v-model="settings.timezone">
            <ComboboxAnchor as-child>
              <ComboboxTrigger as-child>
                <Button
                  variant="outline"
                  class="w-full justify-between bg-background text-foreground border-border hover:border-border hover:text-foreground"
                  :disabled="timezones.length === 0"
                >
                  <span v-if="timezones.length === 0">{{ t('settingView.generalCard.timezoneLoading') }}</span>
                  <span v-else>
                    {{
                      settings.timezone
                        ? timezones.find((tz) => tz.value === settings.timezone)?.label
                        : t('settingView.generalCard.timezonePlaceholder')
                    }}
                  </span>
                  <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </ComboboxTrigger>
            </ComboboxAnchor>
            <ComboboxList
              align="start"
              class="w-[--radix-combobox-trigger-width] bg-background border-border text-foreground"
            >
              <div class="relative w-full max-w-sm items-center p-1">
                <ComboboxInput
                  class="pl-9 focus-visible:ring-0 border-0 rounded-none h-10 bg-transparent"
                  :placeholder="t('settingView.generalCard.timezoneSearch')"
                />
              </div>
              <ComboboxEmpty>{{ t('settingView.generalCard.timezoneNotFound') }}</ComboboxEmpty>
              <ComboboxGroup class="max-h-64 overflow-y-auto">
                <ComboboxItem
                  v-for="tz in timezones"
                  :key="tz.value"
                  :value="tz.value"
                  class="hover:bg-background text-foreground"
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
    <Card class="border-gray-700">
      <CardHeader>
        <CardTitle>{{ t('common.about') }}</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-foreground">{{ t('common.version') }}: {{ VariableEnum.AppVersion }}</p>
      </CardContent>
    </Card>

    <!-- 儲存按鈕 -->
    <div class="flex justify-end mt-4">
      <Button
        :disabled="isSaving"
        class="bg-green-400 hover:bg-green-800 font-bold text-black"
      >
        <Save class="size-4 mr-2" />
        {{ isSaving ? t('common.saving') : t('common.save') }}
      </Button>
    </div>
  </main>
</template>
