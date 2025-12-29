<script lang="ts" setup>
import { Button } from '@/components/ui/button';
import { useTaskStore } from '@/stores/taskStore';
import { CheckSquare, Play, Square, StopCircle, Trash2 } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n()
const taskStore = useTaskStore()
const { isSelectMode, tasks, selectedTaskIds } = storeToRefs(taskStore)

// 直接從 selectedTaskIds 計算選中數量，確保響應性
const selectedCount = computed(() => selectedTaskIds.value.size)

const handleBatchDelete = async () => {
  await taskStore.batchDelete()
}

const handleBatchEnable = async () => {
  await taskStore.batchEnable()
}

const handleBatchDisable = async () => {
  await taskStore.batchDisable()
}
</script>

<template>
  <div class="bg-sidebar p-4 rounded-t-md space-y-3">
    <!-- 工具列 -->
    <div class="flex items-center gap-2">
      <!-- 選擇模式切換按鈕 -->
      <Button
        variant="outline"
        size="sm"
        :class="[
          'flex-1 transition-colors dark:border-white/50 dark:hover:border-white',
          isSelectMode
            ? 'bg-blue-600 hover:bg-blue-700 text-white border-blue-600'
            : ''
        ]"
        @click="taskStore.toggleSelectMode()"
        :disabled="tasks.length === 0"
      >
        <CheckSquare v-if="isSelectMode" class="w-4 h-4 mr-2" />
        <Square v-else class="w-4 h-4 mr-2" />
        {{ isSelectMode ? t('components.sidebarTool.exitSelectMode') : t('components.sidebarTool.selectMode') }}
      </Button>

      <!-- 全選按鈕 (選擇模式下顯示) -->
      <Button
        v-if="isSelectMode"
        variant="outline"
        size="sm"
        class="dark:border-white/50 dark:hover:border-white"
        @click="taskStore.selectAllTasks()"
      >
        {{ selectedCount === tasks.length ? t('components.sidebarTool.deselectAll') : t('components.sidebarTool.selectAll') }}
      </Button>
    </div>

    <!-- 批量操作按鈕 (選擇模式且有選中項目時顯示) -->
    <div
      v-if="isSelectMode && selectedCount > 0"
      class="flex items-center gap-2 p-2 bg-sidebar-accent rounded-md"
    >
      <span class="text-sm text-muted-foreground flex-1">
        {{ t('components.sidebarTool.selectedCount', { count: selectedCount }) }}
      </span>
      <Button
        variant="ghost"
        size="sm"
        class="text-green-500 hover:text-green-400 hover:bg-green-500/10"
        @click="handleBatchEnable"
        :title="t('components.sidebarTool.batchEnable')"
      >
        <Play class="w-4 h-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        class="text-yellow-500 hover:text-yellow-400 hover:bg-yellow-500/10"
        @click="handleBatchDisable"
        :title="t('components.sidebarTool.batchDisable')"
      >
        <StopCircle class="w-4 h-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        class="text-red-500 hover:text-red-400 hover:bg-red-500/10"
        @click="handleBatchDelete"
        :title="t('components.sidebarTool.batchDelete')"
      >
        <Trash2 class="w-4 h-4" />
      </Button>
    </div>
  </div>
</template>
