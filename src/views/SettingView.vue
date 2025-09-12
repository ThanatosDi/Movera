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
import { cn } from '@/lib/utils'
import { useSettingStore } from '@/stores/settingStore'
import { getTimeZones } from '@vvo/tzdb'
import { Check, ChevronsUpDown, HardDrive, Info, Save } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { onMounted, ref } from 'vue'

// 1. 直接從 Pinia Store 獲取狀態並保持響應性
const settingStore = useSettingStore()
const { settings } = storeToRefs(settingStore)

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
  }, 500) // 延遲 500 毫秒
}

const appVersion = __APP_VERSION__
const isSaving = ref(false)

// 3. 修改儲存函式，直接呼叫 store 的 action 來持久化儲存
// const save = () => {
//   isSaving.value = true
//   // 模擬一個非同步儲存操作
//   setTimeout(() => {
//     settingStore.saveSettings() // v-model 已經更新了 store 的狀態，這裡只需觸發保存
//     isSaving.value = false
//     useNotification.showSuccess('設定已儲存', '您的變更已成功套用。')
//   }, 1000)
// }

const triggerSaveBtn = async () => {
  try {
    isSaving.value = true
    await settingStore.updateSettings(settings.value)
    isSaving.value = false
    useNotification.showSuccess('設定已儲存', '您的變更已成功套用。')
  } catch (error: any) {
    console.error('Failed to save settings:', error)
    useNotification.showError('儲存設定失敗', error.message)
  } finally {
    isSaving.value = false
  }

}
</script>

<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">設定</h1>
      <p class="text-gray-400">管理應用程式的全域設定</p>
    </div>

    <!-- 一般設定卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <Info class="size-5" />
          一般設定
        </CardTitle>
        <CardDescription>調整應用程式的外觀與通知行為。</CardDescription>
      </CardHeader>
      <CardContent class="space-y-6">
        <div class="flex flex-col space-y-2">
          <Label>語言</Label>
          <LocaleSelect v-model:locale="settings.locale" />

          <Label>時區</Label>
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
                  <span v-if="timezones.length === 0">載入時區中...</span>
                  <span v-else>
                    {{
                      settings.timezone
                        ? timezones.find((tz) => tz.value === settings.timezone)?.label
                        : '選擇時區...'
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
                  placeholder="搜尋時區..."
                />
              </div>

              <ComboboxEmpty>找不到時區。</ComboboxEmpty>

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

    <!-- 連線設定卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle class="flex items-center gap-2">
          <HardDrive class="size-5" />
          連線設定
        </CardTitle>
        <CardDescription>
          設定後端 API 伺服器的連線位址。一般狀況下無需特別設定，保持原樣即可。
        </CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <div>
          <Label for="server-address">API 伺服器位址</Label>
          <!-- 4. 將 v-model 直接綁定到 store 的狀態 -->
          <Input
            id="server-address"
            v-model="settings.server_address"
            placeholder="例如：http://127.0.0.1:8000"
            class="bg-gray-700 border-gray-600 mt-2"
          />
        </div>
      </CardContent>
    </Card>

    <!-- 關於卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle>關於</CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-gray-400">應用程式版本: {{ appVersion }}</p>
      </CardContent>
    </Card>

    <!-- 儲存按鈕 -->
    <div class="flex justify-end mt-4">
      <Button
        :disabled="isSaving"
        @click="triggerSaveBtn"
        class="bg-green-400 hover:bg-green-800 font-bold text-black"
      >
        <Save class="size-4 mr-2" />
        {{ isSaving ? '儲存中...' : '儲存設定' }}
      </Button>
    </div>
  </main>
</template>
