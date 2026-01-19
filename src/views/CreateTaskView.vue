<script setup lang="ts">
import ParsePreview from '@/components/ParsePreview.vue'
import RegexPreview from '@/components/RegexPreview.vue'
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useNotification } from '@/composables/useNotification'
import type { TaskCreate } from '@/schemas'
import { useTaskStore } from '@/stores/taskStore'
import { useSessionStorage } from '@vueuse/core'
import { Save, X } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()
const tasksStore = useTaskStore()
const isSaving = ref<boolean>(false)
const error_message = ref<string>('')

const regexTestFilename = useSessionStorage('regexPreview:testFilename', '')
const parseTestFilename = useSessionStorage('parsePreview:testFilename', '')

const createTaskData = ref<TaskCreate>({
  name: '',
  include: '',
  move_to: '',
  rename_rule: null,
  src_filename: null,
  dst_filename: null,
  enabled: true,
})


const isRenameRuleRequired = computed(() => {
  return createTaskData.value.rename_rule !== null
})

const clearRenameRules = () => {
  createTaskData.value.src_filename = null
  createTaskData.value.dst_filename = null
  regexTestFilename.value = ''
  parseTestFilename.value = ''
}

const btnActionCreateTask = async () => {
  isSaving.value = true
  try {
    // useSessionStorage('parsePreview:testFilename', '')
    const response = await tasksStore.createTask(createTaskData.value)
    router.push({ name: 'taskDetail', params: { taskId: response.id } })
    useNotification.showSuccess(
      t('notifications.taskCreateSuccessTitle'),
      t('notifications.taskCreateSuccessDesc', { taskName: response.name }))
  } catch (e: unknown) {
    console.error(t('errors.failedToCreateTask'), e)
    const wsError = e as { error?: string; message?: string }
    if (wsError.error === 'TaskAlreadyExists') {
      error_message.value = t('exceptions.TaskAlreadyExists', { taskName: createTaskData.value.name })
    } else {
      error_message.value = wsError.message || (e as Error).message || 'Unknown error'
    }
    useNotification.showError(t('notifications.taskCreateErrorTitle'), error_message.value)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <main class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6`">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('createTaskView.title') }}</h1>
      <p class="text-gray-400">{{ t('createTaskView.description') }}</p>
    </div>

    <!-- 任務設定卡片 -->
    <Card class="bg-card text-foreground normal-border">
      <CardHeader>
        <CardTitle>{{ t('createTaskView.cardTitle') }}</CardTitle>
        <CardDescription>{{ t('createTaskView.cardDescription') }}</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <TaskForm
          v-model="createTaskData"
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
            class="dark:bg-red-500 dark:hover:bg-red-600 text-white font-bold"
          >
            <X class="size-4 mr-2" />
            {{ t('createTaskView.clearRulesButton') }}
          </Button>
          <!-- 佔位符，確保建立按鈕在右邊 -->
          <div v-else></div>
          <!-- 建立按鈕 -->
          <Button
            @click="btnActionCreateTask"
            :disabled="isSaving"
            class="bg-green-400 hover:bg-green-800 font-bold text-black"
          >
            <Save class="size-4 mr-2" />
            {{ isSaving ? t('createTaskView.creatingButton') : t('createTaskView.createButton') }}
          </Button>
        </div>
      </CardContent>
    </Card>
    <!-- 正規表達式預覽 -->
    <RegexPreview
      v-if="createTaskData.rename_rule === 'regex'"
      v-model:src-filename="createTaskData.src_filename"
      v-model:dst-filename="createTaskData.dst_filename"
    />
    <!-- 檔案名稱解析預覽 -->
    <ParsePreview
      v-if="createTaskData.rename_rule === 'parse'"
      v-model:src-filename="createTaskData.src_filename"
      v-model:dst-filename="createTaskData.dst_filename"
    />

  </main>
</template>
