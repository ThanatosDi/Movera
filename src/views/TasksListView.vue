<script setup lang="ts">
import SidebarItem from '@/components/SidebarItem.vue';
import { useTaskStore } from '@/stores/taskStore';
import { Search } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const taskStore = useTaskStore()
const { tasks } = storeToRefs(taskStore)
</script>

<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6 bg-background text-foreground">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">{{ t('tasksListView.title') }}</h1>
      <p class="text-gray-400">{{ t('tasksListView.description') }}</p>
    </div>

    <!-- 任務列表容器 -->
    <div class="flex-1 overflow-y-auto bg-sidebar rounded-md p-2">
      <!-- 空狀態 -->
      <div
        v-if="tasks.length === 0"
        class="p-4 text-center text-gray-400 flex flex-col items-center justify-center h-full"
      >
        <div class="mb-2">
          <Search class="w-12 h-12 mx-auto opacity-50" />
        </div>
        <p class="text-lg">{{ t('common.emptyTasks') }}</p>
      </div>

      <!-- 任務列表 -->
      <SidebarItem
        v-else
        v-for="task in tasks"
        :key="task.id"
        :taskId="task.id"
        :taskName="task.name"
        :taskEnabled="task.enabled"
      />
    </div>
  </main>
</template>
