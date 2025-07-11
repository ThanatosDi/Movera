<script setup lang="ts">
defineProps({
  TaskName: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: false
  }
});
</script>

<template>
  <div class="flex-1 overflow-y-auto">
    <router-link :to="`/services/${TaskName}`"
      class="p-4 flex justify-between items-center hover:bg-gray-700 cursor-pointer"
      :class="active ? 'bg-gray-800' : 'hover:bg-gray-700'">
      <span class="text-lg">{{ `${TaskName}` }}</span>
    </router-link>
  </div>
</template>
