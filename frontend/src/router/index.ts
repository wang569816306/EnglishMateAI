import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/pages/Chat.vue')
  },
  {
    path: '/chat/:id',
    name: 'ChatDetail',
    component: () => import('@/pages/Chat.vue')
  },
  {
    path: '/ai-create',
    name: 'AICreate',
    component: () => import('@/pages/AICreate.vue')
  },
  {
    path: '/ai-create/:id',
    name: 'AICreateDetail',
    component: () => import('@/pages/AICreate.vue')
  },
  {
    path: '/cloud',
    name: 'Cloud',
    component: () => import('@/pages/Cloud.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
