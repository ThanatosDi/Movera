<script setup lang="js">
import IconAdd from '@/components/icons/IconAdd.vue'
import IconHome from '@/components/icons/IconHome.vue'
import IconSettings from '@/components/icons/IconSettings.vue'
import IconTasks from '@/components/icons/IconTasks.vue'
import Header from '@/layout/Header.vue'
import Sidebar from '@/layout/Sidebar.vue'
import { RouterLink, RouterView } from 'vue-router'

import { useApiStore } from '@/stores/api'
import { useTasksStore } from '@/stores/tasks'
import { onMounted } from 'vue'

// // 初始化 stores
const apiStore = useApiStore()
const tasksStore = useTasksStore()

onMounted(async () => {
  // 初始化 API 配置
  apiStore.initialize()

  // 載入初始數據
  await tasksStore.initialize()
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
          to="/"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconHome class="size-6" />
          <span class="text-xs">首頁</span>
        </RouterLink>
        <RouterLink
          to="/tasks"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconTasks class="size-6" />
          <span class="text-xs">任務</span>
        </RouterLink>
        <RouterLink
          to="/create"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconAdd class="size-6" />
          <span class="text-xs">新增</span>
        </RouterLink>
        <RouterLink
          to="/settings"
          class="flex flex-col items-center text-gray-400 hover:text-white"
        >
          <IconSettings class="size-6" />
          <span class="text-xs">設定</span>
        </RouterLink>
      </nav>
    </footer>
  </div>
</template>
