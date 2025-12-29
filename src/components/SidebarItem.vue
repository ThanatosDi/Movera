<script lang="ts" setup>
import { Badge } from '@/components/ui/badge';
import { useTaskStore } from '@/stores/taskStore';
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps({
  taskId: { type: String, required: true },
  taskName: { type: String, required: true },
  taskEnabled: { type: Boolean, required: true },
})

const { t } = useI18n();
const taskStore = useTaskStore()
const { isSelectMode, selectedTaskIds } = storeToRefs(taskStore)

const isSelected = computed(() => selectedTaskIds.value.has(props.taskId))

const handleClick = (navigate: () => void) => {
  if (isSelectMode.value) {
    taskStore.toggleTaskSelection(props.taskId)
  } else {
    navigate()
  }
}
</script>

<template>
  <RouterLink
    v-slot="{ isActive, navigate }"
    :to="`/tasks/${taskId}`"
    custom
  >
    <div
      class="border-b border-gray-700 last:border-b-0"
      @click="handleClick(navigate)"
    >
      <div
        class="p-4 sidebar-item-hover cursor-pointer transition-colors"
        :class="[
          { 'bg-background text-frontend border-l-4 rounded-l border-green-500': isActive && !isSelectMode },
          { 'bg-blue-600/20': isSelected && isSelectMode }
        ]"
      >
        <div class="flex items-center gap-3">
          <!-- Checkbox (選擇模式下顯示) -->
          <div
            v-if="isSelectMode"
            class="flex items-center pointer-events-none"
          >
            <div
              class="size-4 shrink-0 rounded-[4px] border shadow-xs transition-all"
              :class="isSelected
                ? 'bg-primary border-primary text-primary-foreground'
                : 'border-input bg-transparent'"
            >
              <svg
                v-if="isSelected"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="size-3.5"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
          </div>

          <!-- 任務內容 -->
          <div class="flex-1 min-w-0">
            <!-- 任務名稱和狀態 -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2 min-w-0">
                <!-- 狀態 -->
                <Badge :class="taskEnabled
                  ? 'bg-green-600 hover:bg-green-600 text-white'
                  : 'bg-gray-600 hover:bg-gray-600 text-white'
                  ">
                  {{ taskEnabled ? t('common.enabled') : t('common.disabled') }}
                </Badge>
                <!-- 名稱 -->
                <h3
                  class="font-medium"
                  :title="taskName"
                >{{ taskName }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </RouterLink>
</template>
