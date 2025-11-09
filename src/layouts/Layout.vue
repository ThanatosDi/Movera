<script setup lang="ts">
import IconAdd from '@/components/icons/IconAdd.vue'
import IconHome from '@/components/icons/IconHome.vue'
import IconSettings from '@/components/icons/IconSettings.vue'
import IconTasks from '@/components/icons/IconTasks.vue'
import { RoutersEnum } from '@/enums/RoutersEnum'
import Header from '@/layouts/Header.vue'
import Sidebar from '@/layouts/Sidebar.vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, RouterView } from 'vue-router'

const { t } = useI18n()
</script>

<template>
  <div class="h-screen flex flex-col bg-background text-foreground">
    <Header />
    <div class="flex flex-1 overflow-hidden">
      <Sidebar />
      <main class="flex-1 p-4 overflow-y-auto">
        <RouterView />
      </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <footer class="sm:hidden bg-card border-t p-2">
      <nav class="flex justify-around">
        <RouterLink
          :to="RoutersEnum.Home"
          class="flex flex-col items-center text-muted-foreground hover:text-foreground"
        >
          <IconHome class="size-6" />
          <span class="text-xs">{{ t('common.home') }}</span>
        </RouterLink>
        <RouterLink
          :to="RoutersEnum.Tasks"
          class="flex flex-col items-center text-muted-foreground hover:text-foreground"
        >
          <IconTasks class="size-6" />
          <span class="text-xs">{{ t('common.tasks') }}</span>
        </RouterLink>
        <RouterLink
          :to="RoutersEnum.CreateTask"
          class="flex flex-col items-center text-muted-foreground hover:text-foreground"
        >
          <IconAdd class="size-6" />
          <span class="text-xs">{{ t('common.create') }}</span>
        </RouterLink>
        <RouterLink
          :to="RoutersEnum.Setting"
          class="flex flex-col items-center text-muted-foreground hover:text-foreground"
        >
          <IconSettings class="size-6" />
          <span class="text-xs">{{ t('common.settings') }}</span>
        </RouterLink>
      </nav>
    </footer>
  </div>
</template>