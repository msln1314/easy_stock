/**
 * 动态路由配置
 */
import { RouteRecordRaw } from 'vue-router'
import type { UserMenuResponse } from '@/types/menu'

// 组件映射表 - 将后端组件路径映射到实际组件
const componentModules = import.meta.glob('@/views/**/*.vue')

/**
 * 根据组件路径获取组件
 */
function getComponent(componentPath?: string) {
  if (!componentPath) return null

  // 尝试多种路径格式
  const paths = [
    `/src/views/${componentPath}.vue`,
    `/src/views/${componentPath}/index.vue`,
    `${componentPath}`,
  ]

  for (const path of paths) {
    if (componentModules[path]) {
      return componentModules[path]
    }
  }

  // 尝试直接匹配
  const directPath = Object.keys(componentModules).find(p =>
    p.includes(componentPath) || p.endsWith(`${componentPath}.vue`)
  )

  if (directPath) {
    return componentModules[directPath]
  }

  return null
}

/**
 * 将菜单转换为路由
 */
export function transformMenusToRoutes(menus: UserMenuResponse[]): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []

  function processMenu(menu: UserMenuResponse, parentPath?: string): RouteRecordRaw | null {
    // 目录类型不需要组件
    if (menu.menu_type === 'directory') {
      const route: RouteRecordRaw = {
        path: menu.path,
        name: `dir_${menu.id}`,
        meta: {
          title: menu.name,
          icon: menu.icon,
        },
        children: []
      }

      if (menu.children && menu.children.length > 0) {
        route.children = menu.children
          .map(child => processMenu(child, menu.path))
          .filter((r): r is RouteRecordRaw => r !== null)
      }

      return route
    }

    // 外部链接不生成路由
    if (menu.menu_type === 'link' && menu.is_external) {
      return null
    }

    // 按钮类型不生成路由
    if (menu.menu_type === 'button') {
      return null
    }

    // 菜单类型
    const component = getComponent(menu.component)

    const route: RouteRecordRaw = {
      path: menu.path,
      name: `menu_${menu.id}`,
      component: component || undefined,
      meta: {
        title: menu.name,
        icon: menu.icon,
      },
      children: []
    }

    if (menu.children && menu.children.length > 0) {
      route.children = menu.children
        .map(child => processMenu(child, menu.path))
        .filter((r): r is RouteRecordRaw => r !== null)
    }

    return route
  }

  for (const menu of menus) {
    const route = processMenu(menu)
    if (route) {
      routes.push(route)
    }
  }

  return routes
}

export { componentModules }