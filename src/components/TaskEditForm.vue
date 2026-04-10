<script setup lang="ts">
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { Task } from '@/schemas'
import { Save } from 'lucide-vue-next'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  modelValue: Task
  isSaving: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Task): void
  (e: 'save'): void
}>()

const task = computed({
  get: () => props.modelValue,
  set: (value: Task) => emit('update:modelValue', value)
})

const isRenameRuleRequired = computed(() => {
  return task.value.rename_rule !== null
})

const handleSave = () => {
  emit('save')
}
</script>

<template>
  <Card class="border border-border">
    <CardHeader>
      <CardTitle>{{ t('taskDetailView.taskCardTitle') }}</CardTitle>
      <CardDescription>{{ t('taskDetailView.taskCardDescription') }}</CardDescription>
    </CardHeader>
    <CardContent class="space-y-4">
      <TaskForm
        v-model="task"
        :isRenameRuleRequired="isRenameRuleRequired"
      />
      <div class="flex justify-end">
        <Button
          @click="handleSave"
          :disabled="isSaving"
          class="bg-blue-500 hover:bg-blue-600 font-bold text-white"
        >
          <Save class="size-4 mr-2" />
          {{ isSaving ? t('common.saving') : t('taskDetailView.saveChanges') }}
        </Button>
      </div>
    </CardContent>
  </Card>
</template>
