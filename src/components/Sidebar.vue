<script setup>
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Filter, Plus, Search, X } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import SidebarItem from './SidebarItem.vue'

const selected = ref(null)

// 工具欄狀態
const showCheckboxes = ref(false)
const searchQuery = ref('')
const selectedTags = ref([])

// 模擬任務數據（包含標籤）
const services = [
    {
        name: 'Emby',
        status: '100%',
        tags: ['媒體', '串流'],
        description: 'Emby 媒體伺服器'
    },
    {
        name: 'Jellyfin',
        status: '100%',
        tags: ['媒體', '串流', '開源'],
        description: 'Jellyfin 媒體伺服器'
    },
    {
        name: 'Pangolin',
        status: '100%',
        tags: ['下載', '自動化'],
        description: 'Pangolin 下載管理'
    },
    {
        name: 'qbittorrent',
        status: '100%',
        tags: ['下載', 'BT'],
        description: 'qBittorrent 下載器'
    },
    {
        name: '動漫下載任務',
        status: '85%',
        tags: ['動漫', '下載', '自動化'],
        description: '自動下載動漫任務'
    },
    {
        name: '電影整理任務',
        status: '92%',
        tags: ['電影', '整理', '媒體'],
        description: '電影檔案整理任務'
    }
]

// 所有可用的標籤
const availableTags = computed(() => {
    const allTags = services.flatMap(service => service.tags)
    return [...new Set(allTags)].sort()
})

// 過濾後的任務列表
const filteredServices = computed(() => {
    let filtered = services

    // 根據搜尋查詢過濾
    if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(service =>
            service.name.toLowerCase().includes(query) ||
            service.description.toLowerCase().includes(query) ||
            service.tags.some(tag => tag.toLowerCase().includes(query))
        )
    }

    // 根據選中的標籤過濾
    if (selectedTags.value.length > 0) {
        filtered = filtered.filter(service =>
            selectedTags.value.every(tag => service.tags.includes(tag))
        )
    }

    return filtered
})

// 顯示模式選項
const displayModeOptions = [
    { value: 'normal', label: '一般模式' },
    { value: 'checkbox', label: '選擇模式' }
]

// 切換顯示模式
const toggleDisplayMode = (mode) => {
    showCheckboxes.value = mode === 'checkbox'
}

// 添加標籤到過濾器
const addTagFilter = (tag) => {
    if (!selectedTags.value.includes(tag)) {
        selectedTags.value.push(tag)
    }
}

// 移除標籤過濾器
const removeTagFilter = (tag) => {
    selectedTags.value = selectedTags.value.filter(t => t !== tag)
}

// 清除所有過濾條件
const clearAllFilters = () => {
    searchQuery.value = ''
    selectedTags.value = []
    showCheckboxes.value = false
}

// 檢查是否有任何過濾條件
const hasActiveFilters = computed(() => {
    return searchQuery.value.trim() !== '' || selectedTags.value.length > 0
})
</script>

<template>
    <aside class="w-128 bg-gray-900 p-4 flex flex-col min-h-0">
        <!-- 新增任務按鈕 -->
        <div class="pt-2 pb-4 col-span-1 col-start-1">
            <router-link
                to="/create"
                class="text-gray-500 hover:text-gray-300 text-base"
            >
                <Button class="bg-green-400 hover:bg-green-400 text-base text-black font-bold py-2 px-4 rounded-full">
                    <Plus class="w-4 h-4 mr-2" />新增任務
                </Button>
            </router-link>
        </div>

        <!-- 工具欄 -->
        <div class="bg-gray-800 rounded-md p-3 mb-3 space-y-3">
            <!-- 第一行：顯示模式切換 + 搜尋框 -->
            <div class="flex items-center gap-3">
                <!-- 顯示模式切換 -->
                <div class="flex-shrink-0">
                    <Select @update:model-value="toggleDisplayMode">
                        <SelectTrigger class="w-32 bg-gray-700 border-gray-600 text-white text-sm">
                            <SelectValue placeholder="一般模式" />
                        </SelectTrigger>
                        <SelectContent class="bg-gray-700 border-gray-600">
                            <SelectItem
                                v-for="option in displayModeOptions"
                                :key="option.value"
                                :value="option.value"
                                class="text-white hover:bg-gray-600"
                            >
                                {{ option.label }}
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <!-- 搜尋框 -->
                <div class="flex-1 relative">
                    <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                        v-model="searchQuery"
                        placeholder="搜尋任務..."
                        class="pl-10 bg-gray-700 border-gray-600 text-white placeholder-gray-400 text-sm"
                    />
                    <button
                        v-if="searchQuery"
                        @click="searchQuery = ''"
                        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                        type="button"
                    >
                        <X class="w-4 h-4" />
                    </button>
                </div>
            </div>

            <!-- 第二行：清除過濾器按鈕 + 標籤過濾 -->
            <div class="flex items-center gap-3">
                <!-- 清除過濾器按鈕 -->
                <Button
                    @click="clearAllFilters"
                    :disabled="!hasActiveFilters"
                    variant="outline"
                    size="sm"
                    :class="[
                        'flex-shrink-0 text-xs',
                        hasActiveFilters
                            ? 'border-red-500 text-red-400 hover:bg-red-500 hover:text-white'
                            : 'border-gray-600 text-gray-500 cursor-not-allowed'
                    ]"
                    type="button"
                >
                    <Filter class="w-3 h-3 mr-1" />
                    清除
                </Button>

                <!-- 標籤過濾下拉選單 -->
                <div class="flex-1">
                    <Select @update:model-value="addTagFilter">
                        <SelectTrigger class="bg-gray-700 border-gray-600 text-white text-sm">
                            <SelectValue placeholder="選擇標籤過濾..." />
                        </SelectTrigger>
                        <SelectContent class="bg-gray-700 border-gray-600">
                            <SelectItem
                                v-for="tag in availableTags"
                                :key="tag"
                                :value="tag"
                                :disabled="selectedTags.includes(tag)"
                                class="text-white hover:bg-gray-600"
                            >
                                {{ tag }}
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <!-- 已選標籤顯示 -->
            <div
                v-if="selectedTags.length > 0"
                class="flex flex-wrap gap-2"
            >
                <Badge
                    v-for="tag in selectedTags"
                    :key="tag"
                    variant="secondary"
                    class="bg-blue-600 text-white text-xs flex items-center gap-1"
                >
                    {{ tag }}
                    <button
                        @click="removeTagFilter(tag)"
                        class="hover:bg-blue-700 rounded-full p-0.5"
                        type="button"
                    >
                        <X class="w-3 h-3" />
                    </button>
                </Badge>
            </div>

            <!-- 過濾結果統計 -->
            <div class="text-xs text-gray-400 flex items-center justify-between">
                <span>顯示 {{ filteredServices.length }} / {{ services.length }} 個任務</span>
                <span
                    v-if="hasActiveFilters"
                    class="text-blue-400"
                >
                    <Filter class="w-3 h-3 inline mr-1" />
                    已套用過濾器
                </span>
            </div>
        </div>

        <!-- 任務列表 -->
        <div class="flex-1 overflow-y-auto bg-gray-800 rounded-md">
            <div
                v-if="filteredServices.length === 0"
                class="p-4 text-center text-gray-400"
            >
                <div class="mb-2">
                    <Search class="w-8 h-8 mx-auto opacity-50" />
                </div>
                <p class="text-sm">沒有找到符合條件的任務</p>
                <button
                    v-if="hasActiveFilters"
                    @click="clearAllFilters"
                    class="text-blue-400 hover:text-blue-300 text-xs mt-2 underline"
                    type="button"
                >
                    清除所有過濾條件
                </button>
            </div>
            <SidebarItem
                v-for="(item, index) in filteredServices"
                :key="item.name"
                :TaskName="item.name"
                :showCheckbox="showCheckboxes"
                :tags="item.tags"
                :status="item.status"
                :description="item.description"
            />
        </div>
    </aside>
</template>
