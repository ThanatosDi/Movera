<script setup lang="js">
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { computed } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// Computed property to proxy the modelValue
const task = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
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

    <!-- 來源檔名規則 -->
    <div class="space-y-2">
      <Label for="src_filename_regex">來源檔名規則 (Regex)</Label>
      <Input
        id="src_filename_regex"
        v-model="task.src_filename_regex"
        class="bg-gray-700 border-gray-600"
      />
    </div>

    <!-- 目標檔名規則 -->
    <div class="space-y-2">
      <Label for="dst_filename_regex">目標檔名規則 (Regex)</Label>
      <Textarea
        id="dst_filename_regex"
        v-model="task.dst_filename_regex"
        class="bg-gray-700 border-gray-600"
      />
    </div>
  </div>
</template>
