<script lang="ts" setup>
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { RoutersEnum } from '@/enums/RoutersEnum'
import { WebSocketService } from '@/services/websocketService'
import { useDark, useToggle } from '@vueuse/core'
import { Circle, CircleUser, GitBranch, Home, LoaderCircle, Moon, Sun, X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()
const { status: websocketStatus, data } = WebSocketService()

const isDark = useDark()
const toggleDark = useToggle(isDark)

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
          class="text-muted-foreground hover:text-foreground"
        >
          連接狀態
          <Circle
            v-if="websocketStatus == 'OPEN'"
            class="ml-2 h-3 w-3 text-green-500"
          />
          <X
            v-if="websocketStatus == 'CLOSED'"
            class="ml-2 h-3 w-3 text-red-500"
          />
          <LoaderCircle
            v-if="websocketStatus == 'CONNECTING'"
            class="ml-2 h-3 w-3 animate-spin text-yellow-500"
          />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          class="text-muted-foreground hover:text-foreground"
        >
          <GitBranch class="mr-2 h-4 w-4" />
          {{ t('common.status') }}
        </Button>
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