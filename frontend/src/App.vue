<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <!-- 无侧边栏模式：登录页、大屏 -->
          <template v-if="isNoSiderMode">
            <n-layout>
              <n-layout-content>
                <router-view />
              </n-layout-content>
            </n-layout>
          </template>

          <!-- 管理模式：有侧边栏 -->
          <template v-else>
            <n-layout has-sider>
              <!-- 侧边栏导航 -->
              <n-layout-sider
                bordered
                collapse-mode="width"
                :collapsed-width="64"
                :width="200"
                :collapsed="collapsed"
                show-trigger
                @collapse="collapsed = true"
                @expand="collapsed = false"
              >
                <div class="logo p-4 text-center">
                  <h1 v-if="!collapsed" class="text-lg font-bold text-primary">策略中心</h1>
                  <span v-else class="text-xl">📊</span>
                </div>
                <n-menu
                  :collapsed="collapsed"
                  :collapsed-width="64"
                  :collapsed-icon-size="22"
                  :options="menuOptions"
                  :value="activeKey"
                  @update:value="handleMenuClick"
                />
              </n-layout-sider>

              <!-- 主内容区 -->
              <n-layout>
                <n-layout-header bordered class="px-4 py-3 flex-between">
                  <span class="text-gray-500">{{ currentRouteTitle }}</span>
                  <div class="flex items-center gap-4">
                    <n-button text @click="collapsed = !collapsed">
                      <template #icon>
                        <n-icon><MenuOutline /></n-icon>
                      </template>
                    </n-button>
                    <!-- 头像下拉 -->
                    <n-dropdown :options="userDropdownOptions" @select="handleUserDropdown">
                      <n-avatar round size="small" style="cursor: pointer">
                        <n-icon><PersonOutline /></n-icon>
                      </n-avatar>
                    </n-dropdown>
                  </div>
                </n-layout-header>
                <n-layout-content class="p-4">
                  <router-view />
                </n-layout-content>
              </n-layout>
            </n-layout>
          </template>
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NConfigProvider, NLayout, NLayoutSider, NLayoutHeader, NLayoutContent,
  NMenu, NButton, NIcon, NMessageProvider, NDialogProvider, NNotificationProvider,
  NAvatar, NDropdown
} from 'naive-ui'
import { zhCN, dateZhCN } from 'naive-ui'
import { MenuOutline, GridOutline, TrendingUpOutline, PersonOutline, TvOutline, AnalyticsOutline, BookOutline, CogOutline, FilterOutline, ListOutline, ShieldOutline, LogOutOutline, FolderOutline, LibraryOutline, EyeOutline, TimeOutline, SettingsOutline, PeopleOutline, SwapHorizontalOutline, ChatbubbleOutline, AlertOutline, WarningOutline, FlashOutline, SparklesOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import type { UserMenuResponse } from '@/types/menu'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

const collapsed = ref(false)

const activeKey = computed(() => route.name as string)

const currentRouteTitle = computed(() => {
  return route.meta.title as string || '首页'
})

// 是否为无侧边栏模式（登录页、大屏模式）
const isNoSiderMode = computed(() => route.name === 'Dashboard' || route.name === 'Login')

// 图标映射
const iconMap: Record<string, any> = {
  'GridOutline': GridOutline,
  'TrendingUpOutline': TrendingUpOutline,
  'AnalyticsOutline': AnalyticsOutline,
  'FilterOutline': FilterOutline,
  'LibraryOutline': LibraryOutline,
  'EyeOutline': EyeOutline,
  'TimeOutline': TimeOutline,
  'SwapHorizontalOutline': SwapHorizontalOutline,
  'BookOutline': BookOutline,
  'CogOutline': CogOutline,
  'ListOutline': ListOutline,
  'ShieldOutline': ShieldOutline,
  'SettingsOutline': SettingsOutline,
  'PeopleOutline': PeopleOutline,
  'FolderOutline': FolderOutline,
  'ChatbubbleOutline': ChatbubbleOutline,
  'AlertOutline': AlertOutline,
  'WarningOutline': WarningOutline,
  'FlashOutline': FlashOutline,
  'SparklesOutline': SparklesOutline,
}

// 路由名称映射（根据path映射到路由name）
const routeNameMap: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/strategy': 'Strategy',
  '/indicator': 'Indicator',
  '/factor-screen': 'FactorScreen',
  '/factor-library': 'FactorLibrary',
  '/monitor': 'Monitor',
  '/scheduler': 'Scheduler',
  '/warning': 'Warning',
  '/strategy-config': 'StrategyConfig',
  '/signal': 'Signal',
  '/trade': 'Trade',
  '/dict': 'Dict',
  '/config': 'Config',
  '/system/menu': 'SystemMenu',
  '/system/role': 'SystemRole',
  '/system/user': 'SystemUser',
  '/notification': 'Notification',
  '/profile': 'Profile',
  '/stock-analysis': 'StockAnalysis',
}

// 动态菜单选项
const menuOptions = computed(() => {
  function buildMenuOptions(menus: UserMenuResponse[]): any[] {
    return menus
      .filter(m => m.menu_type !== 'button') // 过滤掉按钮类型
      .map(m => {
        const iconName = m.icon || 'FolderOutline'
        const IconComponent = iconMap[iconName] || FolderOutline

        // 外部链接菜单
        if (m.is_external && m.external_url) {
          return {
            label: m.name,
            key: `external:${m.id}`,
            icon: () => h(NIcon, null, { default: () => h(IconComponent) }),
            children: m.children && m.children.length > 0 ? buildMenuOptions(m.children) : undefined,
            is_external: true,
            external_url: m.external_url,
            link_target: m.link_target,
            path: m.path
          }
        }

        // 内部菜单
        const routeName = routeNameMap[m.path] || m.path
        return {
          label: m.name,
          key: routeName,
          icon: () => h(NIcon, null, { default: () => h(IconComponent) }),
          children: m.children && m.children.length > 0 ? buildMenuOptions(m.children) : undefined
        }
      })
  }

  if (permissionStore.menus.length > 0) {
    return buildMenuOptions(permissionStore.menus)
  }

  // 如果还没有加载菜单，返回空数组或默认菜单
  return []
})

// 用户下拉菜单
const userDropdownOptions = [
  {
    label: '用户信息',
    key: 'profile',
    icon: () => h(NIcon, null, { default: () => h(PersonOutline) })
  },
  {
    label: '大屏展示',
    key: 'dashboard',
    icon: () => h(NIcon, null, { default: () => h(TvOutline) })
  },
  {
    type: 'divider',
    key: 'd1'
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(NIcon, null, { default: () => h(LogOutOutline) })
  }
]

function handleMenuClick(key: string, item?: any) {
  // 检查是否为外部链接
  if (item?.is_external && item?.external_url) {
    if (item.link_target === '_iframe') {
      // iframe嵌入模式
      const encodedUrl = encodeURIComponent(item.external_url)
      router.push(`/external/${encodedUrl}?title=${encodeURIComponent(item.label)}`)
    } else if (item.link_target === '_self') {
      // 当前窗口打开
      window.location.href = item.external_url
    } else {
      // 默认新窗口打开
      window.open(item.external_url, '_blank')
    }
    return
  }
  // 内部路由跳转
  router.push({ name: key })
}

function handleUserDropdown(key: string) {
  if (key === 'dashboard') {
    router.push({ name: 'Dashboard' })
  } else if (key === 'profile') {
    router.push({ name: 'Profile' })
  } else if (key === 'logout') {
    authStore.logout()
  }
}

// 加载用户菜单
async function loadUserMenus() {
  if (authStore.isLoggedIn && permissionStore.menus.length === 0) {
    await permissionStore.fetchUserMenus()
  }
}

// 监听登录状态变化
watch(() => authStore.isLoggedIn, (isLoggedIn) => {
  if (isLoggedIn) {
    loadUserMenus()
  } else {
    permissionStore.clearPermission()
  }
}, { immediate: true })

onMounted(() => {
  if (authStore.isLoggedIn) {
    loadUserMenus()
  }
})
</script>

<style lang="scss">
.logo {
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f4ff 100%);
}

.n-layout-header {
  height: 50px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>