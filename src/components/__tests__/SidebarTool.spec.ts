/**
 * SidebarTool 元件單元測試 - 選擇模式批量操作列
 */

import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import SidebarTool from '../SidebarTool.vue'
import { useTaskStore } from '@/stores/taskStore'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string, params?: Record<string, unknown>) => {
      if (key === 'components.sidebarTool.selectedCount' && params) {
        return `已選擇 ${params.count} 項`
      }
      return key
    },
  }),
}))

// Mock lucide-vue-next icons
vi.mock('lucide-vue-next', () => ({
  CheckSquare: { template: '<span />' },
  Play: { template: '<span />' },
  Square: { template: '<span />' },
  StopCircle: { template: '<span />' },
  Trash2: { template: '<span />' },
}))

describe('SidebarTool - 選擇模式批量操作列', () => {
  let store: ReturnType<typeof useTaskStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTaskStore()
    // 加入假任務讓選擇模式按鈕可用
    store.tasks = [
      { id: '1', name: 'Task 1', include: 'test', move_to: '/tmp', rename_rule: null, src_filename: null, dst_filename: null, enabled: true, created_at: '' } as any,
      { id: '2', name: 'Task 2', include: 'test', move_to: '/tmp', rename_rule: null, src_filename: null, dst_filename: null, enabled: true, created_at: '' } as any,
    ]
  })

  const mountComponent = () => {
    return mount(SidebarTool, {
      global: {
        stubs: {
          Button: {
            template: '<button :disabled="$attrs.disabled" v-bind="$attrs"><slot /></button>',
            inheritAttrs: false,
          },
        },
      },
    })
  }

  describe('操作列顯示條件', () => {
    it('進入選擇模式但未選取任務時，批量操作列應顯示', () => {
      store.isSelectMode = true

      const wrapper = mountComponent()
      const actionBar = wrapper.find('[class*="bg-sidebar-accent"]')
      expect(actionBar.exists()).toBe(true)
    })

    it('進入選擇模式且未選取任務時，顯示「已選擇 0 項」', () => {
      store.isSelectMode = true

      const wrapper = mountComponent()
      expect(wrapper.text()).toContain('已選擇 0 項')
    })
  })

  describe('按鈕禁用狀態', () => {
    it('選取數為 0 時，啟用/停用/刪除按鈕應為 disabled', () => {
      store.isSelectMode = true

      const wrapper = mountComponent()
      const actionBar = wrapper.find('[class*="bg-sidebar-accent"]')
      const buttons = actionBar.findAll('button')
      // 三個操作按鈕（啟用、停用、刪除）
      const actionButtons = buttons.filter(b => !b.text().includes('已選擇'))
      expect(actionButtons.length).toBe(3)
      actionButtons.forEach(btn => {
        expect(btn.attributes('disabled')).toBeDefined()
      })
    })

    it('選取數大於 0 時，啟用/停用/刪除按鈕應為 enabled', () => {
      store.isSelectMode = true
      store.selectedTaskIds = new Set(['1'])

      const wrapper = mountComponent()
      const actionBar = wrapper.find('[class*="bg-sidebar-accent"]')
      const buttons = actionBar.findAll('button')
      const actionButtons = buttons.filter(b => !b.text().includes('已選擇'))
      expect(actionButtons.length).toBe(3)
      actionButtons.forEach(btn => {
        expect(btn.attributes('disabled')).toBeUndefined()
      })
    })
  })

  describe('批量操作按鈕呼叫 store', () => {
    it('點擊「刪除」應呼叫 taskStore.batchDelete 一次', async () => {
      store.isSelectMode = true
      store.selectedTaskIds = new Set(['1'])
      const spy = vi.spyOn(store, 'batchDelete').mockResolvedValue(undefined)

      const wrapper = mountComponent()
      const buttons = wrapper.find('[class*="bg-sidebar-accent"]').findAll('button')
      const actionButtons = buttons.filter(b => !b.text().includes('已選擇'))
      // 順序：啟用、停用、刪除
      await actionButtons[2]!.trigger('click')

      expect(spy).toHaveBeenCalledTimes(1)
    })

    it('點擊「啟用」應呼叫 taskStore.batchEnable 一次', async () => {
      store.isSelectMode = true
      store.selectedTaskIds = new Set(['1'])
      const spy = vi.spyOn(store, 'batchEnable').mockResolvedValue(undefined)

      const wrapper = mountComponent()
      const buttons = wrapper.find('[class*="bg-sidebar-accent"]').findAll('button')
      const actionButtons = buttons.filter(b => !b.text().includes('已選擇'))
      await actionButtons[0]!.trigger('click')

      expect(spy).toHaveBeenCalledTimes(1)
    })

    it('點擊「停用」應呼叫 taskStore.batchDisable 一次', async () => {
      store.isSelectMode = true
      store.selectedTaskIds = new Set(['1'])
      const spy = vi.spyOn(store, 'batchDisable').mockResolvedValue(undefined)

      const wrapper = mountComponent()
      const buttons = wrapper.find('[class*="bg-sidebar-accent"]').findAll('button')
      const actionButtons = buttons.filter(b => !b.text().includes('已選擇'))
      await actionButtons[1]!.trigger('click')

      expect(spy).toHaveBeenCalledTimes(1)
    })
  })
})
