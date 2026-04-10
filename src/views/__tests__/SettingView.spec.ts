/**
 * SettingView - allowed_directories 管理 UI 測試
 */

import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'
import SettingView from '../SettingView.vue'

// Mock settingStore
const mockSettings = ref({
  timezone: 'Asia/Taipei',
  locale: 'zh-TW',
  allowed_directories: [] as string[],
})
const mockIsSaving = ref(false)
const mockFetchSettings = vi.fn()
const mockUpdateSettings = vi.fn()

vi.mock('@/stores/settingStore', () => ({
  useSettingStore: () => ({
    settings: mockSettings,
    isSaving: mockIsSaving,
    error: ref(null),
    fetchSettings: mockFetchSettings,
    updateSettings: mockUpdateSettings,
  }),
}))

// Mock tagStore
vi.mock('@/stores/tagStore', () => ({
  useTagStore: () => ({
    tags: ref([]),
    fetchTags: vi.fn(),
    createTag: vi.fn(),
    updateTag: vi.fn(),
    deleteTag: vi.fn(),
  }),
}))

// Mock pinia
vi.mock('pinia', () => ({
  storeToRefs: (store: any) => {
    const refs: Record<string, any> = {}
    for (const key of Object.keys(store)) {
      if (typeof store[key] !== 'function') {
        refs[key] = store[key]
      }
    }
    return refs
  },
  defineStore: vi.fn(),
}))

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
    locale: ref('zh-TW'),
  }),
}))

// Mock useNotification
vi.mock('@/composables/useNotification', () => ({
  useNotification: {
    showSuccess: vi.fn(),
    showError: vi.fn(),
  },
}))

describe('SettingView - allowed_directories', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockSettings.value = {
      timezone: 'Asia/Taipei',
      locale: 'zh-TW',
      allowed_directories: [],
    }
  })

  const mountView = () => {
    return mount(SettingView, {
      attachTo: document.body,
      global: {
        stubs: {
          Card: { template: '<div><slot /></div>' },
          CardHeader: { template: '<div><slot /></div>' },
          CardTitle: { template: '<div><slot /></div>' },
          CardDescription: { template: '<div><slot /></div>' },
          CardContent: { template: '<div><slot /></div>' },
          Combobox: { template: '<div><slot /></div>', props: ['modelValue'] },
          ComboboxAnchor: { template: '<div><slot /></div>' },
          ComboboxTrigger: { template: '<div><slot /></div>' },
          ComboboxList: { template: '<div><slot /></div>' },
          ComboboxInput: { template: '<div />' },
          ComboboxEmpty: { template: '<div><slot /></div>' },
          ComboboxGroup: { template: '<div><slot /></div>' },
          ComboboxItem: { template: '<div><slot /></div>' },
          ComboboxItemIndicator: { template: '<div><slot /></div>' },
          LocaleSelect: { template: '<div />', props: ['locale'] },
        },
      },
    })
  }

  it('應顯示允許目錄管理區塊', async () => {
    const wrapper = mountView()
    await flushPromises()

    expect(wrapper.find('[data-testid="allowed-directories-section"]').exists()).toBe(true)
  })

  it('應能新增允許目錄路徑', async () => {
    const wrapper = mountView()
    await flushPromises()

    const input = wrapper.find('[data-testid="add-directory-input"]')
    await input.setValue('/downloads')

    await wrapper.find('[data-testid="add-directory-btn"]').trigger('click')
    await flushPromises()

    expect(mockSettings.value.allowed_directories).toContain('/downloads')
  })

  it('應能刪除允許目錄路徑', async () => {
    mockSettings.value.allowed_directories = ['/downloads', '/media']

    const wrapper = mountView()
    await flushPromises()

    const removeButtons = wrapper.findAll('[data-testid="remove-directory-btn"]')
    expect(removeButtons.length).toBe(2)

    await removeButtons[0]!.trigger('click')
    await flushPromises()

    expect(mockSettings.value.allowed_directories).not.toContain('/downloads')
    expect(mockSettings.value.allowed_directories).toContain('/media')
  })
})
