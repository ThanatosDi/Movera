<script setup lang="ts">
import ParsePreview from '@/components/ParsePreview.vue'
import RegexPreview from '@/components/RegexPreview.vue'
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useNotification } from '@/composables/useNotification'
import type { TaskCreate } from '@/schemas'
import { useTaskStore } from '@/stores/taskStore'
import { Save, X } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()

// Composables
const router = useRouter()

// Store
const tasksStore = useTaskStore()

// Local State
const task = ref<TaskCreate>({
  name: '',
  include: '',
  move_to: '',
  rename_rule: null,
  src_filename: null,
  dst_filename: null,
  enabled: true,
})
const isSaving = ref<boolean>(false)

const isRenameRuleRequired = computed(() => {
  return task.value.rename_rule !== null
})

const clearRenameRules = () => {
  task.value.src_filename = null
  task.value.dst_filename = null
}

const validFormData = (taskData: TaskCreate) => {
  if (!taskData.name?.trim()) {
    return t('notifications.formValidation.taskNameRequired')
  }
  if (!taskData.include?.trim()) {
    return t('notifications.formValidation.includeRequired')
  }
  if (!taskData.move_to?.trim()) {
    return t('notifications.formValidation.moveToRequired')
  }
  const invalidPathChars = /[<>:"|?*\x00]/;
  if (invalidPathChars.test(taskData.move_to)) {
    return t('notifications.formValidation.invalidPath')
  }
  if (taskData.rename_rule !== null && (!taskData.src_filename?.trim() || !taskData.dst_filename?.trim())) {
    return t('notifications.formValidation.renameRuleRequired', { rule: taskData.rename_rule })
  }
  return null // No error
}

const createTask = async () => {
  const errorMessage = validFormData(task.value)
  if (errorMessage) {
    useNotification.showError(t('notifications.taskCreateErrorTitle'), errorMessage, { html: true, position: 'top-center', duration: 2000 })
    return
  }

  isSaving.value = true
  try {
    const newTask = await tasksStore.createTask(task.value)
    router.push({ name: 'taskDetail', params: { taskId: newTask.id } })
    useNotification.showSuccess(t('notifications.taskCreateSuccessTitle'), t('notifications.taskCreateSuccessDesc', { taskName: newTask.name }))
  } catch (e: any) {
    console.error('Failed to create task:', e)
    useNotification.showError(t('notifications.taskCreateErrorTitle'), e.message)
  } finally {
    isSaving.value = false
  }
}

</script>

<template>
  <main class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6`">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('views.createTask.title') }}</h1>
      <p class="text-gray-400">{{ t('views.createTask.description') }}</p>
    </div>

    <!-- 任務設定卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle>{{ t('views.createTask.cardTitle') }}</CardTitle>
        <CardDescription>{{ t('views.createTask.cardDescription') }}</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <TaskForm
          v-model="task"
          :isRenameRuleRequired="isRenameRuleRequired"
        />
        <!-- 按鈕區域 -->
        <div class="flex justify-between items-center">
          <!-- 清除規則按鈕 -->
          <Button
            v-if="isRenameRuleRequired"
            @click="clearRenameRules"
            type="button"
            variant="destructive"
          >
            <X class="size-4 mr-2" />
            {{ t('views.createTask.clearRulesButton') }}
          </Button>
          <!-- 佔位符，確保建立按鈕在右邊 -->
          <div v-else></div>
          <!-- 建立按鈕 -->
          <Button
            @click="createTask"
            :disabled="isSaving"
            class="bg-green-400 hover:bg-green-800 font-bold text-black"
          >
            <Save class="size-4 mr-2" />
            {{ isSaving ? t('views.createTask.creatingButton') : t('views.createTask.createButton') }}
          </Button>
        </div>
      </CardContent>
    </Card>
    <!-- 正規表達式預覽 -->
    <RegexPreview
      v-if="task.rename_rule === 'regex'"
      v-model:src-filename="task.src_filename"
      v-model:dst-filename="task.dst_filename"
    />
    <!-- 檔案名稱解析預覽 -->
    <ParsePreview
      v-if="task.rename_rule === 'parse'"
      v-model:src-filename="task.src_filename"
      v-model:dst-filename="task.dst_filename"
    />

  </main>
</template>
