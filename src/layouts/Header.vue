<script lang="ts" setup>
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { RoutersEnum } from '@/enums/RoutersEnum';
import { useTaskStore } from '@/stores/taskStore';
import { useDark, useToggle } from '@vueuse/core';
import { CircleUser, Home, Moon, Sun } from 'lucide-vue-next';
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

const { t } = useI18n()
const router = useRouter()

const isDark = useDark()
const toggleDark = useToggle(isDark)
const taskStore = useTaskStore()

onMounted(() => {
  taskStore.fetchTasks()
})

</script>

<template>
  <header class="border-b bg-background px-4 py-2">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link
          :to="RoutersEnum.Home"
          class="flex items-center gap-2 text-foreground hover:text-muted-foreground transition-colors"
        >
          <Home class="h-6 w-6" />
          <h1 class="text-lg font-semibold">Movera</h1>
        </router-link>
      </div>
      <div class="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          @click="toggleDark()"
        >
          <Moon
            v-if=!isDark
            class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
          />
          <Sun
            v-if=isDark
            class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
          />
          <span class="sr-only">Toggle theme</span>
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
              variant="ghost"
              size="icon"
              class="rounded-full"
            >
              <CircleUser class="h-6 w-6" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent class="w-56">
            <DropdownMenuLabel>Movera</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem @click="router.push(RoutersEnum.Setting)">
                <span>{{ t('common.settings') }}</span>
                <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  </header>
</template>
