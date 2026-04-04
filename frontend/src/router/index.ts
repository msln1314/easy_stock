/**
 * 路由配置（集成通知功能）
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true }
  },
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
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/views/monitor/index.vue'),
    meta: { title: '监控股票池' }
  },
  {
    path: '/notification',
    name: 'Notification',
    component: () => import('@/views/notification/index.vue'),
    meta: { title: '通知配置' }
  },
  {
    path: '/dict',
    name: 'Dict',
    component: () => import('@/views/dict/index.vue'),
    meta: { title: '字典管理' }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/config/index.vue'),
    meta: { title: '系统配置' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/profile/index.vue'),
    meta: { title: '用户信息' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - 策略中心`
  }

  // 公开页面直接访问
  if (to.meta.public) {
    // 已登录用户访问登录页，跳转到首页
    const token = localStorage.getItem('stock_policy_token')
    if (token && to.path === '/login') {
      next('/')
      return
    }
    next()
    return
  }

  // 非公开页面需要登录
  const token = localStorage.getItem('stock_policy_token')
  if (!token) {
    next('/login')
    return
  }

  next()
})

export default router