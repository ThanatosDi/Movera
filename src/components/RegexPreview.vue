<script setup lang="js">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useRegexPreview } from '@/composables/useRegexPreview'
import { AlertCircle, CheckCircle, Lightbulb } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'

// Props
const props = defineProps({
  srcRegex: String,
  dstRegex: String,
})

// Emits
const emit = defineEmits(['update:srcRegex', 'update:dstRegex'])

// 創建響應式 refs 來追蹤 props
const srcRegexRef = ref(props.srcRegex || '')
const dstRegexRef = ref(props.dstRegex || '')

// 監聽 props 變化並同步到內部狀態
watch(
  () => props.srcRegex,
  (newValue) => {
    srcRegexRef.value = newValue || ''
  },
  { immediate: true },
)

watch(
  () => props.dstRegex,
  (newValue) => {
    dstRegexRef.value = newValue || ''
  },
  { immediate: true },
)

// Composable - 傳入響應式 refs
const {
  testFilename,
  srcRegex,
  dstRegex,
  regexResult,
  highlightedFilename,
  testCases,
  setTestFilename,
  setSrcRegex,
  setDstRegex,
  loadTestCase,
} = useRegexPreview(srcRegexRef, dstRegexRef)

// 方法
const updateSrcRegex = (value) => {
  srcRegexRef.value = value
  setSrcRegex(value)
  emit('update:srcRegex', value)
}

const updateDstRegex = (value) => {
  dstRegexRef.value = value
  setDstRegex(value)
  emit('update:dstRegex', value)
}

const handleLoadTestCase = (caseKey) => {
  loadTestCase(caseKey)
  // 更新本地 refs
  srcRegexRef.value = srcRegex.value
  dstRegexRef.value = dstRegex.value
  // 發送事件
  emit('update:srcRegex', srcRegex.value)
  emit('update:dstRegex', dstRegex.value)
}

// 計算屬性
const testCaseButtons = computed(() => [
  { key: 'anime1', label: '動漫案例1' },
  { key: 'anime2', label: '動漫案例2' },
  { key: 'anime3', label: '動漫案例3' },
  { key: 'movie', label: '電影案例' },
])
</script>

<template>
  <Card class="bg-gray-800 border-gray-700 text-white">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <Lightbulb class="w-5 h-5 text-yellow-400" />
        正規表達式預覽
      </CardTitle>
    </CardHeader>

    <CardContent class="space-y-4">
      <!-- 測試檔案名稱輸入 -->
      <div>
        <label class="block text-sm font-medium mb-2">測試檔案名稱：</label>
        <Input
          :model-value="testFilename"
          @update:model-value="(value) => { setTestFilename(String(value ?? '')) }"
          placeholder="輸入要測試的檔案名稱"
          class="bg-gray-700 border-gray-600"
        />

        <!-- 測試案例按鈕 -->
        <div class="mt-2 flex flex-wrap gap-2">
          <Button
            v-for="testCase in testCaseButtons"
            :key="testCase.key"
            type="button"
            @click="handleLoadTestCase(testCase.key)"
            size="sm"
            variant="outline"
            class="bg-blue-600 hover:bg-blue-700 border-blue-600"
          >
            {{ testCase.label }}
          </Button>
        </div>
      </div>

      <!-- 預覽結果 -->
      <div class="space-y-4">
        <!-- 匹配狀態 -->
        <div class="flex items-center space-x-2">
          <CheckCircle
            v-if="regexResult.isValid"
            class="w-5 h-5 text-green-400"
          />
          <AlertCircle
            v-else
            class="w-5 h-5 text-red-400"
          />
          <span :class="regexResult.isValid ? 'text-green-400' : 'text-red-400'">
            {{ regexResult.isValid ? '匹配成功' : (regexResult.error || '無匹配') }}
          </span>
        </div>

        <!-- 匹配結果高亮 -->
        <div
          v-if="regexResult.isValid"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <div class="text-sm text-gray-400 mb-2">匹配結果：</div>
          <div class="font-mono text-sm break-all">
            <span class="text-gray-300">{{ highlightedFilename.before }}</span>
            <span class="bg-yellow-500 text-black px-1 rounded">{{ highlightedFilename.match }}</span>
            <span class="text-gray-300">{{ highlightedFilename.after }}</span>
          </div>
        </div>

        <!-- 捕獲群組 -->
        <div
          v-if="regexResult.isValid && regexResult.groups.length > 0"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <div class="text-sm text-gray-400 mb-2">捕獲群組：</div>
          <div class="space-y-1">
            <div
              v-for="(group, index) in regexResult.groups"
              :key="index"
              class="font-mono text-sm"
            >
              <span class="text-blue-400">群組 {{ index + 1 }}:</span>
              <span class="text-green-400 ml-2 bg-gray-700 px-2 py-1 rounded">{{ group }}</span>
            </div>
          </div>
        </div>

        <!-- 重新命名結果 -->
        <div
          v-if="regexResult.isValid && regexResult.renamedFilename"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <div class="text-sm text-gray-400 mb-2">重新命名後：</div>
          <div class="font-mono text-sm break-all">
            <span :class="regexResult.renamedFilename.startsWith('重新命名格式錯誤')
              ? 'text-red-400'
              : 'text-green-400'">
              {{ regexResult.renamedFilename }}
            </span>
          </div>
        </div>

        <div class="text-xs text-gray-500 bg-gray-800 p-3 rounded border">
          <div class="mb-2"><strong>使用說明：</strong></div>
          <ul class="space-y-1 list-disc list-inside">
            <li>在「檔案名稱正規表示法」中使用括號 () 來建立捕獲群組</li>
            <li>在「重新命名正規表示法」中使用 \1, \2, \3 等來引用對應的群組</li>
            <li>例如：(\d{2}) 會捕獲兩位數字，在重新命名時用 \1 引用</li>
            <li>可以在上方修改測試檔案名稱來驗證不同的情況</li>
            <li>點擊上方的測試案例按鈕可以快速載入範例</li>
          </ul>
          <div class="mt-3 pt-2 border-t border-gray-600">
            <div class="mb-1"><strong>群組引用範例：</strong></div>
            <div class="text-xs space-y-1">
              <div><code>(\d{2})</code> → <code>\1</code> (捕獲兩位數字)</div>
              <div><code>(.+)</code> → <code>\1</code> (捕獲任意字符)</div>
              <div><code>(\d{4})</code> → <code>\1</code> (捕獲四位數字，如年份)</div>
            </div>
          </div>
          <div class="mt-3 pt-2 border-t border-gray-600">
            <div class="mb-1"><strong>常用正規表達式符號：</strong></div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div><code>\d</code> - 數字 (0-9)</div>
              <div><code>\w</code> - 字母數字</div>
              <div><code>+</code> - 一個或多個</div>
              <div><code>*</code> - 零個或多個</div>
              <div><code>?</code> - 零個或一個</div>
              <div><code>\.</code> - 點號字面值</div>
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>