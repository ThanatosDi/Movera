<script setup>
import { useRoute, useRouter } from 'vue-router'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
const router = useRouter()
const route = useRoute()

const services = ['emby', 'jellyfin', 'pangolin', 'qbittorrent']

// function goToService(TaskName) {
//     router.push(`/services/${TaskName}`)
// }
</script>

<template>
    <div class="h-screen bg-gray-900 text-white flex flex-col">
        <Header />
        <div class="flex flex-1 p-4 min-h-0">
            <!-- Sidebar -->
            <Sidebar />
            <!-- Content -->
            <router-view />
        </div>
    </div>
</template>