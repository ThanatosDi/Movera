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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useNotification } from '@/composables/useNotification'
import { ApiError } from '@/schemas/errors'
import { VariableEnum } from '@/enums/VariableEnum'
import { cn } from '@/lib/utils'
import { useSettingStore } from '@/stores/settingStore'
import { Check, ChevronsUpDown, FolderCog, Info, Plus, Save, X } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

// 從 localStorage 讀取時區資料
const timezones = ref<{ value: string, label: string }[]>(JSON.parse(localStorage.getItem(VariableEnum.TimeZoneStorageKey) || '[]'))

const settingStore = useSettingStore()
const { isSaving, settings } = storeToRefs(settingStore)

const UpdateSettings = async () => {
  isSaving.value = true
  try {
    await settingStore.updateSettings(settings.value)
    useNotification.showSuccess(t('notifications.settingsSaveSuccessTitle'), t('notifications.settingsSaveSuccessDesc'))
  } catch (e: unknown) {
    console.error('Failed to update settings:', e)
    const message = e instanceof ApiError || e instanceof Error ? e.message : 'Unknown error'
    useNotification.showError(t('notifications.settingsSaveErrorTitle'), message)
  } finally {
    isSaving.value = false
  }
}

watch(
  () => settings.value.locale, (newLocale, oldLocale) => {
    if (newLocale !== oldLocale) {
      locale.value = newLocale
      UpdateSettings()
    }
  }
)

const handleSaveSettings = async () => {
  await UpdateSettings()
}

// Allowed directories management
const newDirectoryPath = ref('')
const directoryPathError = ref('')

function isAbsolutePath(path: string): boolean {
  // POSIX: starts with /
  // Windows: starts with drive letter (C:\, D:/) or UNC (\\)
  return /^\//.test(path) || /^[A-Za-z]:[/\\]/.test(path) || /^\\\\/.test(path)
}

function addDirectory() {
  const path = newDirectoryPath.value.trim()
  if (!path) return

  if (!isAbsolutePath(path)) {
    directoryPathError.value = t('settingView.allowedDirectoriesCard.absolutePathRequired')
    return
  }

  directoryPathError.value = ''
  if (!settings.value.allowed_directories) {
    settings.value.allowed_directories = []
  }
  if (!settings.value.allowed_directories.includes(path)) {
    settings.value.allowed_directories.push(path)
  }
  newDirectoryPath.value = ''
}

function removeDirectory(index: number) {
  if (settings.value.allowed_directories) {
    settings.value.allowed_directories.splice(index, 1)
  }
}
</script>

<template>
  <main class="bg-background text-foreground flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('settingView.title') }}</h1>
      <p class="">{{ t('settingView.description') }}</p>
    </div>

    <!-- 一般設定卡片 -->
    <Card class="border border-border">
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
                  class="w-full justify-between bg-background text-foreground border-foreground dark:border-foreground"
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
              class="w-[--radix-combobox-trigger-width] bg-background border-foreground text-foreground"
            >
              <div class="relative w-full max-w-sm items-center p-1 ">
                <ComboboxInput
                  class="pl-9 focus-visible:ring-0 border-foreground rounded-none h-10 bg-transparent"
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

    <!-- 允許目錄設定卡片 -->
    <Card class="border border-border" data-testid="allowed-directories-section">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <FolderCog class="size-5" />
          {{ t('settingView.allowedDirectoriesCard.title') }}
        </CardTitle>
        <CardDescription>{{ t('settingView.allowedDirectoriesCard.description') }}</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <!-- 新增目錄 -->
        <div class="space-y-1">
          <div class="flex gap-2">
            <Input
              data-testid="add-directory-input"
              v-model="newDirectoryPath"
              :placeholder="t('settingView.allowedDirectoriesCard.placeholder')"
              :class="['flex-1 border-foreground', directoryPathError ? 'border-red-500' : '']"
              @keydown.enter.prevent="addDirectory"
              @input="directoryPathError = ''"
            />
          <Button
            data-testid="add-directory-btn"
            variant="outline"
            class="border-foreground shrink-0"
            @click="addDirectory"
          >
            <Plus class="size-4 mr-1" />
            {{ t('settingView.allowedDirectoriesCard.add') }}
          </Button>
          </div>
          <p v-if="directoryPathError" class="text-red-500 text-sm">{{ directoryPathError }}</p>
        </div>

        <!-- 已設定的目錄列表 -->
        <div
          v-if="settings.allowed_directories && settings.allowed_directories.length > 0"
          class="space-y-2"
        >
          <div
            v-for="(dir, index) in settings.allowed_directories"
            :key="dir"
            class="flex items-center gap-2 p-2 border rounded-md border-foreground/20"
          >
            <span class="flex-1 font-mono text-sm truncate">{{ dir }}</span>
            <Button
              data-testid="remove-directory-btn"
              variant="ghost"
              size="sm"
              class="text-red-500 hover:text-red-700 shrink-0"
              @click="removeDirectory(index)"
            >
              <X class="size-4" />
            </Button>
          </div>
        </div>

        <!-- 空狀態 -->
        <div
          v-else
          class="text-sm text-muted-foreground p-4 text-center"
        >
          {{ t('settingView.allowedDirectoriesCard.empty') }}
        </div>
      </CardContent>
    </Card>

    <!-- 關於卡片 -->
    <Card class="border border-border">
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
        @click="handleSaveSettings"
      >
        <Save class="size-4 mr-2" />
        {{ isSaving ? t('common.saving') : t('common.save') }}
      </Button>
    </div>
  </main>
</template>
