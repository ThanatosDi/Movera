<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useRegexPreview } from '@/composables/useRegexPreview'
import { useSessionStorage } from '@vueuse/core'
import { Lightbulb } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

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
// 使用 sessionStorage 持久化測試檔名
const testFilename = useSessionStorage('regexPreview:testFilename', '')

// --- Refactor: Use local refs and watchers for v-model stability ---
const srcPattern = ref(props.srcFilename ?? '')
const dstPattern = ref(props.dstFilename ?? '')

// Watch for prop changes from parent and update local state
watch(
  () => props.srcFilename,
  (newValue) => {
    if (newValue !== srcPattern.value) {
      srcPattern.value = newValue ?? ''
    }
  }
)
watch(
  () => props.dstFilename,
  (newValue) => {
    if (newValue !== dstPattern.value) {
      dstPattern.value = newValue ?? ''
    }
  }
)

// Watch for local changes (user input) and emit to parent
watch(srcPattern, (newValue) => {
  emit('update:srcFilename', newValue)
})
watch(dstPattern, (newValue) => {
  emit('update:dstFilename', newValue)
})
// --- End of Refactor ---

// Use the composable
const { groups, formattedResult, error } = useRegexPreview(
  testFilename,
  srcPattern,
  dstPattern
)

// 載入測試案例的處理函式
const handleLoadTestCase = (testCase: any) => {
  testFilename.value = testCase.filename
  // These will trigger the computed setter and emit updates
  srcPattern.value = testCase.src_filename
  dstPattern.value = testCase.dst_filename
}

const autoGrow = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = `${target.scrollHeight}px`
}
</script>

<template>
  <Card class="border-gray-700 text-foreground bg-background">
    <CardHeader>
      <CardTitle class="flex items-center gap-2">
        <Lightbulb class="w-5 h-5 text-yellow-400" />
        {{ t('components.regexPreview.title') }}
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
            class="text-foreground bg-background border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            placeholder="公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4"
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
        <div class="space-y-2">
          <Label for="regex-src-pattern">{{ t('components.regexPreview.sourcePattern') }}</Label>
          <Textarea
            id="regex-src-pattern"
            v-model="srcPattern"
            placeholder="(?P<title>\w+) - (?P<episode>\d{2})(v2)? (.+)\.mp4"
            class="text-foreground bg-background border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
        <!-- 測試案例按鈕 (暫時註解，需要定義 RegexExamples) -->
        <!-- <div class="space-y-2 col-span-full">
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
        </div> -->
        <div class="space-y-2 col-span-full">
          <Label for="regex-dst-pattern">{{ t('components.regexPreview.destinationPattern') }}</Label>
          <Textarea
            id="regex-dst-pattern"
            v-model="dstPattern"
            placeholder="\g<title> - S01E\g<episode> \4.mp4"
            class="text-foreground bg-background border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
      </div>

      <!-- Error Display -->
      <div
        v-if="error"
        class="bg-destructive/30 border border-red-500 text-destructive-foreground px-4 py-3 rounded-md"
      >
        <p class="font-bold">{{ t('common.error') }}</p>
        <p>{{ t(error) }}</p>
      </div>

      <!-- Results -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        <!-- Named Groups -->
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">{{ t('components.regexPreview.namedGroups') }}</h3>
          <div
            v-if="groups.named_group && Object.keys(groups.named_group).length > 0"
            class="text-foreground bg-background p-4 rounded-md border font-mono text-sm space-y-1"
          >
            <div
              v-for="(value, key) in groups.named_group"
              :key="key"
              class="flex"
            >
              <span class="text-chart-3 mr-2">{{ key }}:</span>
              <span class="text-chart-2">"{{ value }}"</span>
            </div>
          </div>
          <div
            v-else
            class="text-gray-400 italic"
          >
            {{ t('components.regexPreview.noNamedGroups') }}
          </div>
        </div>

        <!-- Numbered Groups -->
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">{{ t('components.regexPreview.numberedGroups') }}</h3>
          <div
            v-if="groups.numbered_group && groups.numbered_group.length > 0"
            class="text-foreground bg-background p-4 rounded-md border font-mono text-sm space-y-1"
          >
            <div
              v-for="(value, index) in groups.numbered_group"
              :key="index"
              class="flex"
            >
              <span class="text-chart-3 mr-2">\{{ index + 1 }}:</span>
              <span class="text-chart-2">{{ value !== null ? `"${value}"` : 'null' }}</span>
            </div>
          </div>
          <div
            v-else
            class="text-gray-400 italic"
          >
            {{ t('components.regexPreview.noNumberedGroups') }}
          </div>
        </div>

        <!-- Formatted Result -->
        <div class="space-y-2 col-span-full">
          <h3 class="font-semibold text-lg">{{ t('components.regexPreview.result') }}</h3>
          <div class="text-chart-2 bg-background border p-4 rounded-md font-mono text-sm break-all">
            {{ formattedResult || t('components.regexPreview.noResult') }}
          </div>
        </div>
      </div>

      <!-- 使用說明 -->
      <div class="text-s text-ring bg-background p-3 rounded border">
        <div class="mb-2"><strong>{{ t('components.regexPreview.instructions.title') }}</strong></div>
        <ul class="space-y-1 list-disc list-inside">
          <li
            v-for="(node, index) in tm('components.regexPreview.instructions.lines')"
            :key="index"
          >
            {{ rt(node) }}
          </li>
        </ul>
        <div class="mt-3 pt-2 border-t border-gray-600">
          <div class="mb-1"><strong>{{ t('components.regexPreview.exampleUsage')
              }}</strong></div>
          <div class="text-s space-y-1">
            <div><code>(\d{2})</code> → <code>\1</code> ({{ t('components.regexPreview.usage1')
            }})</div>
            <div><code>(.+)</code> → <code>\1</code> ({{ t('components.regexPreview.usage2')
            }})</div>
            <div><code>(\d{4})</code> → <code>\1</code> ({{ t('components.regexPreview.usage3')
            }})</div>
          </div>
        </div>
        <div class="mt-3 pt-2 border-t border-gray-600">
          <div class="mb-1"><strong>{{ t('components.regexPreview.commonSymbols')
              }}</strong></div>
          <div class="grid grid-cols-2 gap-2 text-s">
            <div><code>\d</code> - {{ t('components.regexPreview.symbols.d') }}</div>
            <div><code>\w</code> - {{ t('components.regexPreview.symbols.w') }}</div>
            <div><code>+</code> - {{ t('components.regexPreview.symbols.plus') }}</div>
            <div><code>*</code> - {{ t('components.regexPreview.symbols.star') }}</div>
            <div><code>?</code> - {{ t('components.regexPreview.symbols.qmark') }}</div>
            <div><code>\.</code> - {{ t('components.regexPreview.symbols.dot') }}</div>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>