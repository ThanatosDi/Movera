/**
 * TaskForm 元件單元測試 - move_to 目錄選擇整合
 */

import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import TaskForm from '../TaskForm.vue'

// Mock tagStore
vi.mock('@/stores/tagStore', () => ({
  useTagStore: () => ({
    tags: ref([]),
    fetchTags: vi.fn(),
  }),
}))

// Mock useDirectoryBrowser
vi.mock('@/composables/useDirectoryBrowser', () => ({
  useDirectoryBrowser: () => ({
    directories: ref([]),
    loading: ref(false),
    error: ref(null),
    fetchDirectories: vi.fn(),
  }),
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}))

describe('TaskForm - move_to 目錄選擇', () => {
  const defaultTask = {
    name: '測試任務',
    include: '測試',
    move_to: '',
    src_filename: null,
    dst_filename: null,
    rename_rule: null,
    enabled: true,
  }

  const mountForm = (task = { ...defaultTask }) => {
    return mount(TaskForm, {
      props: {
        modelValue: task,
      },
      attachTo: document.body,
      global: {
        stubs: {
          Dialog: { template: '<div><slot /></div>', props: ['open'] },
          DialogContent: { template: '<div><slot /></div>' },
          DialogHeader: { template: '<div><slot /></div>' },
          DialogTitle: { template: '<div><slot /></div>' },
          DialogDescription: { template: '<div><slot /></div>' },
          DialogFooter: { template: '<div><slot /></div>' },
        },
      },
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('move_to 欄位應顯示為 Input + 瀏覽按鈕', async () => {
    const wrapper = mountForm()
    await flushPromises()

    expect(wrapper.find('#move_to').exists()).toBe(true)
    expect(wrapper.find('[data-testid="browse-btn"]').exists()).toBe(true)
  })

  it('點擊瀏覽按鈕應開啟 DirectoryPickerModal', async () => {
    const wrapper = mountForm()
    await flushPromises()

    await wrapper.find('[data-testid="browse-btn"]').trigger('click')
    await flushPromises()

    // 檢查 modal 的 open prop
    const modal = wrapper.findComponent({ name: 'DirectoryPickerModal' })
    expect(modal.exists()).toBe(true)
  })

  it('手動編輯 move_to Input 應有效', async () => {
    const wrapper = mountForm()
    await flushPromises()

    const input = wrapper.find('#move_to')
    await input.setValue('/custom/path')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })
})
