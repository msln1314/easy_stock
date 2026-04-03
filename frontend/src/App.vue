<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <!-- 大屏模式：无侧边栏 -->
          <template v-if="isDashboardMode">
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
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NConfigProvider, NLayout, NLayoutSider, NLayoutHeader, NLayoutContent,
  NMenu, NButton, NIcon, NMessageProvider, NDialogProvider, NNotificationProvider,
  NAvatar, NDropdown
} from 'naive-ui'
import { zhCN, dateZhCN } from 'naive-ui'
import { MenuOutline, GridOutline, TrendingUpOutline, PersonOutline, TvOutline, SettingsOutline, AnalyticsOutline, BookOutline, CogOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)

const activeKey = computed(() => route.name as string)

const currentRouteTitle = computed(() => {
  return route.meta.title as string || '首页'
})

// 是否为大屏模式（无侧边栏）
const isDashboardMode = computed(() => route.name === 'Dashboard')

const menuOptions = [
  {
    label: '监控大屏',
    key: 'Dashboard',
    icon: () => h(NIcon, null, { default: () => h(GridOutline) })
  },
  {
    label: '策略管理',
    key: 'Strategy',
    icon: () => h(NIcon, null, { default: () => h(TrendingUpOutline) })
  },
  {
    label: '指标库管理',
    key: 'Indicator',
    icon: () => h(NIcon, null, { default: () => h(AnalyticsOutline) })
  },
  {
    label: '字典管理',
    key: 'Dict',
    icon: () => h(NIcon, null, { default: () => h(BookOutline) })
  },
  {
    label: '系统配置',
    key: 'Config',
    icon: () => h(NIcon, null, { default: () => h(CogOutline) })
  }
]

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
    icon: () => h(NIcon, null, { default: () => h(SettingsOutline) })
  }
]

function handleMenuClick(key: string) {
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