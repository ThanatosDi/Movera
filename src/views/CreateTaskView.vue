<script setup lang="js">
import RegexPreview from '@/components/RegexPreview.vue'
import TaskForm from '@/components/TaskForm.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useNotification } from '@/composables/useNotification'
import { useTasksStore } from '@/stores/tasks'
import { Save } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Composables
const router = useRouter()
const { notifyTaskCreated, notifySaveError } = useNotification()

// Store
const tasksStore = useTasksStore()

// Local State
const task = ref({
  name: '',
  include: '',
  move_to: '',
  src_filename_regex: '',
  dst_filename_regex: '',
  enabled: true,
})
const isSaving = ref(false)

// Methods
const validateForm = (taskData) => {
  if (!taskData.name?.trim()) {
    return '「任務名稱」為必填項。'
  }
  if (!taskData.include?.trim()) {
    return '「檔案名稱包含」為必填項。'
  }
  if (!taskData.move_to?.trim()) {
    return '「移動至」為必填項。'
  }
  // Regex to find characters that are invalid in paths on any common OS.
  // This prevents characters like < > : " | ? * and the null character.
  const invalidPathChars = /[<>:"|?*\x00]/;
  if (invalidPathChars.test(taskData.move_to)) {
    return '「移動至」包含無效的路徑字元(< > : " | ? *)。'
  }
  return null // No error
}

const createTask = async () => {
  const errorMessage = validateForm(task.value)
  if (errorMessage) {
    notifySaveError(errorMessage)
    return // Stop execution if validation fails
  }

  isSaving.value = true
  try {
    const newTask = await tasksStore.createTask(task.value)
    notifyTaskCreated()
    // 建立成功後導向到新任務的詳細頁面
    router.push({ name: 'taskDetail', params: { taskId: newTask.id } })
  } catch (error) {
    console.error('Failed to create task:', error)
    notifySaveError(error instanceof Error ? error.message : '建立任務失敗')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6`">
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
        <TaskForm v-model="task" />
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
      v-model:src-regex="task.src_filename_regex"
      v-model:dst-regex="task.dst_filename_regex"
    />
  </main>
</template>
