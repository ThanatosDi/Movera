<script setup lang="ts">
import { Badge } from '@/components/ui/badge';

defineProps({
  taskId: { type: String, required: true },
  taskName: { type: String, required: true },
  taskEnabled: { type: Boolean, required: true },
})
</script>

<template>
  <RouterLink
    v-slot="{ isActive, navigate }"
    :to="`/tasks/${taskId}`"
    custom
  >
    <div
      class="border-b border-gray-700 last:border-b-0"
      @click="navigate"
    >
      <div
        class="p-4 hover:bg-gray-700 cursor-pointer transition-colors"
        :class="{ 'bg-black border-l-4 rounded-l border-green-500': isActive }"
      >
        <div class="flex items-start gap-3">

          <!-- 任務內容 -->
          <div class="flex-1 min-w-0">
            <!-- 任務名稱和狀態 -->
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2 min-w-0">
                <Badge :class="taskEnabled
                  ? 'bg-green-600 hover:bg-green-600 text-white'
                  : 'bg-gray-600 hover:bg-gray-600 text-white'
                  ">
                  {{ taskEnabled ? '已啟動' : '未啟動' }}
                </Badge>
                <h3 class="text-white font-medium truncate">{{ taskName }}</h3>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </RouterLink>
</template>