<script setup lang="ts">
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Route } from '@/constants';
import { Plus, Search } from 'lucide-vue-next';

</script>

<template>
  <!-- 新增任務按鈕 -->
  <div class="pt-2 pb-4 col-span-1 col-start-1">
    <RouterLink
      :to="Route.CREATE_TASK"
      class="text-gray-500 hover:text-gray-300 text-base"
    >
      <Button
        class="bg-green-400 hover:bg-green-500 text-base text-black font-bold py-2 px-4 rounded-full w-full transition-colors"
      >
        <Plus class="w-4 h-4 mr-2" />新增任務
      </Button>
    </RouterLink>
  </div>
  <div class="space-y-3 pb-4">
    <!-- 搜尋框 -->
    <div class="relative">
      <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
      <Input
        placeholder="搜尋任務..."
        class="pl-10 bg-gray-800 border-gray-600 text-white placeholder-gray-400"
      />
    </div>
  </div>
</template>