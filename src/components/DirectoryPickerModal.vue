<script setup lang="ts">
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useDirectoryBrowser } from '@/composables/useDirectoryBrowser'
import type { DirectoryItem } from '@/schemas'
import { ChevronRight, Folder, Loader2 } from 'lucide-vue-next'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'select', path: string): void
}>()

const { directories, loading, fetchDirectories } = useDirectoryBrowser()

const currentPath = ref<string | undefined>(undefined)
const breadcrumbs = ref<{ name: string; path: string }[]>([])

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      currentPath.value = undefined
      breadcrumbs.value = []
      fetchDirectories(undefined)
    }
  },
  { immediate: true }
)

function navigateToDirectory(dir: DirectoryItem) {
  currentPath.value = dir.path
  breadcrumbs.value.push({ name: dir.name, path: dir.path })
  fetchDirectories(dir.path)
}

function navigateToBreadcrumb(index: number) {
  if (index < 0) {
    // 回到根目錄
    currentPath.value = undefined
    breadcrumbs.value = []
    fetchDirectories(undefined)
  } else {
    const crumb = breadcrumbs.value[index]!
    currentPath.value = crumb.path
    breadcrumbs.value = breadcrumbs.value.slice(0, index + 1)
    fetchDirectories(crumb.path)
  }
}

function confirmSelection() {
  if (currentPath.value) {
    emit('select', currentPath.value)
    emit('update:open', false)
  }
}

function cancel() {
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="(v: boolean) => emit('update:open', v)">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('components.directoryPicker.title') }}</DialogTitle>
        <DialogDescription>{{ t('components.directoryPicker.description') }}</DialogDescription>
      </DialogHeader>

      <!-- 麵包屑導航 -->
      <div class="flex items-center gap-1 text-sm text-foreground/70 flex-wrap">
        <button
          data-testid="breadcrumb-item"
          class="hover:text-foreground cursor-pointer transition-colors"
          @click="navigateToBreadcrumb(-1)"
        >
          {{ t('components.directoryPicker.root') }}
        </button>
        <template v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
          <ChevronRight class="size-3 text-foreground/40" />
          <button
            data-testid="breadcrumb-item"
            class="hover:text-foreground cursor-pointer transition-colors"
            @click="navigateToBreadcrumb(index)"
          >
            {{ crumb.name }}
          </button>
        </template>
      </div>

      <!-- 目錄列表 -->
      <div class="min-h-[200px] max-h-[400px] overflow-y-auto border border-foreground/20 rounded-md bg-background">
        <!-- 載入中 -->
        <div
          v-if="loading"
          data-testid="loading-indicator"
          class="flex items-center justify-center p-8 text-foreground"
        >
          <Loader2 class="size-6 animate-spin" />
        </div>

        <!-- 目錄列表 -->
        <div v-else-if="directories.length > 0" class="divide-y divide-foreground/10">
          <button
            v-for="dir in directories"
            :key="dir.path"
            data-testid="directory-item"
            class="w-full flex items-center gap-2 p-3 hover:bg-foreground/10 text-foreground text-left cursor-pointer transition-colors"
            @click="navigateToDirectory(dir)"
          >
            <Folder class="size-4 text-foreground/60 shrink-0" />
            <span class="flex-1 truncate">{{ dir.name }}</span>
            <ChevronRight v-if="dir.has_children" class="size-4 text-foreground/40" />
          </button>
        </div>

        <!-- 空目錄/未設定 -->
        <div
          v-else
          data-testid="empty-message"
          class="flex items-center justify-center p-8 text-foreground/50 text-sm"
        >
          <template v-if="breadcrumbs.length === 0 && !currentPath">
            {{ t('components.directoryPicker.noAllowedDirectories') }}
          </template>
          <template v-else>
            {{ t('components.directoryPicker.emptyDirectory') }}
          </template>
        </div>
      </div>

      <!-- 目前選擇的路徑 -->
      <div v-if="currentPath" class="text-sm text-foreground">
        <span class="text-foreground/60">{{ t('components.directoryPicker.selected') }}:</span>
        <span class="ml-1 font-mono text-green-400">{{ currentPath }}</span>
      </div>

      <DialogFooter>
        <Button
          data-testid="cancel-btn"
          variant="outline"
          class="border-foreground"
          @click="cancel"
        >
          {{ t('common.cancel') }}
        </Button>
        <Button
          data-testid="confirm-btn"
          :disabled="!currentPath"
          class="bg-green-400 hover:bg-green-800 text-black"
          @click="confirmSelection"
        >
          {{ t('components.directoryPicker.confirm') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
