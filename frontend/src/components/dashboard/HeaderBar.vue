<template>
  <header class="dashboard-header">
    <!-- 指数信息 -->
    <div class="index-section">
      <div class="index-item" v-for="idx in indexData" :key="idx.code">
        <span class="index-name">{{ idx.name }}</span>
        <span class="index-price" :class="idx.change >= 0 ? 'rise' : 'fall'">{{ idx.price.toFixed(2) }}</span>
        <span class="index-change" :class="idx.change >= 0 ? 'rise' : 'fall'">
          {{ idx.change >= 0 ? '+' : '' }}{{ idx.change.toFixed(2) }}%
        </span>
      </div>
    </div>

    <!-- 时间显示 -->
    <div class="time-section">
      <span class="current-time">{{ currentTime }}</span>
    </div>

    <!-- 接口状态 -->
    <div class="status-section">
      <div class="status-item">
        <span class="status-dot" :class="dataApiStatus"></span>
        <span class="status-text" :class="dataApiStatus">{{ dataApiStatusText }}</span>
      </div>
      <div class="status-item">
        <span class="status-dot" :class="qmtApiStatus"></span>
        <span class="status-text" :class="qmtApiStatus">{{ qmtApiStatusText }}</span>
      </div>
    </div>

    <!-- 布局控制 -->
    <div class="layout-controls">
      <n-button
        :type="editMode ? 'warning' : 'default'"
        size="tiny"
        @click="$emit('toggle-edit')"
      >
        <template #icon><n-icon size="14"><CreateOutline /></n-icon></template>
        {{ editMode ? '完成' : '编辑' }}
      </n-button>
      <n-select
        :value="currentLayoutId"
        :options="layoutOptions"
        placeholder="布局"
        style="width: 100px"
        size="tiny"
        @update:value="handleLayoutChange"
      />
      <template v-if="editMode">
        <n-popover trigger="click" placement="bottom">
          <template #trigger>
            <n-button type="success" size="tiny">
              <template #icon><n-icon size="14"><AddOutline /></n-icon></template>
              添加
            </n-button>
          </template>
          <div class="add-module-list">
            <div v-if="unusedModules.length === 0" class="empty-tip">所有模块已添加</div>
            <div
              v-for="module in unusedModules"
              :key="module.id"
              class="module-item"
              @click="$emit('add-module', module.id)"
            >
              <span class="module-name">{{ module.name }}</span>
            </div>
          </div>
        </n-popover>
        <n-button type="primary" size="tiny" @click="$emit('save')">
          <template #icon><n-icon size="14"><SaveOutline /></n-icon></template>
          保存
        </n-button>
        <n-button size="tiny" @click="$emit('reset')">
          <template #icon><n-icon size="14"><RefreshOutline /></n-icon></template>
          重置
        </n-button>
      </template>
    </div>

    <!-- 用户下拉 -->
    <div class="user-section">
      <!-- 通知铃铛 -->
      <n-popover trigger="click" placement="bottom-end" :show-arrow="false">
        <template #trigger>
          <div class="notification-bell" :class="{ 'has-unread': unreadCount > 0 }">
            <n-icon size="18"><NotificationsOutline /></n-icon>
            <span class="unread-badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
          </div>
        </template>
        <div class="notification-popup">
          <div class="popup-header">
            <span class="popup-title">通知</span>
            <n-button quaternary size="tiny" v-if="unreadCount > 0" @click="markAllRead">
              全部已读
            </n-button>
          </div>
          <div class="popup-content">
            <div v-if="recentNotifications.length === 0" class="empty-tip">暂无通知</div>
            <div v-else class="notification-list">
              <div
                v-for="notify in recentNotifications"
                :key="notify.id"
                class="notify-item"
                :class="{ unread: !notify.is_read }"
                @click="handleNotifyClick(notify)"
              >
                <div class="notify-icon" :class="notify.type">
                  <n-icon size="14">
                    <SettingsOutline v-if="notify.type === 'system'" />
                    <SwapHorizontalOutline v-else-if="notify.type === 'trade'" />
                    <TrendingUpOutline v-else-if="notify.type === 'market'" />
                    <FlashOutline v-else />
                  </n-icon>
                </div>
                <div class="notify-content">
                  <div class="notify-title">{{ notify.title }}</div>
                  <div class="notify-time">{{ formatNotifyTime(notify.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="popup-footer">
            <n-button quaternary size="small" @click="goToNotificationPage">
              查看全部
            </n-button>
          </div>
        </div>
      </n-popover>

      <n-dropdown :options="userDropdownOptions" @select="handleUserAction">
        <n-avatar round size="small" class="user-avatar">
          <n-icon><PersonOutline /></n-icon>
        </n-avatar>
      </n-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon, NAvatar, NDropdown, NSelect, NButton, NPopover } from 'naive-ui'
import { CreateOutline, SaveOutline, RefreshOutline, AddOutline, PersonOutline, SettingsOutline, TvOutline, NotificationsOutline, SwapHorizontalOutline, TrendingUpOutline, FlashOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
dayjs.locale('zh-cn')
import { fetchIndexQuotes } from '@/api/dashboard'
import type { DashboardModule } from '@/types/dashboard'

const router = useRouter()

// Props
defineProps<{
  editMode: boolean
  currentLayoutId: number | null
  layoutOptions: { label: string; value: number }[]
  unusedModules: DashboardModule[]
}>()

// Emits
const emit = defineEmits<{
  'toggle-edit': []
  'change-layout': [value: number]
  'save': []
  'reset': []
  'add-module': [moduleId: string]
  'user-action': [key: string]
}>()

// 时间状态
const currentTime = ref(dayjs().format('HH:mm:ss'))

// 指数信息
const indexData = ref([
  { code: 'sh', name: '上证', price: 0, change: 0 },
  { code: 'sz', name: '深证', price: 0, change: 0 },
  { code: 'cy', name: '创业板', price: 0, change: 0 },
  { code: 'hs300', name: '沪深300', price: 0, change: 0 }
])

// 接口状态
const dataApiStatus = ref<'healthy' | 'error' | 'warning'>('healthy')
const qmtApiStatus = ref<'healthy' | 'error' | 'warning'>('warning')
const dataApiStatusText = computed(() => dataApiStatus.value === 'healthy' ? '数据正常' : dataApiStatus.value === 'warning' ? '数据延迟' : '数据异常')
const qmtApiStatusText = computed(() => qmtApiStatus.value === 'healthy' ? 'QMT已连接' : qmtApiStatus.value === 'warning' ? 'QMT未连接' : 'QMT异常')

// 用户下拉选项
const userDropdownOptions = [
  { label: '管理页面', key: 'manage', icon: () => h(NIcon, null, { default: () => h(SettingsOutline) }) },
  { label: '全屏模式', key: 'fullscreen', icon: () => h(NIcon, null, { default: () => h(TvOutline) }) }
]

// ==================== 通知相关 ====================

interface NotificationItem {
  id: number
  type: 'system' | 'trade' | 'market' | 'strategy'
  title: string
  content: string
  is_read: boolean
  created_at: string
}

const unreadCount = ref(0)
const recentNotifications = ref<NotificationItem[]>([])

// 加载未读通知数量
async function loadUnreadCount() {
  try {
    const response = await fetch('/api/v1/user-notification/unread-count?user_id=1')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        unreadCount.value = result.data.total || 0
      }
    }
  } catch (e) {
    console.error('加载未读通知数量失败', e)
  }
}

// 加载最近通知
async function loadRecentNotifications() {
  try {
    const response = await fetch('/api/v1/user-notification/recent?limit=5&user_id=1')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        recentNotifications.value = result.data
      }
    }
  } catch (e) {
    console.error('加载最近通知失败', e)
    // 模拟数据
    recentNotifications.value = [
      { id: 1, type: 'trade', title: '平安银行买入成交', content: '以10.25元买入1000股', is_read: false, created_at: '2026-04-23 10:30:00' },
      { id: 2, type: 'strategy', title: '趋势突破策略触发', content: '美的集团突破关键价位', is_read: false, created_at: '2026-04-23 09:45:00' },
      { id: 3, type: 'market', title: '大盘突破3100点', content: '上证指数强势上涨', is_read: true, created_at: '2026-04-22 14:20:00' }
    ]
    unreadCount.value = 2
  }
}

// 格式化通知时间
function formatNotifyTime(time: string): string {
  const date = dayjs(time)
  const now = dayjs()
  const diffHours = now.diff(date, 'hour')

  if (diffHours < 1) {
    return '刚刚'
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffHours < 72) {
    return `${Math.floor(diffHours / 24)}天前`
  } else {
    return date.format('MM-DD HH:mm')
  }
}

// 标记全部已读
async function markAllRead() {
  try {
    const response = await fetch('/api/v1/user-notification/read-all?user_id=1', { method: 'PUT' })
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200) {
        unreadCount.value = 0
        recentNotifications.value.forEach(n => n.is_read = true)
      }
    }
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

// 点击通知
async function handleNotifyClick(notify: NotificationItem) {
  if (!notify.is_read) {
    try {
      const response = await fetch(`/api/v1/user-notification/${notify.id}/read?user_id=1`, { method: 'PUT' })
      if (response.ok) {
        notify.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    } catch (e) {
      console.error('标记已读失败', e)
    }
  }
  router.push(`/notification/${notify.id}`)
}

// 查看全部通知
function goToNotificationPage() {
  router.push('/notification')
}

// 布局变更处理
function handleLayoutChange(val: number) {
  emit('change-layout', val)
}

// 用户操作处理
function handleUserAction(key: string) {
  emit('user-action', key)
}

// ==================== 指数数据 ====================

// 加载指数数据
async function loadIndexData() {
  try {
    const indexes = await fetchIndexQuotes()
    if (indexes && indexes.length > 0) {
      indexData.value = indexes.map((idx: any) => ({
        code: idx.code,
        name: idx.name?.replace('指数', '').replace('成指', '').replace('指', '') || idx.code,
        price: idx.price,
        change: idx.change
      }))
      qmtApiStatus.value = 'healthy'
    }
  } catch (e) {
    console.error('加载指数数据失败', e)
    qmtApiStatus.value = 'error'
    // 模拟数据
    indexData.value = [
      { code: 'sh', name: '上证', price: 3089.34, change: 0.56 },
      { code: 'sz', name: '深证', price: 10234.56, change: 1.23 },
      { code: 'cy', name: '创业板', price: 2156.78, change: -0.45 },
      { code: 'hs300', name: '沪深300', price: 3567.89, change: 0.32 }
    ]
  }
}

// 定时器
let timeTimer: number
let dataTimer: number
let notificationTimer: number

onMounted(() => {
  timeTimer = window.setInterval(() => {
    currentTime.value = dayjs().format('HH:mm:ss')
  }, 1000)

  loadIndexData()
  loadUnreadCount()
  loadRecentNotifications()

  dataTimer = window.setInterval(() => {
    loadIndexData()
  }, 30000)

  notificationTimer = window.setInterval(() => {
    loadUnreadCount()
    loadRecentNotifications()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(timeTimer)
  clearInterval(dataTimer)
  clearInterval(notificationTimer)
})

defineExpose({
  dataApiStatus,
  qmtApiStatus,
  loadData: loadIndexData
})
</script>

<style scoped lang="scss">
.dashboard-header {
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 15px;
  background: rgba(20, 40, 80, 0.6);
  border-radius: 6px;
  border: 1px solid rgba(100, 150, 255, 0.3);

  .index-section {
    display: flex;
    gap: 12px;

    .index-item {
      display: flex;
      align-items: center;
      gap: 4px;

      .index-name {
        color: rgba(255, 255, 255, 0.7);
        font-size: 11px;
      }

      .index-price {
        font-size: 13px;
        font-weight: 600;
      }

      .index-change {
        font-size: 10px;
      }
    }
  }

  .time-section {
    .current-time {
      font-size: 16px;
      font-weight: 600;
      color: #ff4466;
      font-family: 'Courier New', monospace;
      min-width: 70px;
    }
  }

  .status-section {
    display: flex;
    gap: 8px;

    .status-item {
      display: flex;
      align-items: center;
      gap: 3px;

      .status-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;

        &.healthy { background: #00ff88; }
        &.warning { background: #ffaa00; }
        &.error { background: #ff4466; }
      }

      .status-text {
        font-size: 10px;

        &.healthy { color: #00ff88; }
        &.warning { color: #ffaa00; }
        &.error { color: #ff4466; }
      }
    }
  }

  .layout-controls {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-left: auto;
  }

  .user-section {
    display: flex;
    align-items: center;
    gap: 10px;

    .notification-bell {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      cursor: pointer;
      border-radius: 4px;
      transition: background 0.2s;
      position: relative;

      &:hover {
        background: rgba(100, 150, 255, 0.3);
      }

      &.has-unread {
        color: #ff4466;
      }

      .unread-badge {
        position: absolute;
        top: -4px;
        right: -4px;
        background: #ff4466;
        color: #fff;
        font-size: 10px;
        padding: 2px 5px;
        border-radius: 8px;
        min-width: 18px;
        text-align: center;
        font-weight: 500;
      }
    }

    .user-avatar {
      cursor: pointer;
      background: rgba(0, 170, 255, 0.3);
    }
  }
}

// 通知弹窗样式
.notification-popup {
  width: 280px;
  background: rgba(20, 40, 80, 0.95);
  border-radius: 6px;
  border: 1px solid rgba(100, 150, 255, 0.3);

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);

    .popup-title {
      font-size: 14px;
      color: #fff;
      font-weight: 500;
    }
  }

  .popup-content {
    padding: 8px;
    max-height: 250px;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(100, 150, 255, 0.3);
      border-radius: 2px;
    }

    .empty-tip {
      color: rgba(255, 255, 255, 0.6);
      font-size: 12px;
      text-align: center;
      padding: 20px;
    }

    .notification-list {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .notify-item {
      padding: 8px;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s;
      border: 1px solid rgba(100, 150, 255, 0.1);

      &:hover {
        background: rgba(50, 70, 120, 0.4);
      }

      &.unread {
        background: rgba(40, 60, 110, 0.5);
        border-color: rgba(255, 68, 102, 0.3);
      }

      .notify-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;

        &.system { background: rgba(0, 170, 255, 0.2); color: #00aaff; }
        &.trade { background: rgba(255, 68, 102, 0.2); color: #ff4466; }
        &.market { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        &.strategy { background: rgba(255, 170, 0, 0.2); color: #ffaa00; }
      }

      .notify-content {
        flex: 1;
        min-width: 0;

        .notify-title {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.9);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .notify-time {
          font-size: 10px;
          color: rgba(255, 255, 255, 0.5);
          margin-top: 2px;
        }
      }
    }
  }

  .popup-footer {
    padding: 8px 12px;
    border-top: 1px solid rgba(100, 150, 255, 0.2);
    text-align: center;
  }
}

// 涨跌颜色（红涨绿跌）
.rise { color: #ff4466; }
.fall { color: #00ff88; }

// 添加模块弹窗样式
.add-module-list {
  padding: 8px;
  min-width: 120px;
  background: rgba(20, 40, 80, 0.95);
  border-radius: 4px;

  .empty-tip {
    color: rgba(255, 255, 255, 0.6);
    font-size: 12px;
    text-align: center;
    padding: 8px;
  }

  .module-item {
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
    border: 1px solid rgba(100, 150, 255, 0.2);
    margin-bottom: 4px;

    &:last-child {
      margin-bottom: 0;
    }

    &:hover {
      background: rgba(100, 150, 255, 0.3);
      border-color: rgba(100, 150, 255, 0.5);
    }

    .module-name {
      color: #fff;
      font-size: 13px;
      font-weight: 500;
    }
  }
}
</style>