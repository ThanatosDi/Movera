<script setup lang="ts">
import SidebarItem from '@/components/SidebarItem.vue';
import { useTaskStore } from '@/stores/taskStore';
import { Search } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';

const taskStore = useTaskStore()
const { tasks } = storeToRefs(taskStore)
</script>

<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto pb-6">
    <!-- 頁面標題 -->
    <div class="pt-2 pb-2">
      <h1 class="text-2xl font-bold">任務清單</h1>
      <p class="text-gray-400">管理所有已建立的任務</p>
    </div>

    <!-- 任務列表容器 -->
    <div class="flex-1 overflow-y-auto bg-gray-800 rounded-md p-2">
      <!-- 空狀態 -->
      <div
        v-if="tasks.length === 0"
        class="p-4 text-center text-gray-400 flex flex-col items-center justify-center h-full"
      >
        <div class="mb-2">
          <Search class="w-12 h-12 mx-auto opacity-50" />
        </div>
        <p class="text-lg">沒有找到符合條件的任務</p>
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
