<script setup>
defineProps({
  TaskName: String
})
</script>


<template>
  <main class="flex-1 flex flex-col p-4 space-y-4 overflow-auto">
    <div class="pt-2 pb-2 col-span-1 col-start-1">
      <h1 class="text-2xl">{{ TaskName }}</h1>
      <p class="text-green-500">Docker container: {{ TaskName }}</p>
    </div>
    <div class="flex justify-between items-center">
      <div class="space-x-2">
        <button class="bg-gray-700 px-2 py-1 rounded">暫停</button>
        <button class="bg-gray-700 px-2 py-1 rounded">編輯</button>
        <button class="bg-gray-700 px-2 py-1 rounded">複製</button>
        <button class="bg-red-600 px-2 py-1 rounded">刪除</button>
      </div>
    </div>

    <div class="bg-gray-800 p-4 rounded">
      <div class="flex flex-wrap gap-1">
        <div
          v-for="n in 50"
          :key="n"
          class="w-2 h-6 bg-green-500 rounded"
        ></div>
      </div>
      <div class="text-green-500 mt-2">正常</div>
    </div>

    <div class="grid grid-cols-4 gap-4">
      <div class="bg-gray-800 p-4 rounded text-center">
        <div class="text-sm">Ping (目前)</div>
        <div class="text-blue-400">N/A</div>
      </div>
      <div class="bg-gray-800 p-4 rounded text-center">
        <div class="text-sm">平均 Ping (24 小時)</div>
        <div class="text-blue-400">N/A</div>
      </div>
      <div class="bg-gray-800 p-4 rounded text-center">
        <div class="text-sm">運作率 (24 小時)</div>
        <div class="text-green-400">100%</div>
      </div>
      <div class="bg-gray-800 p-4 rounded text-center">
        <div class="text-sm">運作率 (30 天)</div>
        <div class="text-green-400">98.97%</div>
      </div>
    </div>
  </main>
</template>
