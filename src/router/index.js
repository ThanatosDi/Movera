import { createRouter, createWebHistory } from 'vue-router'
// 懶加載組件
const Layout = () => import('@/layout/Layout.vue')
const DefaultView = () => import('@/views/DefaultView.vue')
const CreateTaskView = () => import('@/views/CreateTaskView.vue')
const TaskDetailView = () => import('@/views/TaskDetailView.vue')
// const Settings = () => import('@/views/Settings.vue')

/**
 * 路由配置
 */
const routes = [
  {
    path: '/',
    name: 'layout',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Home',
        component: DefaultView,
        meta: {
          title: '首頁',
          description: '歡迎使用 Movera 自動化檔案管理系統',
        },
      },
      {
        path: 'tasks/:taskId',
        name: 'taskDetail',
        component: TaskDetailView,
        props: true,
        meta: {
          title: '任務詳情',
          description: '查看和編輯任務詳細設定',
        },
      },
      {
        path: 'create',
        name: 'createTask',
        component: CreateTaskView,
        meta: {
          title: '建立任務',
          description: '設定自動化檔案管理任務',
        },
      },
      //   {
      //     path: 'settings',
      //     name: 'settings',
      //     component: Settings,
      //     meta: {
      //       title: '設定',
      //       description: '系統設定和偏好',
      //     },
      //   },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'notFound',
    redirect: '/',
  },
]

/**
 * 創建路由器
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

/**
 * 路由守衛
 */
router.beforeEach((to, from, next) => {
  // 設置頁面標題
  if (to.meta?.title) {
    document.title = `${to.meta.title} - Movera`
  } else {
    document.title = 'Movera'
  }

  next()
})

export default router