/**
 * 路由配置
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/index.vue'),
    meta: { title: '监控大屏' }
  },
  {
    path: '/strategy',
    name: 'Strategy',
    component: () => import('@/views/strategy/index.vue'),
    meta: { title: '策略管理' }
  },
  {
    path: '/indicator',
    name: 'Indicator',
    component: () => import('@/views/indicator/index.vue'),
    meta: { title: '指标库管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - 策略中心`
  }
  next()
})

export default router