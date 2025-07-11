import { createRouter, createWebHistory } from 'vue-router'
import CreateTask from '../components/CreateTask.vue'
import TaskDetail from '../components/TaskDetail.vue'
import Layout from '../layout/Layout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: Layout,
      children: [
        {
          path: 'services/:TaskName',
          component: TaskDetail,
          props: true
        },
        {
          path: 'create',
          component: CreateTask,
          props: true
        }
      ]
    },
  ],
})

export default router
