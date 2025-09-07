<script setup lang="ts">
import IconAdd from '@/components/icons/IconAdd.vue'
import IconHome from '@/components/icons/IconHome.vue'
import IconSettings from '@/components/icons/IconSettings.vue'
import IconTasks from '@/components/icons/IconTasks.vue'
import { Route } from '@/constants'
import Header from '@/layout/Header.vue'
import Sidebar from '@/layout/Sidebar.vue'
import { useTaskStore } from '@/stores/taskStore'
import { onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const taskStore = useTaskStore()

onMounted(async () => {
  // 載入初始數據
  await taskStore.fetchTasks()
})
</script>

<template>
  <div class="h-screen bg-gray-900 text-white flex flex-col">
    <Header />
    <div class="flex flex-1 overflow-hidden">
      <Sidebar />
      <main class="flex-1 p-4 overflow-y-auto">
        <RouterView />
      </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <footer class="sm:hidden bg-gray-800 p-2">
      <nav class="flex justify-around">
        <RouterLink
          :to="Route.HOME"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconHome class="size-6" />
          <span class="text-xs">首頁</span>
        </RouterLink>
        <RouterLink
          :to="Route.TASKS"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconTasks class="size-6" />
          <span class="text-xs">任務</span>
        </RouterLink>
        <RouterLink
          :to="Route.CREATE_TASK"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconAdd class="size-6" />
          <span class="text-xs">新增</span>
        </RouterLink>
        <RouterLink
          :to="Route.SETTING"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconSettings class="size-6" />
          <span class="text-xs">設定</span>
        </RouterLink>
      </nav>
    </footer>
  </div>
</template>
