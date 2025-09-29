<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useRegexPreview } from '@/composables/useRegexPreview';
import { RegexExamples } from '@/constants';
import { AlertCircle, CheckCircle, Lightbulb } from 'lucide-vue-next';
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const { t, tm, rt } = useI18n()

// v-model 綁定，從父組件接收 src 和 dst 規則
const props = defineProps<{
  srcFilename: string | null
  dstFilename: string | null
}>()

const emit = defineEmits<{
  'update:srcFilename': [value: string | null]
  'update:dstFilename': [value: string | null]
}>()

// 本地元件狀態，用於測試的檔案名稱
const testFilename = ref('')

// --- Refactor: Use local refs and watchers for v-model stability ---
const srcRule = ref(props.srcFilename ?? '')
const dstRule = ref(props.dstFilename ?? '')

// Watch for prop changes from parent and update local state
watch(
  () => props.srcFilename,
  (newValue) => {
    if (newValue !== srcRule.value) {
      srcRule.value = newValue ?? ''
    }
  }
)
watch(
  () => props.dstFilename,
  (newValue) => {
    if (newValue !== dstRule.value) {
      dstRule.value = newValue ?? ''
    }
  }
)

// Watch for local changes (user input) and emit to parent
watch(srcRule, (newValue) => {
  emit('update:srcFilename', newValue)
})
watch(dstRule, (newValue) => {
  emit('update:dstFilename', newValue)
})
// --- End of Refactor ---

// Use the composable with the reactive rules
const { preview, highlightedParts, error, isValid, groups } = useRegexPreview(
  testFilename,
  srcRule,
  dstRule
)

// 載入測試案例的處理函式
const handleLoadTestCase = (testCase: any) => {
  testFilename.value = testCase.filename
  // These will trigger the computed setter and emit updates
  srcRule.value = testCase.src_filename
  dstRule.value = testCase.dst_filename
}

const autoGrow = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = `${target.scrollHeight}px`
}
</script>

<template>
  <Card class="bg-gray-800 border-gray-700 text-white">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <Lightbulb class="w-5 h-5 text-yellow-400" />
        {{ t('components.preview.regex.title') }}
      </CardTitle>
    </CardHeader>

    <CardContent class="space-y-6">
      <!-- Inputs -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="regex-test-filename">{{ t('components.preview.testFilename') }}</Label>
          <Textarea
            id="regex-test-filename"
            v-model="testFilename"
            :placeholder="t('components.preview.testFilenamePlaceholder')"
            class="bg-gray-900 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />

        </div>
        <div class="space-y-2">
          <Label for="regex-src-rule">{{ t('components.taskForm.srcFilename') }}</Label>
          <Textarea
            id="regex-src-rule"
            v-model="srcRule"
            placeholder="e.g., (.*)\.S(\d{2})E(\d{2})\.(.*)"
            class="bg-gray-900 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
        <div class="space-y-2 col-span-full">
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
        <div class="space-y-2 col-span-full">
          <Label for="regex-dst-rule">{{ t('components.taskForm.dstFilename') }}</Label>
          <Textarea
            id="regex-dst-rule"
            v-model="dstRule"
            placeholder="e.g., \1 S\2E\3.\4"
            class="bg-gray-900 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
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
            {{ isValid ? t('common.matchSuccess') : (error || t('common.noMatch')) }}
          </span>
        </div>

        <!-- 匹配結果高亮 -->
        <div
          v-if="isValid"
          class="bg-gray-900 p-3 rounded-md border border-gray-600"
        >
          <Label class="text-sm text-gray-400 mb-2 block">{{ t('components.preview.matchResult')
          }}</Label>
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
          <Label class="text-sm text-gray-400 mb-2 block">{{
            t('components.preview.regex.capturedGroups') }}</Label>
          <div class="space-y-1">
            <div
              v-for="(group, index) in groups"
              :key="index"
              class="font-mono text-sm"
            >
              <span class="text-blue-400">{{ t('components.preview.regex.group') }} {{ index + 1
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
          <Label class="text-sm text-gray-400 mb-2 block">{{ t('components.preview.renameResult')
          }}</Label>
          <div class="font-mono text-sm break-all">
            <span :class="preview.startsWith(t('components.preview.regex.renameFormatError'))
              ? 'text-red-400'
              : 'text-green-400'">
              {{ preview }}
            </span>
          </div>
        </div>

        <!-- 使用說明 -->
        <div class="text-s text-gray-500 bg-gray-800 p-3 rounded border">
          <div class="mb-2"><strong>{{ t('components.preview.instructions') }}</strong></div>
          <ul class="space-y-1 list-disc list-inside">
            <li
              v-for="(node, index) in tm('components.preview.regex.instructions')"
              :key="index"
            >
              {{ rt(node) }}
            </li>
          </ul>
          <div class="mt-3 pt-2 border-t border-gray-600">
            <div class="mb-1"><strong>{{ t('components.preview.regex.exampleUsage')
            }}</strong></div>
            <div class="text-s space-y-1">
              <div><code>(\d{2})</code> → <code>\1</code> ({{ t('components.preview.regex.usage1')
              }})</div>
              <div><code>(.+)</code> → <code>\1</code> ({{ t('components.preview.regex.usage2')
              }})</div>
              <div><code>(\d{4})</code> → <code>\1</code> ({{ t('components.preview.regex.usage3')
              }})</div>
            </div>
          </div>
          <div class="mt-3 pt-2 border-t border-gray-600">
            <div class="mb-1"><strong>{{ t('components.preview.regex.commonSymbols')
            }}</strong></div>
            <div class="grid grid-cols-2 gap-2 text-s">
              <div><code>\d</code> - {{ t('components.preview.regex.symbols.d') }}</div>
              <div><code>\w</code> - {{ t('components.preview.regex.symbols.w') }}</div>
              <div><code>+</code> - {{ t('components.preview.regex.symbols.plus') }}</div>
              <div><code>*</code> - {{ t('components.preview.regex.symbols.star') }}</div>
              <div><code>?</code> - {{ t('components.preview.regex.symbols.qmark') }}</div>
              <div><code>\.</code> - {{ t('components.preview.regex.symbols.dot') }}</div>
            </div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>