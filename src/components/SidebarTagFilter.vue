<script setup lang="ts">
import { useTagStore } from '@/stores/tagStore'
import { useTaskStore } from '@/stores/taskStore'
import { ChevronDown, ChevronRight } from 'lucide-vue-next'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const tagStore = useTagStore()
const taskStore = useTaskStore()
const { tags } = storeToRefs(tagStore)
const { selectedFilterTagIds } = storeToRefs(taskStore)

const isExpanded = ref(true)

const selectedCount = computed(() => selectedFilterTagIds.value.size)

const colorClasses: Record<string, string> = {
  red: 'bg-red-500/20 text-red-400 border-red-500/30',
  orange: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  green: 'bg-green-500/20 text-green-400 border-green-500/30',
  blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  pink: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  gray: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

function isSelected(tagId: string) {
  return selectedFilterTagIds.value.has(tagId)
}
</script>

<template>
  <div
    v-if="tags.length > 0"
    data-testid="sidebar-tag-filter"
    class="mb-2"
  >
    <!-- 標題列 -->
    <button
      data-testid="filter-header"
      class="flex items-center justify-between w-full px-3 py-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      @click="isExpanded = !isExpanded"
    >
      <span class="flex items-center gap-1">
        <component :is="isExpanded ? ChevronDown : ChevronRight" class="w-3.5 h-3.5" />
        {{ t('components.sidebarTagFilter.title') }}
      </span>
      <span v-if="!isExpanded && selectedCount > 0" class="text-xs opacity-70">
        {{ t('components.sidebarTagFilter.selected', { count: selectedCount }) }}
      </span>
    </button>

    <!-- Tag 列表 -->
    <div v-if="isExpanded" class="flex flex-wrap gap-1.5 px-3 pb-2">
      <button
        v-for="tag in tags"
        :key="tag.id"
        data-testid="filter-tag"
        :class="[
          'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border cursor-pointer transition-all',
          colorClasses[tag.color] || colorClasses.gray,
          isSelected(tag.id) ? 'ring-2 ring-white/30 opacity-100' : 'opacity-50 hover:opacity-75',
        ]"
        @click="taskStore.toggleFilterTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>
  </div>
</template>
