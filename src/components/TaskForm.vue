<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import DirectoryPickerModal from '@/components/DirectoryPickerModal.vue'
import PresetRuleModal from '@/components/PresetRuleModal.vue'
import TagSelector from '@/components/TagSelector.vue'
import { useTagStore } from '@/stores/tagStore'
import { FileCode, FolderOpen } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n();

const tagStore = useTagStore()
const { tags: availableTags } = storeToRefs(tagStore)
tagStore.fetchTags()

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
  isRenameRuleRequired: {
    type: Boolean,
    default: false,
  },
  availableGroups: {
    type: Array as () => string[],
    default: () => [],
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// Computed property to proxy the modelValue
const task = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const renameRuleProxy = computed({
  get: () => task.value.rename_rule === null ? 'null' : task.value.rename_rule,
  set: (value) => {
    task.value.rename_rule = value === 'null' ? null : value
  }
})

const autoGrow = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  target.style.height = 'auto'
  target.style.height = `${target.scrollHeight}px`
}

// Directory picker modal state
const isDirectoryPickerOpen = ref(false)

// Preset rule modal state
const isPresetRuleModalOpen = ref(false)
const presetRuleFieldType = ref<'src' | 'dst'>('src')

function openPresetRuleModal(fieldType: 'src' | 'dst') {
  presetRuleFieldType.value = fieldType
  isPresetRuleModalOpen.value = true
}

function handlePresetRuleSelect(pattern: string) {
  if (presetRuleFieldType.value === 'src') {
    task.value.src_filename = pattern
  } else {
    task.value.dst_filename = pattern
  }
  emit('update:modelValue', { ...task.value })
}

function handleDirectorySelect(path: string) {
  task.value.move_to = path
  emit('update:modelValue', { ...task.value, move_to: path })
}

// 從 src_filename pattern 解析出可用的 group 名稱
const computedAvailableGroups = computed<string[]>(() => {
  const src = task.value.src_filename
  const rule = task.value.rename_rule
  if (!src || !rule) return []

  if (rule === 'parse') {
    // 提取 {groupname} 格式的 group（排除格式指定符如 {episode:02d}）
    const matches = src.matchAll(/\{([a-zA-Z_]\w*)(?::[^}]*)?\}/g)
    return [...matches].map(m => m[1])
  }

  if (rule === 'regex') {
    // 提取 (?P<groupname>...) 格式的 named group
    const matches = src.matchAll(/\(\?P<([a-zA-Z_]\w*)>/g)
    return [...matches].map(m => m[1])
  }

  return []
})

// 合併 props 傳入的 groups 與自動計算的 groups
const mergedAvailableGroups = computed(() => {
  const fromProps = props.availableGroups ?? []
  const fromPattern = computedAvailableGroups.value
  const combined = new Set([...fromPattern, ...fromProps])
  return [...combined]
})

const tagIds = computed(() => task.value.tag_ids ?? task.value.tags?.map((t: { id: string }) => t.id) ?? [])

function handleTagIdsUpdate(value: string[]) {
  emit('update:modelValue', { ...task.value, tag_ids: value })
}

const episodeOffsetEnabled = computed({
  get: () => task.value.episode_offset_enabled ?? false,
  set: (value: boolean | 'indeterminate' | null) => {
    task.value.episode_offset_enabled = value === true
  }
})

function handleOffsetGroupChange(value: string) {
  task.value.episode_offset_group = value
}

</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 名稱 -->
      <div class="space-y-2">
        <Label for="name">{{ t('components.taskForm.name') }}<span class="text-red-500">*</span></Label>
        <Textarea
          id="name"
          v-model="task.name"
          class="resize-none min-h-0 py-2 px-3 overflow-hidden border-foreground"
          rows="1"
          @input="autoGrow"
          @keydown.enter.prevent
        />
      </div>

      <!-- 包含 -->
      <div class="space-y-2">
        <Label for="include">{{ t('components.taskForm.include') }}<span class="text-red-500">*</span></Label>
        <Textarea
          id="include"
          v-model="task.include"
          class="resize-none min-h-0 py-2 px-3 overflow-hidden border-foreground"
          rows="1"
          @input="autoGrow"
          @keydown.enter.prevent
        />
      </div>
    </div>

    <!-- 移動至 -->
    <div class="space-y-2">
      <Label for="move_to">{{ t('components.taskForm.moveTo') }}<span class="text-red-500">*</span></Label>
      <div class="flex gap-2">
        <Input
          id="move_to"
          v-model="task.move_to"
          class="flex-1 border-foreground"
          :placeholder="t('components.taskForm.moveToPlaceholder')"
          @input="emit('update:modelValue', { ...task, move_to: ($event.target as HTMLInputElement).value })"
        />
        <Button
          data-testid="browse-btn"
          type="button"
          variant="outline"
          class="border-foreground shrink-0"
          @click="isDirectoryPickerOpen = true"
        >
          <FolderOpen class="size-4 mr-1" />
          {{ t('components.taskForm.browse') }}
        </Button>
      </div>
    </div>

    <!-- Directory Picker Modal -->
    <DirectoryPickerModal
      v-model:open="isDirectoryPickerOpen"
      @select="handleDirectorySelect"
    />

    <!-- 標籤選擇器 -->
    <TagSelector
      :available-tags="availableTags"
      :model-value="tagIds"
      @update:model-value="handleTagIdsUpdate"
    />

    <!-- 重新命名規則 -->
    <Label for="rename_rule">{{ t('components.taskForm.renameRule') }}<span class="text-red-500">*</span></Label>
    <RadioGroup
      v-model="renameRuleProxy"
      :orientation="'vertical'"
    >
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r1"
          value="null"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500 border-foreground"
        />
        <Label for="r1">{{ t('components.taskForm.renameRuleOptions.noRename') }}</Label>
      </div>
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r2"
          value="regex"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500 border-foreground"
        />
        <Label for="r2">{{ t('components.taskForm.renameRuleOptions.regex') }}</Label>
      </div>
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r3"
          value="parse"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500 border-foreground"
        />
        <Label for="r3">{{ t('components.taskForm.renameRuleOptions.parse') }}</Label>
      </div>
    </RadioGroup>

    <!-- 來源檔名規則 -->
    <div
      v-if="isRenameRuleRequired"
      class="space-y-2"
    >
      <Label for="src_filename">
        {{ t('components.taskForm.srcFilename') }}
        <span
          v-if="isRenameRuleRequired"
          class="text-red-500"
        >*</span>
      </Label>
      <div class="flex gap-2">
        <Textarea
          id="src_filename"
          v-model="task.src_filename"
          class="flex-1 resize-none min-h-0 py-2 px-3 overflow-hidden border-foreground"
          rows="1"
          @input="autoGrow"
          @keydown.enter.prevent
        />
        <Button
          type="button"
          variant="outline"
          class="border-foreground shrink-0"
          data-testid="preset-rule-src-btn"
          @click="openPresetRuleModal('src')"
        >
          <FileCode class="size-4" />
        </Button>
      </div>
    </div>

    <!-- 目標檔名規則 -->
    <div
      v-if="isRenameRuleRequired"
      class="space-y-2"
    >
      <Label for="dst_filename">
        {{ t('components.taskForm.dstFilename') }}
        <span
          v-if="isRenameRuleRequired"
          class="text-red-500"
        >*</span>
      </Label>
      <div class="flex gap-2">
        <Textarea
          id="dst_filename"
          v-model="task.dst_filename"
          class="flex-1 resize-none min-h-0 py-2 px-3 overflow-hidden border-foreground"
          rows="1"
          @input="autoGrow"
          @keydown.enter.prevent
        />
        <Button
          type="button"
          variant="outline"
          class="border-foreground shrink-0"
          data-testid="preset-rule-dst-btn"
          @click="openPresetRuleModal('dst')"
        >
          <FileCode class="size-4" />
        </Button>
      </div>
    </div>

    <!-- Episode 偏移設定 -->
    <div
      v-if="isRenameRuleRequired"
      data-testid="episode-offset-section"
      class="space-y-3 rounded-md border border-foreground/20 p-4"
    >
      <div class="flex items-center space-x-2">
        <Checkbox
          id="episode_offset_enabled"
          data-testid="episode-offset-enabled"
          v-model="episodeOffsetEnabled"
        />
        <Label for="episode_offset_enabled" class="cursor-pointer">
          {{ t('components.taskForm.episodeOffset.enabled') }}
        </Label>
      </div>
      <p class="text-xs text-muted-foreground">
        {{ t('components.taskForm.episodeOffset.description') }}
      </p>

      <div
        v-if="episodeOffsetEnabled"
        class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2"
      >
        <!-- Group 選擇 -->
        <div class="space-y-2">
          <Label for="episode_offset_group">
            {{ t('components.taskForm.episodeOffset.group') }}
          </Label>
          <Select
            :model-value="task.episode_offset_group ?? undefined"
            @update:model-value="handleOffsetGroupChange"
          >
            <SelectTrigger
              id="episode_offset_group"
              data-testid="episode-offset-group"
              class="border-foreground"
            >
              <SelectValue :placeholder="t('components.taskForm.episodeOffset.groupPlaceholder')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="group in mergedAvailableGroups"
                :key="group"
                :value="group"
              >
                {{ group }}
              </SelectItem>
            </SelectContent>
          </Select>
          <p
            v-if="mergedAvailableGroups.length === 0"
            class="text-xs text-muted-foreground"
          >
            {{ t('components.taskForm.episodeOffset.groupEmpty') }}
          </p>
        </div>

        <!-- 偏移量 -->
        <div class="space-y-2">
          <Label for="episode_offset_value">
            {{ t('components.taskForm.episodeOffset.value') }}
          </Label>
          <Input
            id="episode_offset_value"
            data-testid="episode-offset-value"
            type="number"
            class="border-foreground"
            v-model.number="task.episode_offset_value"
          />
        </div>
      </div>
    </div>

    <!-- Preset Rule Modal -->
    <PresetRuleModal
      v-if="task.rename_rule"
      v-model:open="isPresetRuleModalOpen"
      :rule-type="task.rename_rule"
      :field-type="presetRuleFieldType"
      @select="handlePresetRuleSelect"
    />
  </div>
</template>
