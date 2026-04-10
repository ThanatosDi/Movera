/**
 * DirectoryPickerModal 元件單元測試
 */

import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import DirectoryPickerModal from '../DirectoryPickerModal.vue'
import type { DirectoryItem } from '@/schemas'

// Mock useDirectoryBrowser with real Vue refs
const mockFetchDirectories = vi.fn()
const mockDirectories = ref<DirectoryItem[]>([])
const mockLoading = ref(false)
const mockError = ref<string | null>(null)

vi.mock('@/composables/useDirectoryBrowser', () => ({
  useDirectoryBrowser: () => ({
    directories: mockDirectories,
    loading: mockLoading,
    error: mockError,
    fetchDirectories: mockFetchDirectories,
  }),
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}))

describe('DirectoryPickerModal', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockDirectories.value = []
    mockLoading.value = false
    mockError.value = null
  })

  const mountModal = (props = {}) => {
    return mount(DirectoryPickerModal, {
      props: {
        open: true,
        ...props,
      },
      attachTo: document.body,
      global: {
        stubs: {
          Dialog: {
            template: '<div><slot /></div>',
            props: ['open'],
          },
          DialogContent: { template: '<div><slot /></div>' },
          DialogHeader: { template: '<div><slot /></div>' },
          DialogTitle: { template: '<div><slot /></div>' },
          DialogDescription: { template: '<div><slot /></div>' },
          DialogFooter: { template: '<div><slot /></div>' },
        },
      },
    })
  }

  describe('開啟時行為', () => {
    it('開啟時應載入根目錄列表', async () => {
      mountModal({ open: true })
      await flushPromises()

      expect(mockFetchDirectories).toHaveBeenCalledWith(undefined)
    })

    it('應顯示目錄列表', async () => {
      mockDirectories.value = [
        { name: 'downloads', path: '/downloads', has_children: true },
        { name: 'media', path: '/media', has_children: false },
      ]

      const wrapper = mountModal()
      await flushPromises()

      const items = wrapper.findAll('[data-testid="directory-item"]')
      expect(items.length).toBe(2)
      expect(items[0]!.text()).toContain('downloads')
      expect(items[1]!.text()).toContain('media')
    })
  })

  describe('目錄導航', () => {
    it('點擊目錄後應進入子目錄', async () => {
      mockDirectories.value = [
        { name: 'downloads', path: '/downloads', has_children: true },
      ]

      const wrapper = mountModal()
      await flushPromises()

      await wrapper.find('[data-testid="directory-item"]').trigger('click')
      await flushPromises()

      expect(mockFetchDirectories).toHaveBeenCalledWith('/downloads')
    })

    it('應顯示麵包屑導航', async () => {
      mockDirectories.value = [
        { name: 'downloads', path: '/downloads', has_children: true },
      ]

      const wrapper = mountModal()
      await flushPromises()

      // 進入 downloads
      await wrapper.find('[data-testid="directory-item"]').trigger('click')
      await flushPromises()

      const breadcrumbs = wrapper.findAll('[data-testid="breadcrumb-item"]')
      // root + downloads = 2
      expect(breadcrumbs.length).toBe(2)
    })
  })

  describe('選擇與取消', () => {
    it('點擊確認應 emit select 事件', async () => {
      mockDirectories.value = [
        { name: 'downloads', path: '/downloads', has_children: true },
      ]

      const wrapper = mountModal()
      await flushPromises()

      // 進入 downloads (sets currentPath)
      await wrapper.find('[data-testid="directory-item"]').trigger('click')
      await flushPromises()

      // 點確認
      await wrapper.find('[data-testid="confirm-btn"]').trigger('click')

      expect(wrapper.emitted('select')).toBeTruthy()
      expect(wrapper.emitted('select')![0]).toEqual(['/downloads'])
    })

    it('點擊取消應 emit update:open 事件', async () => {
      const wrapper = mountModal()
      await flushPromises()

      await wrapper.find('[data-testid="cancel-btn"]').trigger('click')

      expect(wrapper.emitted('update:open')).toBeTruthy()
      expect(wrapper.emitted('update:open')![0]).toEqual([false])
    })
  })

  describe('狀態顯示', () => {
    it('載入中時應顯示載入指示器', async () => {
      mockLoading.value = true

      const wrapper = mountModal()
      await flushPromises()

      expect(wrapper.find('[data-testid="loading-indicator"]').exists()).toBe(true)
    })

    it('空目錄且非載入中時應顯示提示訊息', async () => {
      mockDirectories.value = []
      mockLoading.value = false

      const wrapper = mountModal()
      await flushPromises()

      expect(wrapper.find('[data-testid="empty-message"]').exists()).toBe(true)
    })
  })
})
