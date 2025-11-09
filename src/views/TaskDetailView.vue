<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Play, RefreshCw, Save, Square, Trash2 } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
// 假資料
const isLoading = false
const isSaving = false
const isLoadingLogs = false
const task = {
  id: '5454a5d46as4d65as4da4d',
  name: '範例任務一',
  enabled: true,
}
const logs = [
  {
    id: '5454a5d46as4d65as4da4d',
    timestamp: '2024-01-01 12:00:00',
    level: 'INFO',
    message: '任務執行成功',
  },
]


</script>

<template>
  <main :class="`flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6`">
    <div
      v-if="isLoading"
      class="flex items-center justify-center h-full"
    >
      <!-- <p>{{ UI_CONSTANTS.LOADING_TEXT }}</p> -->
    </div>

    <div v-else-if="task">
      <div class="mb-4">
        <h1 class="text-2xl font-bold">{{ task.name }}</h1>
        <p class="text-gray-400">{{ t('taskDetailView.taskId') }}: {{ task.id }}</p>
      </div>

      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center space-x-2">
          <!-- 啟用/停用按鈕 -->
          <Button
            v-if="!task.enabled"
            @click="btnActionToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-green-500 hover:bg-green-600 text-black font-bold"
          >
            <Play class="size-4 mr-2" />
            {{ t('taskDetailView.enableButton') }}
          </Button>
          <Button
            v-if="task.enabled"
            @click="btnActionToggleTaskStatus"
            :disabled="isSaving"
            size="sm"
            class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold"
          >
            <Square class="size-4 mr-2" />
            {{ t('taskDetailView.disableButton') }}
          </Button>
          <!-- 刪除按鈕 -->
          <AlertDialog>
            <AlertDialogTrigger as-child>
              <Button
                :disabled="isSaving"
                variant="destructive"
                size="sm"
                class="bg-red-500 hover:bg-red-600 text-white font-bold"
              >
                <Trash2 class="size-4 mr-2" />
                {{ t('common.delete') }}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent class="bg-gray-800 border-gray-700 text-white">
              <AlertDialogHeader>
                <AlertDialogTitle>{{ t('taskDetailView.deleteDialogTitle') }}</AlertDialogTitle>
                <AlertDialogDescription class="text-current">
                  {{ t('taskDetailView.deleteDialogDesc', { taskName: task.name }) }}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel class="hover:bg-stone-400 text-black">{{ t('common.cancel') }}</AlertDialogCancel>
                <AlertDialogAction
                  class="bg-green-400 hover:bg-green-800 text-black"
                  @click="btnActionDeleteTask"
                >{{ t('common.continue') }}</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      <Card class="bg-gray-800 border-gray-700 text-white">
        <CardHeader>
          <CardTitle>{{ t('taskDetailView.cardTitle') }}</CardTitle>
          <CardDescription>{{ t('taskDetailView.cardDescription') }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <TaskForm
            v-model="task"
            :isRenameRuleRequired="isRenameRuleRequired ?? false"
          />
          <div class="flex justify-end">
            <Button
              @click="btnActionUpdateTask"
              :disabled="isSaving"
              class="bg-blue-500 hover:bg-blue-600 font-bold text-white"
            >
              <Save class="size-4 mr-2" />
              {{ isSaving ? t('common.saving') : t('taskDetailView.saveChanges') }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card
        ref="logCard"
        class="mt-4 bg-gray-800 border-gray-700 text-white"
      >
        <CardHeader class="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{{ t('taskDetailView.logsTitle') }}</CardTitle>
            <CardDescription>{{ t('taskDetailView.logsDescription') }}</CardDescription>
          </div>
          <Button
            @click="btnActionFetchLogs"
            :disabled="isLoadingLogs"
            size="sm"
            variant="outline"
            class="bg-gray-700 hover:bg-gray-600"
          >
            <RefreshCw
              class="size-4 mr-2"
              :class="{ 'animate-spin': isLoadingLogs }"
            />
            {{ isLoadingLogs ? t('common.loading') : t('common.reload') }}
          </Button>
        </CardHeader>
        <CardContent class="space-y-2">
          <div
            v-if="isLoadingLogs"
            class="text-center text-gray-400 py-4"
          >
            <p>{{ t('taskDetailView.loadingLogs') }}</p>
          </div>
          <div
            v-else-if="logs.length > 0"
            class="space-y-2"
          >
            <ScrollArea class="h-72 rounded-md">
              <LogItem
                v-for="log in logs"
                :key="log.id"
                :timestamp="log.timestamp"
                :level="log.level"
                :message="log.message"
              />
            </ScrollArea>
          </div>
          <div
            v-else
            class="text-center text-gray-400 py-4"
          >
            <p>{{ t('taskDetailView.noLogs') }}</p>
          </div>
        </CardContent>
      </Card>
    </div>

    <div
      v-else
      class="flex items-center justify-center h-full"
    >
      <div class="text-center text-gray-400">
        <p class="text-lg mb-2">{{ t('taskDetailView.taskNotFound') }}</p>
        <p class="text-sm">{{ t('taskDetailView.checkTaskId') }}</p>
      </div>
    </div>
  </main>
</template>
