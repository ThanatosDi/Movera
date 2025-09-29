<script setup lang="ts">
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from '@/components/ui/textarea'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n();

// Props
const props = defineProps({
  /**
   * task 物件，由 TaskDetailView 的 v-model 導入
   * @type {Object}
   * @required
   */
  modelValue: {
    type: Object,
    required: true,
  },
  /**
   * 是否需要重新命名規則
   * @type {Boolean}
   * @default false
   */
  isRenameRuleRequired: {
    type: Boolean,
    default: false,
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// Computed property to proxy the modelValue
const task = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

/**
 * 計算屬性：renameRuleProxy
 * 作為 task.value.rename_rule 的雙向代理
 *
 * 當取得值時，如果 task.value.rename_rule 是 null(object)，則返回 'null'(string)
 * 否則返回原始值
 *
 * 當設定值時，如果新值是 'null'(string)，則設定 task.value.rename_rule 為 null(object)
 * 否則設定為新值
 */
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
          class="bg-gray-700 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
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
          class="bg-gray-700 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
          rows="1"
          @input="autoGrow"
          @keydown.enter.prevent
        />
      </div>
    </div>

    <!-- 移動至 -->
    <div class="space-y-2">
      <Label for="move_to">{{ t('components.taskForm.moveTo') }}<span class="text-red-500">*</span></Label>
      <Textarea
        id="move_to"
        v-model="task.move_to"
        class="bg-gray-700 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
        rows="1"
        @input="autoGrow"
        @keydown.enter.prevent
      />
    </div>

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
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500"
        />
        <Label for="r1">{{ t('components.taskForm.options.noRename') }}</Label>
      </div>
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r2"
          value="regex"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500"
        />
        <Label for="r2">{{ t('components.taskForm.options.regex') }}</Label>
      </div>
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r3"
          value="parse"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500"
        />
        <Label for="r3">{{ t('components.taskForm.options.parse') }}</Label>
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
      <Textarea
        id="src_filename"
        v-model="task.src_filename"
        class="bg-gray-700 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
        rows="1"
        @input="autoGrow"
        @keydown.enter.prevent
      />
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
      <Textarea
        id="dst_filename"
        v-model="task.dst_filename"
        class="bg-gray-700 border-gray-600 resize-none min-h-0 py-2 px-3 overflow-hidden"
        rows="1"
        @input="autoGrow"
        @keydown.enter.prevent
      />
    </div>
  </div>
</template>