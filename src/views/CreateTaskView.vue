<script setup lang="ts">
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

const createTask = async () => {
  isSaving.value = true
  try {
    await tasksStore.createTask(task.value)
  } catch (e: any) {
    console.error('Failed to create task:', e)
    useNotification.showError('建立任務失敗', e.message)
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
    <!-- <RegexPreview
      v-model:src-regex="task.src_filename_regex"
      v-model:dst-regex="task.dst_filename_regex"
    /> -->
  </main>
</template>
