<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useParsePreview } from '@/composables/useParsePreview'
import { useSessionStorage } from '@vueuse/core'
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
// 使用 localStorage 持久化測試檔名，即使重新整理頁面也會保留
const testFilename = useSessionStorage('parsePreview:testFilename', '')

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
const { groups, formattedResult, error } = useParsePreview(
  testFilename,
  srcPattern,
  dstPattern
)

// Load test case handler
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
      <CardTitle>{{ t('components.parsePreview.title') }}</CardTitle>
      <CardDescription>{{ t('components.parsePreview.description') }}</CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <!-- Inputs -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="test-filename">{{ t('components.parsePreview.testFilename') }}</Label>
          <Textarea
            id="test-filename"
            v-model="testFilename"
            class="text-foreground bg-background border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />

        </div>
        <div class="space-y-2">
          <Label for="src-rule">{{ t('components.parsePreview.sourcePattern') }}</Label>
          <Textarea
            id="src-rule"
            v-model="srcPattern"
            placeholder="{title}.S{season:02d}E{episode:02d}.{extension}"
            class="text-foreground bg-background border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
        <div class="space-y-2 col-span-full">
          <!-- Test case buttons -->
          <!-- <div class="mt-2 flex flex-wrap gap-2">
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
          </div> -->
        </div>
        <div class="space-y-2 col-span-full">
          <Label for="dst-rule">{{ t('components.parsePreview.destinationPattern') }}</Label>
          <Textarea
            id="dst-rule"
            v-model="dstPattern"
            placeholder="{title} S{season:02d}E{episode:02d}.{extension}"
            class="text-foreground bg-background border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
            readonly
            rows="1"
            @input="autoGrow"
            @keydown.enter.prevent
          />
        </div>
      </div>

      <!-- Loading and Error Display -->
      <!-- <div
        v-if="isLoading"
        class="text-center text-gray-400"
      >
        {{ t('common.loading') }}
      </div> -->
      <div
        v-if="error"
        class="bg-red-900/50 border border-red-500 text-red-300 px-4 py-3 rounded-md"
      >
        <p class="font-bold">{{ t('common.error') }}</p>
        <p>{{ t(error) }}</p>
      </div>

      <!-- Results -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        <!-- Parsed Fields -->
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">{{ t('components.parsePreview.groups') }}</h3>
          <div
            v-if="groups && Object.keys(groups).length > 0"
            class="text-foreground bg-background p-4 rounded-md border font-mono text-sm space-y-1"
          >
            <div
              v-for="(value, key) in groups"
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
            {{ t('components.parsePreview.withoutGroups') }}
          </div>
        </div>

        <!-- Formatted Result -->
        <div class="space-y-2">
          <h3 class="font-semibold text-lg">{{ t('components.parsePreview.result') }}</h3>
          <div class="text-chart-2 bg-background border p-4 rounded-md font-mono text-sm break-all">
            {{ formattedResult || t('components.parsePreview.noResult') }}
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="text-s text-ring bg-background p-3 rounded border">
        <div class="mb-2"><strong>{{ t('components.parsePreview.instructions.title') }}</strong></div>
        <ul class="space-y-1 list-disc list-inside">
          <li
            v-for="(node, index) in tm('components.parsePreview.instructions.lines')"
            :key="index"
          >
            {{ rt(node) }}
          </li>
        </ul>
        <div class="mt-3 pt-2 border-t border-gray-600">
          <div class="mb-1"><strong>{{ t('components.parsePreview.instructions.commonTypesTitle') }}</strong></div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-x-4 gap-y-1 text-xs">
            <div><code>{}</code> - {{ t('components.parsePreview.instructions.types.default') }}</div>
            <div><code>{:d}</code> - {{ t('components.parsePreview.instructions.types.integer') }}</div>
            <div><code>{:f}</code> - {{ t('components.parsePreview.instructions.types.float') }}</div>
            <div><code>{:s}</code> - {{ t('components.parsePreview.instructions.types.string') }}</div>
            <div><code>{:l}</code> - {{ t('components.parsePreview.instructions.types.lowercase') }}</div>
            <div><code>{:u}</code> - {{ t('components.parsePreview.instructions.types.uppercase') }}</div>
            <div><code>{:ts}</code> - {{ t('components.parsePreview.instructions.types.timestamp') }}</div>
          </div>
        </div>
        <div class="mt-3 pt-2 border-t border-gray-600">
          <i18n-t
            keypath="components.parsePreview.instructions.docsLink"
            tag="p"
          >
            <template #link>
              <a
                href="https://pypi.org/project/parse/"
                target="_blank"
                class="text-blue-400 hover:underline"
              >{{ t('components.parsePreview.instructions.officialDocs') }}</a>
            </template>
          </i18n-t>
        </div>
      </div>

    </CardContent>
  </Card>
</template>
