<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useRegexPreview } from '@/composables/useRegexPreview';
import { RegexExamples } from '@/constants';
import { AlertCircle, CheckCircle, Lightbulb } from 'lucide-vue-next';
import { computed, ref } from 'vue';

// v-model 綁定，從父組件接收 src 和 dst 規則
const srcFilename = defineModel<string | null>('srcFilename')
const dstFilename = defineModel<string | null>('dstFilename')

// 本地元件狀態，用於測試的檔案名稱
const testFilename = ref<string>('')

// 建立安全的 computed refs，確保傳遞給 composable 的值永遠是 string
// 使用 ?? (nullish coalescing operator) 如果 model 是 null 或 undefined，就回傳空字串 ''
const safeSrcFilename = computed(() => srcFilename.value ?? '')
const safeDstFilename = computed(() => dstFilename.value ?? '')
// --- ↑↑↑ 新增的程式碼 ↑↑↑ ---

// 在元件內部響應式地使用 useRegexPreview
// 當 testFilename, srcFilename, 或 dstFilename 變化時，結果會自動更新
const { preview, highlightedParts, error, isValid, groups } = useRegexPreview(
  testFilename,
  safeSrcFilename,
  safeDstFilename
)

// 載入測試案例的處理函式
const handleLoadTestCase = (testCase: any) => {
  testFilename.value = testCase.filename
  // 直接更新 model，預覽結果會自動重新計算
  srcFilename.value = testCase.src_filename
  dstFilename.value = testCase.dst_filename
}
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
        <Label
          for="test-filename"
          class="block text-sm font-medium mb-2"
        >測試檔案名稱：</Label>
        <Input
          id="test-filename"
          v-model="testFilename"
          placeholder="輸入要測試的檔案名稱"
          class="bg-gray-700 border-gray-600"
        />

        <!-- 測試案例按鈕 -->
        <div class="mt-2 flex flex-wrap gap-2">
          <Button
            v-for="exampleCase in RegexExamples"
            :key="exampleCase.key"
            @click="handleLoadTestCase(exampleCase)"
            type="button"
            size="sm"
            variant="outline"
            class="bg-blue-600 hover:bg-blue-700 border-blue-600"
          >
            {{ exampleCase.label }}
          </Button>
        </div>
      </div>

      <!-- 預覽結果 -->
      <div class="space-y-4">
        <!-- 匹配狀態 -->
        <div class="flex items-center space-x-2">
          <CheckCircle
            v-if="isValid"
            class="w-5 h-5 text-green-400"
          />
          <AlertCircle
            v-else
            class="w-5 h-5 text-red-400"
          />
          <span :class="isValid ? 'text-green-400' : 'text-red-400'">
            {{ isValid ? '匹配成功' : (error || '無匹配結果') }}
          </span>
        </div>

        <!-- 匹配結果高亮 -->
        <div
          v-if="isValid"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <Label class="text-sm text-gray-400 mb-2 block">匹配結果：</Label>
          <p class="preview-text">
            <span>{{ highlightedParts.before }}</span>
            <span
              v-if="highlightedParts.match"
              class="bg-green-700 rounded p-0.5"
            >
              {{ highlightedParts.match }}
            </span>
            <span>{{ highlightedParts.after }}</span>
          </p>
        </div>

        <!-- 捕獲群組 -->
        <div
          v-if="isValid && groups.length > 0"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <Label class="text-sm text-gray-400 mb-2 block">捕獲群組：</Label>
          <div class="space-y-1">
            <div
              v-for="(group, index) in groups"
              :key="index"
              class="font-mono text-sm"
            >
              <span class="text-blue-400">群組 {{ index + 1
              }}:</span>
              <span class="text-green-400 ml-2 bg-gray-700 px-2 py-1 rounded">{{ group }}</span>
            </div>
          </div>
        </div>

        <!-- 重新命名結果 -->
        <div
          v-if="isValid && preview"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <Label class="text-sm text-gray-400 mb-2 block">重新命名後：</Label>
          <div class="font-mono text-sm break-all">
            <span :class="preview.startsWith('重新命名格式錯誤')
              ? 'text-red-400'
              : 'text-green-400'">
              {{ preview }}
            </span>
          </div>
        </div>

        <div class="text-xs text-gray-500 bg-gray-800 p-3 rounded border">
          <div class="mb-2"><strong>使用說明：</strong></div>
          <ul class="space-y-1 list-disc list-inside">
            <li
              v-for="(instruction, index) in [
              '在「檔案名稱正規表示法」中使用括號 () 來建立捕獲群組',
              '在「重新命名正規表示法」中使用 \\1, \\2, \\3 等來引用對應的群組',
              '例如：(\\d{2}) 會捕獲兩位數字，在重新命名時用 \\1 引用',
              '可以在上方修改測試檔案名稱來驗證不同的情況',
              '點擊上方的測試案例按鈕可以快速載入範例'
            ]"
              :key="index"
            >
              {{ instruction }}
            </li>
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
