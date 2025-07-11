<script setup>
import { Plus } from 'lucide-vue-next'
import { ref } from 'vue'
import SidebarItem from './SidebarItem.vue'
import { Button } from './ui/button'

const selected = ref(null)

const services = [
    { name: 'Emby', status: '100%' },
    { name: 'Jellyfin', status: '100%' },
    { name: 'Pangolin', status: '100%' },
    { name: 'qbittorrent', status: '100%' }
]
</script>

<template>
    <aside class="w-128 bg-gray-900 p-4 flex flex-col min-h-0">
        <div class="pt-2 pb-4 col-span-1 col-start-1">
            <router-link to="/create" class="text-gray-500 hover:text-gray-300 text-base">
                <Button class="bg-green-400 hover:bg-green-400 text-base text-black font-bold py-2 px-4 rounded-full">
                    <Plus class="w-4 h-4 mr-2" />新增任務
                </Button>
            </router-link>
        </div>

        <div class="flex-1 overflow-y-auto bg-gray-800 rounded-md">
            <SidebarItem v-for="(item, index) in services" :key="item.name" :TaskName="item.name" />
        </div>
    </aside>
</template>
