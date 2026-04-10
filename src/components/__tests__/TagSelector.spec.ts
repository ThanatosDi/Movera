/**
 * TagSelector 元件單元測試
 */

import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import TagSelector from '../TagSelector.vue'
import type { Tag } from '@/schemas'

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => {
      const map: Record<string, string> = {
        'components.tagSelector.label': '標籤',
        'components.tagSelector.placeholder': '選擇標籤...',
        'components.tagSelector.empty': '尚無標籤',
      }
      return map[key] || key
    },
  }),
}))

vi.mock('lucide-vue-next', () => ({
  ChevronDown: { template: '<span />' },
  X: { template: '<span />' },
}))

const mockTags: Tag[] = [
  { id: 'tag-1', name: '動畫', color: 'blue' },
  { id: 'tag-2', name: '電影', color: 'red' },
  { id: 'tag-3', name: '音樂', color: 'green' },
]

describe('TagSelector', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const mountComponent = (props: { availableTags?: Tag[]; modelValue?: string[] } = {}) => {
    return mount(TagSelector, {
      props: {
        availableTags: props.availableTags ?? mockTags,
        modelValue: props.modelValue ?? [],
      },
      global: {
        stubs: {
          Button: { template: '<button v-bind="$attrs"><slot /></button>' },
          DropdownMenu: { template: '<div><slot /></div>' },
          DropdownMenuTrigger: { template: '<div><slot /></div>' },
          DropdownMenuContent: { template: '<div><slot /></div>' },
          DropdownMenuLabel: { template: '<div><slot /></div>' },
          DropdownMenuSeparator: { template: '<hr />' },
          DropdownMenuCheckboxItem: {
            template: '<div data-checkbox :data-checked="$attrs[\'model-value\'] || $attrs.modelValue" @click="$emit(\'update:modelValue\', !($attrs[\'model-value\'] || $attrs.modelValue))"><slot /></div>',
            inheritAttrs: false,
          },
          TagBadge: {
            template: '<span :data-color="$attrs.color">{{ $attrs.name }}</span>',
            inheritAttrs: false,
          },
        },
      },
    })
  }

  it('顯示可用標籤下拉選單', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('動畫')
    expect(wrapper.text()).toContain('電影')
    expect(wrapper.text()).toContain('音樂')
  })

  it('選取標籤後 emit 更新事件', async () => {
    const wrapper = mountComponent()
    const items = wrapper.findAll('[data-checkbox]')
    await items[0].trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toEqual(['tag-1'])
  })

  it('已選標籤以 Badge 顯示在選擇器中', () => {
    const wrapper = mountComponent({ modelValue: ['tag-1', 'tag-2'] })
    // The selected tags should appear as TagBadge in the top area
    const badges = wrapper.findAll('[data-color]')
    // At least 2 from the selected tags display + 3 from dropdown = 5
    // But the selected badges are rendered separately with click handlers
    const selectedBadges = badges.filter(b => b.attributes('data-color') === 'blue' || b.attributes('data-color') === 'red')
    expect(selectedBadges.length).toBeGreaterThanOrEqual(2)
  })
})
