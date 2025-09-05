<script setup lang="ts">
import RegexPreview from '@/components/RegexPreview.vue'
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useNotification } from '@/composables/useNotification'
import type { TaskCreate } from '@/schemas'
import { useTaskStore } from '@/stores/taskStore'
import { Save } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

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

const validFormData = (taskData: TaskCreate) => {
  if (!taskData.name?.trim()) {
    return '任務名稱為必填項。'
  }
  if (!taskData.include?.trim()) {
    return '檔案名稱包含為必填項。'
  }
  if (!taskData.move_to?.trim()) {
    return '移動至為必填項。'
  }
  const invalidPathChars = /[<>:"|?*\x00]/;
  if (invalidPathChars.test(taskData.move_to)) {
    return '移動至包含無效的路徑字元(< > : " | ? *)。'
  }
  if (taskData.rename_rule !== null && (!taskData.src_filename?.trim() || !taskData.dst_filename?.trim())) {
    return `以啟用重新命名: ${taskData.rename_rule} 但未設定<br/> - 來源檔名規則<br/> - 目標檔名規則`
  }
  return null // No error
}

const createTask = async () => {
  const errorMessage = validFormData(task.value)
  if (errorMessage) {
    useNotification.showError('建立任務失敗', errorMessage, { html: true, position: 'top-center', duration: 2000 })
    return
  }

  isSaving.value = true
  try {
    const newTask = await tasksStore.createTask(task.value)
    router.push({ name: 'taskDetail', params: { taskId: newTask.id } })
    useNotification.showSuccess('任務已建立', `任務 "${newTask.name}" 已成功建立。`)
  } catch (e: any) {
    console.error('Failed to create task:', e)
    useNotification.showError('建立任務失敗', e.message)
  } finally {
    isSaving.value = false
  }
}

</script>

<template>
  <main class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6`">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">建立任務</h1>
      <p class="text-gray-400">設定自動化檔案管理任務</p>
    </div>

    <!-- 任務設定卡片 -->
    <Card class="bg-gray-800 border-gray-700 text-white">
      <CardHeader>
        <CardTitle>任務設定</CardTitle>
        <CardDescription>在這裡編輯任務的詳細設定。</CardDescription>
      </CardHeader>
      <CardContent class="space-y-4">
        <TaskForm
          v-model="task"
          :isRenameRuleRequired="isRenameRuleRequired"
        />
        <!-- 建立按鈕 -->
        <div class="flex justify-end">
          <Button
            @click="createTask"
            :disabled="isSaving"
            class="bg-green-400 hover:bg-green-800 font-bold text-black"
          >
            <Save class="size-4 mr-2" />
            {{ isSaving ? '建立中...' : '建立任務' }}
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
  </main>
</template>
