/**
 * SidebarTagFilter 元件單元測試
 */

import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import SidebarTagFilter from '../SidebarTagFilter.vue'
import { useTagStore } from '@/stores/tagStore'
import { useTaskStore } from '@/stores/taskStore'
import type { Tag } from '@/schemas'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      if (key === 'components.sidebarTagFilter.selected' && params) {
        return `已選取 ${params.count} 個`
      }
      if (key === 'components.sidebarTagFilter.title') return '標籤篩選'
      return key
    },
  }),
}))

// Mock lucide-vue-next icons
vi.mock('lucide-vue-next', () => ({
  ChevronDown: { template: '<span class="chevron-down" />' },
  ChevronRight: { template: '<span class="chevron-right" />' },
}))

// Mock useHttpService (required by stores)
vi.mock('@/composables/useHttpService', () => ({
  request: vi.fn(),
}))

const sampleTags: Tag[] = [
  { id: 'tag-1', name: '動畫', color: 'blue', created_at: '2024-01-01T00:00:00Z' },
  { id: 'tag-2', name: '電影', color: 'red', created_at: '2024-01-01T00:00:00Z' },
  { id: 'tag-3', name: '音樂', color: 'green', created_at: '2024-01-01T00:00:00Z' },
]

describe('SidebarTagFilter', () => {
  let tagStore: ReturnType<typeof useTagStore>
  let taskStore: ReturnType<typeof useTaskStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    tagStore = useTagStore()
    taskStore = useTaskStore()
    vi.clearAllMocks()
  })

  const mountComponent = () => {
    return mount(SidebarTagFilter)
  }

  describe('顯示條件', () => {
    it('無 Tag 時不渲染元件', () => {
      tagStore.tags = []
      const wrapper = mountComponent()
      expect(wrapper.find('[data-testid="sidebar-tag-filter"]').exists()).toBe(false)
    })

    it('有 Tag 時渲染所有 Tag 為可點擊的標籤', () => {
      tagStore.tags = [...sampleTags]
      const wrapper = mountComponent()
      expect(wrapper.find('[data-testid="sidebar-tag-filter"]').exists()).toBe(true)
      const tagButtons = wrapper.findAll('[data-testid="filter-tag"]')
      expect(tagButtons).toHaveLength(3)
    })
  })

  describe('篩選互動', () => {
    it('點擊 Tag 應呼叫 toggleFilterTag', async () => {
      tagStore.tags = [...sampleTags]
      const wrapper = mountComponent()

      const tagButtons = wrapper.findAll('[data-testid="filter-tag"]')
      await tagButtons[0]!.trigger('click')

      expect(taskStore.selectedFilterTagIds.has('tag-1')).toBe(true)
    })

    it('已選取的 Tag 應呈現高亮樣式', () => {
      tagStore.tags = [...sampleTags]
      taskStore.toggleFilterTag('tag-1')

      const wrapper = mountComponent()
      const tagButtons = wrapper.findAll('[data-testid="filter-tag"]')
      expect(tagButtons[0]!.classes()).toContain('ring-2')
    })
  })

  describe('收合功能', () => {
    it('點擊標題應切換收合/展開狀態', async () => {
      tagStore.tags = [...sampleTags]
      const wrapper = mountComponent()

      // 預設展開，Tag 應可見
      expect(wrapper.findAll('[data-testid="filter-tag"]')).toHaveLength(3)

      // 點擊標題收合
      await wrapper.find('[data-testid="filter-header"]').trigger('click')
      expect(wrapper.findAll('[data-testid="filter-tag"]')).toHaveLength(0)

      // 再點擊展開
      await wrapper.find('[data-testid="filter-header"]').trigger('click')
      expect(wrapper.findAll('[data-testid="filter-tag"]')).toHaveLength(3)
    })

    it('收合時顯示已選取 Tag 數量', async () => {
      tagStore.tags = [...sampleTags]
      taskStore.toggleFilterTag('tag-1')
      taskStore.toggleFilterTag('tag-2')

      const wrapper = mountComponent()

      // 收合
      await wrapper.find('[data-testid="filter-header"]').trigger('click')

      expect(wrapper.text()).toContain('已選取 2 個')
    })
  })
})
