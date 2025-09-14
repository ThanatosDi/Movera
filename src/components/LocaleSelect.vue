<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Locales } from '@/constants'
import { computed } from 'vue'

const props = defineProps({
  locale: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:locale'])

const selectedLocale = computed({
  get: () => props.locale,
  set: (value) => {
    emit('update:locale', value)
  },
})
</script>

<template>
  <Select
    v-model="selectedLocale"
    class="bg-gray-700 border-gray-600"
  >
    <SelectTrigger class="w-[180px]">
      <SelectValue placeholder="選擇語言" />
    </SelectTrigger>
    <SelectContent class="bg-gray-700 border-gray-600 text-white">
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
