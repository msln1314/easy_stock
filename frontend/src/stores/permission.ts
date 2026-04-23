/**
 * 权限状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserMenuResponse } from '@/types/menu'
import * as menuApi from '@/api/menu'
import { useAuthStore } from '@/stores/auth'
import { addDynamicRoutes } from '@/router'

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const menus = ref<UserMenuResponse[]>([])
  const permissions = ref<string[]>([])
  const routesLoaded = ref(false)

  // 计算属性
  const hasMenus = computed(() => menus.value.length > 0)

  // 获取用户菜单
  async function fetchUserMenus() {
    try {
      const res = await menuApi.getUserMenus()
      menus.value = res

      // 自动添加动态路由（每次都刷新）
      if (res.length > 0) {
        addDynamicRoutes(res)
        routesLoaded.value = true
      }

      return res
    } catch (e) {
      menus.value = []
      return []
    }
  }

  // 获取用户权限标识列表
  async function fetchUserPermissions() {
    // 从菜单中提取权限标识
    const perms: string[] = []
    function extractPermissions(menuList: UserMenuResponse[]) {
      for (const menu of menuList) {
        // 权限标识在菜单数据中，需要从完整菜单获取
        if (menu.children && menu.children.length > 0) {
          extractPermissions(menu.children)
        }
      }
    }
    extractPermissions(menus.value)
    permissions.value = perms
    return perms
  }

  // 检查是否有指定权限
  function hasPermission(permission: string): boolean {
    // 管理员拥有所有权限
    const authStore = useAuthStore()
    if (authStore.isAdmin) return true

    return permissions.value.includes(permission)
  }

  // 检查是否有任意一个权限
  function hasAnyPermission(permissionList: string[]): boolean {
    const authStore = useAuthStore()
    if (authStore.isAdmin) return true

    return permissionList.some(p => permissions.value.includes(p))
  }

  // 检查是否有所有权限
  function hasAllPermissions(permissionList: string[]): boolean {
    const authStore = useAuthStore()
    if (authStore.isAdmin) return true

    return permissionList.every(p => permissions.value.includes(p))
  }

  // 清空权限数据
  function clearPermission() {
    menus.value = []
    permissions.value = []
    routesLoaded.value = false
  }

  return {
    menus,
    permissions,
    routesLoaded,
    hasMenus,
    fetchUserMenus,
    fetchUserPermissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    clearPermission
  }
})