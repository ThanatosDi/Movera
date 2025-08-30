<script setup lang="js">
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
import { CircleUser, GitBranch, Home } from 'lucide-vue-next';
</script>

<template>
  <header class="border-b bg-gray-900 px-4 py-2">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link
          :to="`/`"
          class="flex items-center gap-2 text-white hover:text-gray-300 transition-colors"
        >
          <Home class="h-6 w-6" />
          <h1 class="text-lg font-semibold">Movera</h1>
        </router-link>
      </div>
      <div class="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          class="text-gray-300 hover:text-white"
        >
          <GitBranch class="mr-2 h-4 w-4" />
          狀態頁
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
              <DropdownMenuItem>
                <span>設定</span>
                <DropdownMenuShortcut>⇧⌘P</DropdownMenuShortcut>
              </DropdownMenuItem>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  </header>
</template>