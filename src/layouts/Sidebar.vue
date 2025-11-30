<script setup lang="ts">
// import { useTaskStore } from '@/stores/taskStore';
import SidebarItem from '@/components/SidebarItem.vue';
import SidebarTool from '@/components/SidebarTool.vue';
import { useTaskStore } from '@/stores/taskStore';
import { Search } from 'lucide-vue-next';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const taskStore = useTaskStore()
const { tasks } = storeToRefs(taskStore)

</script>

<template>
  <aside class="hidden sm:flex flex-col w-90 p-4 rounded-lg mr-4">
    <SidebarTool />
    <!-- <nav class="flex flex-col space-y-2"> -->
    <nav class="flex-1 overflow-y-auto bg-sidebar rounded-b-md">
      <!-- <div :class="`flex-1 overflow-y-auto bg-gray-800 rounded-md`"> -->
      <!-- 空狀態 -->
      <div
        v-if="tasks.length === 0"
        class="p-4 text-center"
      >
        <div class="mb-2">
          <Search class="w-8 h-8 mx-auto opacity-50" />
        </div>
        <p class="text-sm">{{ t('common.emptyTasks') }}</p>
      </div>

      <!-- 任務列表 -->
      <SidebarItem
        v-for="task in tasks"
        :key="task.id"
        :taskId="task.id"
        :taskName="task.name"
        :taskEnabled="task.enabled"
      />
      <!-- </div> -->
    </nav>
  </aside>
</template>
