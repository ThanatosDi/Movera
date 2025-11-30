<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  locale: {
    type: String,
    required: true,
    default: 'en',
  },
})

const emit = defineEmits(['update:locale'])

const selectedLocale = computed({
  get: () => props.locale,
  set: (value) => {
    emit('update:locale', value)
  },
})

const Locales = [
  { value: 'en', label: 'English' },
  { value: 'zh-TW', label: '繁體中文' },
]
</script>

<template>
  <Select v-model="selectedLocale">
    <SelectTrigger
      class="w-[180px] bg-background text-foreground border-foreground"
    >
      <SelectValue :placeholder="t('components.localeSelect.placeholder')" />
    </SelectTrigger>
    <SelectContent class="bg-background text-foreground">
      <SelectGroup>
        <SelectItem
          v-for="Local in Locales"
          :key="Local.value"
          :value="Local.value"
          class="hover:bg-gray-600"
        >
          {{ Local.label }}
        </SelectItem>
      </SelectGroup>
    </SelectContent>
  </Select>
</template>
