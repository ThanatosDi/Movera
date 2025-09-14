<script setup lang="ts">
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Textarea } from '@/components/ui/textarea'
import { computed } from 'vue'

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
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 名稱 -->
      <div class="space-y-2">
        <Label for="name">任務名稱<span class="text-red-500">*</span></Label>
        <Input
          id="name"
          v-model="task.name"
          class="bg-gray-700 border-gray-600"
        />
      </div>

      <!-- 包含 -->
      <div class="space-y-2">
        <Label for="include">檔案名稱包含<span class="text-red-500">*</span></Label>
        <Input
          id="include"
          v-model="task.include"
          class="bg-gray-700 border-gray-600"
        />
      </div>
    </div>

    <!-- 移動至 -->
    <div class="space-y-2">
      <Label for="move_to">移動至 (Move To)<span class="text-red-500">*</span></Label>
      <Input
        id="move_to"
        v-model="task.move_to"
        class="bg-gray-700 border-gray-600"
      />
    </div>

    <!-- 重新命名規則 -->
    <Label for="rename_rule">重新命名規則 (Rename Rule)<span class="text-red-500">*</span></Label>
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
        <Label for="r1">不重新命名</Label>
      </div>
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r2"
          value="regex"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500"
        />
        <Label for="r2">正規表示 Regex</Label>
      </div>
      <div class="flex items-center space-x-2">
        <RadioGroupItem
          id="r3"
          value="parse"
          class="data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500 data-[state=checked]:text-green-500"
        />
        <Label for="r3">模板解析 Parse</Label>
      </div>
    </RadioGroup>

    <!-- 來源檔名規則 -->
    <div class="space-y-2">
      <Label for="src_filename">
        來源檔名規則 (Src Filename)
        <span
          v-if="isRenameRuleRequired"
          class="text-red-500"
        >*</span>
      </Label>
      <Input
        id="src_filename"
        v-model="task.src_filename"
        class="bg-gray-700 border-gray-600"
      />
    </div>

    <!-- 目標檔名規則 -->
    <div class="space-y-2">
      <Label for="dst_filename">
        目標檔名規則 (Dst Filename)
        <span
          v-if="isRenameRuleRequired"
          class="text-red-500"
        >*</span>
      </Label>
      <Textarea
        id="dst_filename"
        v-model="task.dst_filename"
        class="bg-gray-700 border-gray-600"
      />
    </div>
  </div>
</template>
