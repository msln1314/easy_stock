/**
 * 权限指令
 * 用于按钮级别的权限控制
 *
 * 使用方式:
 * <button v-permission="'user:create'">创建用户</button>
 * <button v-permission="['user:create', 'user:edit']">创建或编辑用户</button>
 */
import type { Directive, DirectiveBinding } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * 权限检查指令
 */
export const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const authStore = useAuthStore()

    // 管理员拥有所有权限
    if (authStore.isAdmin) return

    // 获取需要检查的权限列表
    const requiredPermissions = Array.isArray(binding.value)
      ? binding.value
      : [binding.value]

    // TODO: 这里需要从后端获取用户权限列表进行比对
    // 目前暂时只对管理员放行，非管理员隐藏按钮
    // 完整实现需要在permissionStore中维护用户权限列表

    // 暂时隐藏按钮（等permissionStore完善后再实现完整检查）
    el.style.display = 'none'
  }
}

/**
 * 权限角色检查指令
 * 根据用户角色控制显示
 *
 * 使用方式:
 * <button v-role="'admin'">仅管理员可见</button>
 * <button v-role="['admin', 'manager']">管理员或经理可见</button>
 */
export const role: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const authStore = useAuthStore()

    // 获取需要的角色列表
    const requiredRoles = Array.isArray(binding.value)
      ? binding.value
      : [binding.value]

    // 检查用户角色
    if (!requiredRoles.includes(authStore.user?.role || '')) {
      el.style.display = 'none'
    }
  }
}

/**
 * 注册权限指令
 */
export function setupPermissionDirectives(app: any) {
  app.directive('permission', permission)
  app.directive('role', role)
}