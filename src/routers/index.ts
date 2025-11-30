import { createRouter, createWebHistory } from 'vue-router'
// 懶加載組件
const Layout = () => import('@/layouts/Layout.vue')
const HomeView = () => import('@/views/HomeView.vue')
const SettingView = () => import('@/views/SettingView.vue')
const TaskDetailView = () => import('@/views/TaskDetailView.vue')
const CreateTaskView = () => import('@/views/CreateTaskView.vue')
const TasksListView = () => import('@/views/TasksListView.vue')


/**
 * 路由配置
 */
const routes = [
  {
    path: '/',
    name: 'layout',
    component: Layout,
    children: [
      // 首頁
      {
        path: '',
        name: 'Home',
        component: HomeView,
        meta: {
          title: '首頁',
          description: '歡迎使用 Movera 自動化檔案管理系統',
        },
        // beforeEnter: async (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
        //   const taskStore = useTaskStore()
        //   try {
        //     await taskStore.fetchTasks()

        //   } catch (error) {
        //     console.error("Failed to fetch tasks before entering route:", error)
        //     // 你可以在這裡處理錯誤，例如導向到一個錯誤頁面
        //   }
        //   next()
        // }
      },
      // 設定頁面
      {
        path: 'setting',
        name: 'setting',
        component: SettingView,
        meta: {
          title: '設定',
          description: '管理應用程式的全域設定',
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
        // beforeEnter: async (_to: RouteLocationNormalized, _from: RouteLocationNormalized, next: NavigationGuardNext) => {
        //   const taskStore = useTaskStore()
        //   try {
        //     await taskStore.fetchTasks()

        //   } catch (error) {
        //     console.error("Failed to fetch tasks before entering route:", error)
        //     // 你可以在這裡處理錯誤，例如導向到一個錯誤頁面
        //   }
        //   next()
        // }
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
      {
        path: 'tasks',
        name: 'tasksList',
        component: TasksListView,
        meta: {
          title: '任務清單',
          description: '管理所有已建立的任務',
        },
      }
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
  scrollBehavior(_to, _from, savedPosition) {
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
router.beforeEach((to, _from, next) => {
  // 設置頁面標題
  if (to.meta?.title) {
    document.title = `${to.meta.title} - Movera`
  } else {
    document.title = 'Movera'
  }

  next()
})

export default router