<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useParsePreview } from '@/composables/useParsePreview'
import { ParseExamples } from '@/constants'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, tm, rt } = useI18n()

// Props and Emits for v-model
const props = defineProps<{
  srcFilename: string | null
  dstFilename: string | null
}>()

const emit = defineEmits<{
  'update:srcFilename': [value: string | null]
  'update:dstFilename': [value: string | null]
}>()

// Local state for the component
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

// Use the composable
const { parsedFields, formattedResult, error, isLoading } = useParsePreview(
  testFilename,
  srcRule,
  dstRule
)

// Load test case handler
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
      <CardTitle>{{ t('components.preview.parse.title') }}</CardTitle>
      <CardDescription>{{ t('components.preview.parse.description') }}</CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <!-- Inputs -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="test-filename">{{ t('components.preview.parse.testFilename') }}</Label>
          <Textarea
            id="test-filename"
            v-model="testFilename"
            class="bg-gray-900 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            :disabled="isLoading"
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />

        </div>
        <div class="space-y-2">
          <Label for="src-rule">{{ t('components.preview.parse.sourceRule') }}</Label>
          <Textarea
            id="src-rule"
            v-model="srcRule"
            placeholder="{title}.S{season:02d}E{episode:02d}.{extension}"
            class="bg-gray-900 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            :disabled="isLoading"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
        <div class="space-y-2 col-span-full">
          <!-- Test case buttons -->
          <div class="mt-2 flex flex-wrap gap-2">
            <Button
              v-for="exampleCase in ParseExamples"
              :key="exampleCase.key"
              @click="handleLoadTestCase(exampleCase)"
              type="button"
              size="sm"
              variant="outline"
              class="bg-sky-600 hover:bg-sky-700 border-sky-600"
              :disabled="isLoading"
            >
              {{ exampleCase.label }}
            </Button>
          </div>
        </div>
        <div class="space-y-2 col-span-full">
          <Label for="dst-rule">{{ t('components.preview.parse.targetRule') }}</Label>
          <Textarea
            id="dst-rule"
            v-model="dstRule"
            placeholder="{title} S{season:02d}E{episode:02d}.{extension}"
            class="bg-gray-900 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            :disabled="isLoading"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
      </div>

      <!-- Loading and Error Display -->
      <div
        v-if="isLoading"
        class="text-center text-gray-400"
      >
        {{ t('common.loading') }}
      </div>
      <div
        v-else-if="error"
        class="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-md"
      >
        <p class="font-bold">{{ t('common.error') }}</p>
        <p v-if="error === '來源規則與檔案名稱不匹配。'">{{ t('notifications.formValidation.parseNoMatch') }}</p>
        <p v-if="error === '發生未知錯誤。'">{{ t('notifications.unknownError') }}</p>
      </div>

      <!-- Results -->
      <div
        v-if="!error && !isLoading"
        class="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        <!-- Parsed Fields -->
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">{{ t('components.preview.parse.parsedFields') }}</h3>
          <div
            v-if="parsedFields && Object.keys(parsedFields).length > 0"
            class="bg-gray-900 p-4 rounded-md font-mono text-sm space-y-1"
          >
            <div
              v-for="(value, key) in parsedFields"
              :key="key"
              class="flex"
            >
              <span class="text-purple-400 mr-2">{{ key }}:</span>
              <span class="text-cyan-300">"{{ value }}"</span>
            </div>
          </div>
          <div
            v-else
            class="text-gray-400 italic"
          >
            {{ t('components.preview.parse.noFieldsParsed') }}
          </div>
        </div>

        <!-- Formatted Result -->
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">{{ t('components.preview.parse.result') }}</h3>
          <div class="bg-gray-900 p-4 rounded-md font-mono text-sm text-green-400 break-all">
            {{ formattedResult || t('components.preview.parse.noResult') }}
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="text-xs text-gray-500 bg-gray-800 p-3 rounded border">
        <div class="mb-2"><strong>{{ t('components.preview.parse.instructions.title') }}</strong></div>
        <ul class="space-y-1 list-disc list-inside">
          <li
            v-for="(node, index) in tm('components.preview.parse.instructions.lines')"
            :key="index"
          >
            {{ rt(node) }}
          </li>
        </ul>
        <div class="mt-3 pt-2 border-t border-gray-600">
          <div class="mb-1"><strong>{{ t('components.preview.parse.instructions.commonTypesTitle') }}</strong></div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-x-4 gap-y-1 text-xs">
            <div><code>{}</code> - {{ t('components.preview.parse.instructions.types.default') }}</div>
            <div><code>{:d}</code> - {{ t('components.preview.parse.instructions.types.integer') }}</div>
            <div><code>{:f}</code> - {{ t('components.preview.parse.instructions.types.float') }}</div>
            <div><code>{:s}</code> - {{ t('components.preview.parse.instructions.types.string') }}</div>
            <div><code>{:l}</code> - {{ t('components.preview.parse.instructions.types.lowercase') }}</div>
            <div><code>{:u}</code> - {{ t('components.preview.parse.instructions.types.uppercase') }}</div>
            <div><code>{:ts}</code> - {{ t('components.preview.parse.instructions.types.timestamp') }}</div>
          </div>
        </div>
        <div class="mt-3 pt-2 border-t border-gray-600">
          <i18n-t
            keypath="components.preview.parse.instructions.docsLink"
            tag="p"
          >
            <template #link>
              <a
                href="https://pypi.org/project/parse/"
                target="_blank"
                class="text-blue-400 hover:underline"
              >{{ t('components.preview.parse.instructions.officialDocs') }}</a>
            </template>
          </i18n-t>
        </div>
      </div>

    </CardContent>
  </Card>
</template>
