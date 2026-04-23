/**
 * 路由配置
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { transformMenusToRoutes } from './dynamic'
import type { UserMenuResponse } from '@/types/menu'

// 静态路由 - 登录、外部链接等公共页面
const staticRoutes: RouteRecordRaw[] = [
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
    path: '/external/:encodedUrl',
    name: 'ExternalLink',
    component: () => import('@/views/external-link/index.vue'),
    meta: { title: '外部链接' }
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
  routes: staticRoutes
})

// 动态路由是否已加载
let dynamicRoutesAdded = false

/**
 * 重置并重新添加动态路由
 */
export function refreshDynamicRoutes(menus: UserMenuResponse[]) {
  // 先重置路由
  resetRouter()

  // 再添加新的动态路由
  const dynamicRoutes = transformMenusToRoutes(menus)

  dynamicRoutes.forEach(route => {
    router.addRoute(route)
  })

  dynamicRoutesAdded = true
  console.log('[Router] 动态路由已刷新:', dynamicRoutes.length, '个')
}

/**
 * 添加动态路由（首次加载）
 */
export function addDynamicRoutes(menus: UserMenuResponse[]) {
  if (dynamicRoutesAdded) {
    // 已加载过，改用刷新方法
    refreshDynamicRoutes(menus)
    return
  }

  const dynamicRoutes = transformMenusToRoutes(menus)

  dynamicRoutes.forEach(route => {
    router.addRoute(route)
  })

  dynamicRoutesAdded = true
  console.log('[Router] 动态路由已添加:', dynamicRoutes.length, '个')
}

/**
 * 重置路由（用于退出登录）
 */
export function resetRouter() {
  // 移除所有动态添加的路由
  const newRouter = createRouter({
    history: createWebHistory(),
    routes: staticRoutes
  })
  ;(router as any).matcher = (newRouter as any).matcher
  dynamicRoutesAdded = false
}

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