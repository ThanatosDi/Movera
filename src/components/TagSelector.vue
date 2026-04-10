<script lang="ts" setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Tag } from '@/schemas'
import TagBadge from './TagBadge.vue'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ChevronDown, X } from 'lucide-vue-next'

const props = defineProps<{
  availableTags: Tag[]
  modelValue: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const { t } = useI18n()

const selectedTags = computed(() =>
  props.availableTags.filter(tag => props.modelValue.includes(tag.id))
)

function toggleTag(tagId: string) {
  const current = [...props.modelValue]
  const index = current.indexOf(tagId)
  if (index === -1) {
    current.push(tagId)
  } else {
    current.splice(index, 1)
  }
  emit('update:modelValue', current)
}

function removeTag(tagId: string) {
  emit('update:modelValue', props.modelValue.filter(id => id !== tagId))
}
</script>

<template>
  <div class="space-y-2">
    <label class="text-sm font-medium">{{ t('components.tagSelector.label') }}</label>
    <div class="flex flex-wrap items-center gap-2">
      <TagBadge
        v-for="tag in selectedTags"
        :key="tag.id"
        :name="tag.name"
        :color="tag.color"
        class="cursor-pointer"
        @click="removeTag(tag.id)"
      >
        <template #default>
          <span class="flex items-center gap-1">
            {{ tag.name }}
            <X class="w-3 h-3" />
          </span>
        </template>
      </TagBadge>

      <DropdownMenu>
        <DropdownMenuTrigger as-child>
          <Button variant="outline" size="sm" class="h-7 text-xs">
            {{ t('components.tagSelector.placeholder') }}
            <ChevronDown class="w-3 h-3 ml-1" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent class="w-48">
          <DropdownMenuLabel>{{ t('components.tagSelector.label') }}</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <template v-if="availableTags.length > 0">
            <DropdownMenuCheckboxItem
              v-for="tag in availableTags"
              :key="tag.id"
              :model-value="modelValue.includes(tag.id)"
              @update:model-value="toggleTag(tag.id)"
            >
              <TagBadge :name="tag.name" :color="tag.color" />
            </DropdownMenuCheckboxItem>
          </template>
          <div v-else class="px-2 py-1.5 text-sm text-muted-foreground">
            {{ t('components.tagSelector.empty') }}
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  </div>
</template>
