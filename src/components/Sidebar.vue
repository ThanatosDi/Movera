<script setup>
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Filter, Plus, Search, Trash2, X } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import SidebarItem from './SidebarItem.vue'

const selected = ref(null)

// 工具欄狀態
const showCheckboxes = ref(false)
const searchQuery = ref('')
const selectedTags = ref([])

// 選擇模式相關狀態
const selectedItems = ref(new Set())
const isSelectAllChecked = ref(false)

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

// 切換顯示模式
const toggleDisplayMode = () => {
    showCheckboxes.value = !showCheckboxes.value
    if (!showCheckboxes.value) {
        // 退出選擇模式時清除所有選擇
        selectedItems.value.clear()
        isSelectAllChecked.value = false
    }
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

// 選擇模式相關功能
const handleItemSelection = (itemName, isSelected) => {
    if (isSelected) {
        selectedItems.value.add(itemName)
    } else {
        selectedItems.value.delete(itemName)
    }

    // 更新全選狀態
    updateSelectAllState()
}

const updateSelectAllState = () => {
    const totalItems = filteredServices.value.length
    const selectedCount = Array.from(selectedItems.value).filter(itemName => 
        filteredServices.value.some(service => service.name === itemName)
    ).length
    isSelectAllChecked.value = totalItems > 0 && selectedCount === totalItems
}

const handleSelectAll = () => {
    if (isSelectAllChecked.value) {
        // 取消全選 - 只取消當前過濾結果中的項目
        filteredServices.value.forEach(service => {
            selectedItems.value.delete(service.name)
        })
        isSelectAllChecked.value = false
    } else {
        // 全選 - 選中當前過濾結果中的所有項目
        filteredServices.value.forEach(service => {
            selectedItems.value.add(service.name)
        })
        isSelectAllChecked.value = true
    }
}

const deleteSelectedItems = () => {
    if (selectedItems.value.size === 0) return

    // 這裡可以添加確認對話框
    if (confirm(`確定要刪除 ${selectedItems.value.size} 個選中的項目嗎？`)) {
        // 實際刪除邏輯，這裡只是模擬
        console.log('刪除項目:', Array.from(selectedItems.value))
        selectedItems.value.clear()
        isSelectAllChecked.value = false

        // 實際應用中，這裡應該調用 API 刪除項目
        // 然後更新 services 數據
    }
}

// 計算選中項目數量
const selectedCount = computed(() => {
    return Array.from(selectedItems.value).filter(itemName => 
        filteredServices.value.some(service => service.name === itemName)
    ).length
})

// 監聽過濾條件變化，更新全選狀態
watch(filteredServices, () => {
    updateSelectAllState()
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
                    <Button
                        @click="toggleDisplayMode"
                        :variant="showCheckboxes ? 'default' : 'outline'"
                        size="sm"
                        class="text-sm"
                        :class="showCheckboxes ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-gray-600 border-gray-600 text-gray-300 hover:bg-gray-500'"
                    >
                        {{ showCheckboxes ? '選擇模式' : '一般模式' }}
                    </Button>
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

            <!-- 選擇模式控制行 -->
            <div
                v-if="showCheckboxes"
                class="flex items-center gap-3 pt-2 border-t border-gray-700"
            >
                <!-- 全選 checkbox -->
                <div class="flex items-center gap-2">
                    <input
                        type="checkbox"
                        v-model="isSelectAllChecked"
                        @change="handleSelectAll"
                        class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
                    />
                    <span class="text-sm text-gray-300">
                        全選 ({{ selectedCount }}/{{ filteredServices.length }})
                    </span>
                </div>

                <!-- 刪除按鈕 -->
                <Button
                    @click="deleteSelectedItems"
                    :disabled="selectedCount === 0"
                    variant="destructive"
                    size="sm"
                    class="ml-auto text-sm"
                    :class="selectedCount === 0 ? 'opacity-50 cursor-not-allowed' : ''"
                >
                    <Trash2 class="w-4 h-4 mr-1" />
                    刪除選中項目 ({{ selectedCount }})
                </Button>
            </div>
        </div>

        <!-- 任務列表 -->
        <div class="flex-1 overflow-y-auto bg-gray-800 rounded-md custom-scrollbar">
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
                :isSelected="selectedItems.has(item.name)"
                @update:selected="handleItemSelection"
            />
        </div>
    </aside>
</template>
