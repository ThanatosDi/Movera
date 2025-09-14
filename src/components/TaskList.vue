<script setup lang="ts">
import SidebarItem from '@/components/SidebarItem.vue';
import { useTaskStore } from '@/stores/taskStore';
import { Search } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';

const taskStore = useTaskStore();
const { tasks } = storeToRefs(taskStore);

</script>

<template>
  <div :class="`flex-1 overflow-y-auto bg-gray-800 rounded-md`">
    <!-- 空狀態 -->
    <div
      v-if="tasks.length === 0"
      class="p-4 text-center text-gray-400"
    >
      <div class="mb-2">
        <Search class="w-8 h-8 mx-auto opacity-50" />
      </div>
      <p class="text-sm">沒有找到符合條件的任務</p>
      <!-- <button
        v-if="hasActiveFilters"
        @click="$emit('clearAllFilters')"
        class="text-blue-400 hover:text-blue-300 text-xs mt-2 underline transition-colors"
        type="button"
      >
        清除所有過濾條件
      </button> -->
    </div>

    <!-- 任務列表 -->
    <SidebarItem
      v-for="task in tasks"
      :key="task.id"
      :taskId="task.id"
      :taskName="task.name"
      :taskEnabled="task.enabled"
    />
  </div>
</template>