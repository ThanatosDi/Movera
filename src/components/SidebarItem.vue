<script setup lang="ts">
import { ref, watch } from 'vue'
import { Badge } from '@/components/ui/badge'

const props = defineProps({
  TaskName: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false
  },
  showCheckbox: {
    type: Boolean,
    default: false
  },
  tags: {
    type: Array,
    default: () => []
  },
  status: {
    type: String,
    default: '100%'
  },
  description: {
    type: String,
    default: ''
  },
  isSelected: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:selected'])

const localSelected = ref(props.isSelected)

// 監聽 props 變化
watch(() => props.isSelected, (newValue) => {
  localSelected.value = newValue
})

// 處理選擇狀態變化
const handleSelectionChange = () => {
  emit('update:selected', props.TaskName, localSelected.value)
}

const tagColors = {
  '媒體': 'bg-purple-600',
  '串流': 'bg-blue-600',
  '開源': 'bg-green-600',
  '下載': 'bg-orange-600',
  '自動化': 'bg-cyan-600',
  'BT': 'bg-red-600',
  '動漫': 'bg-pink-600',
  '電影': 'bg-yellow-600',
  '整理': 'bg-indigo-600'
}

const getTagColor = (tag) => {
  return tagColors[tag] || 'bg-gray-600'
}
</script>

<template>
  <div class="border-b border-gray-700 last:border-b-0">
    <div
      class="p-4 hover:bg-gray-700 cursor-pointer transition-colors"
      :class="active ? 'bg-gray-700' : ''"
    >

      <div class="flex items-start gap-3">
        <!-- Checkbox (when enabled) -->
        <!-- Checkbox (when enabled) -->
        <div v-if="showCheckbox" class="flex-shrink-0 pt-1">
          <input 
            type="checkbox" 
            v-model="localSelected"
            @change="handleSelectionChange"
            class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
          />
        </div>

        <!-- Task content -->
        <div class="flex-1 min-w-0">
          <router-link :to="`/services/${TaskName}`" class="block">
            <!-- Task name and status -->
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-white font-medium truncate">{{ TaskName }}</h3>
              <span class="text-xs text-gray-400 flex-shrink-0 ml-2">{{ status }}</span>
            </div>

            <!-- Description -->
            <p v-if="description" class="text-sm text-gray-400 mb-2 line-clamp-2">
              {{ description }}
            </p>

            <!-- Tags -->
            <div v-if="tags && tags.length > 0" class="flex flex-wrap gap-1">
              <Badge 
                v-for="tag in tags" 
                :key="tag"
                :class="[getTagColor(tag), 'text-white text-xs px-2 py-0.5']"
              >
                {{ tag }}
              </Badge>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>