<template>
  <div class="notification-panel">
    <div class="panel-header">
      <span class="panel-title">信息通知</span>
      <span class="unread-badge" v-if="unreadTotal > 0">{{ unreadTotal }}</span>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stats-row">
        <div class="stat-card" @click="filterByType('system')">
          <div class="stat-icon system">
            <n-icon size="18"><SettingsOutline /></n-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.system }}</span>
            <span class="stat-label">系统</span>
          </div>
          <span class="unread-dot" v-if="unreadByType.system > 0">{{ unreadByType.system }}</span>
        </div>
        <div class="stat-card" @click="filterByType('trade')">
          <div class="stat-icon trade">
            <n-icon size="18"><SwapHorizontalOutline /></n-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.trade }}</span>
            <span class="stat-label">交易</span>
          </div>
          <span class="unread-dot" v-if="unreadByType.trade > 0">{{ unreadByType.trade }}</span>
        </div>
        <div class="stat-card" @click="filterByType('market')">
          <div class="stat-icon market">
            <n-icon size="18"><TrendingUpOutline /></n-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.market }}</span>
            <span class="stat-label">市场</span>
          </div>
          <span class="unread-dot" v-if="unreadByType.market > 0">{{ unreadByType.market }}</span>
        </div>
        <div class="stat-card" @click="filterByType('strategy')">
          <div class="stat-icon strategy">
            <n-icon size="18"><FlashOutline /></n-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stats.strategy }}</span>
            <span class="stat-label">策略</span>
          </div>
          <span class="unread-dot" v-if="unreadByType.strategy > 0">{{ unreadByType.strategy }}</span>
        </div>
      </div>
      <div class="stats-summary">
        <span>近3天共 {{ total }} 条通知</span>
        <span class="unread-summary" v-if="unreadTotal > 0">{{ unreadTotal }} 条未读</span>
      </div>
    </div>

    <!-- 最近通知列表 -->
    <div class="notification-list">
      <div class="list-header">
        <span class="list-title">最近通知</span>
        <n-button quaternary size="tiny" @click="goToNotificationPage">
          查看全部
          <template #icon><n-icon size="12"><ChevronForwardOutline /></n-icon></template>
        </n-button>
      </div>
      <div class="list-content">
        <div v-if="recentNotifications.length === 0" class="empty-tip">暂无通知</div>
        <div
          v-for="notify in recentNotifications"
          :key="notify.id"
          class="notify-item"
          :class="[notify.type, { unread: !notify.is_read }]"
          @click="handleNotificationClick(notify)"
        >
          <div class="notify-icon" :class="notify.type">
            <n-icon size="16">
              <SettingsOutline v-if="notify.type === 'system'" />
              <SwapHorizontalOutline v-else-if="notify.type === 'trade'" />
              <TrendingUpOutline v-else-if="notify.type === 'market'" />
              <FlashOutline v-else />
            </n-icon>
          </div>
          <div class="notify-content">
            <div class="notify-title">{{ notify.title }}</div>
            <div class="notify-time">{{ formatTime(notify.created_at) }}</div>
          </div>
          <span class="unread-indicator" v-if="!notify.is_read"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { NIcon, NButton } from 'naive-ui'
import { SettingsOutline, SwapHorizontalOutline, TrendingUpOutline, FlashOutline, ChevronForwardOutline } from '@vicons/ionicons5'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'

const router = useRouter()

interface NotificationItem {
  id: number
  type: 'system' | 'trade' | 'market' | 'strategy'
  title: string
  content: string
  is_read: boolean
  created_at: string
}

// 统计数据
const stats = ref({
  system: 0,
  trade: 0,
  market: 0,
  strategy: 0
})

// 未读统计
const unreadByType = ref({
  system: 0,
  trade: 0,
  market: 0,
  strategy: 0
})

// 最近通知
const recentNotifications = ref<NotificationItem[]>([])

// 总计
const total = computed(() => stats.value.system + stats.value.trade + stats.value.market + stats.value.strategy)
const unreadTotal = computed(() => unreadByType.value.system + unreadByType.value.trade + unreadByType.value.market + unreadByType.value.strategy)

// 格式化时间
function formatTime(time: string): string {
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

// 按类型筛选
function filterByType(type: string) {
  router.push(`/notification?type=${type}`)
}

// 查看全部通知
function goToNotificationPage() {
  router.push('/notification')
}

// 点击通知
function handleNotificationClick(notify: NotificationItem) {
  // 标记为已读（这里可以调用API）
  notify.is_read = true
  router.push(`/notification/${notify.id}`)
}

// 加载统计数据
async function loadStats() {
  try {
    const response = await fetch('/api/v1/notification/stats?days=3')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data.stats || stats.value
        unreadByType.value = result.data.unread || unreadByType.value
      }
    }
  } catch (e) {
    console.error('加载通知统计失败', e)
  }
}

// 加载最近通知
async function loadRecentNotifications() {
  try {
    const response = await fetch('/api/v1/notification/recent?limit=3')
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
    stats.value = { system: 2, trade: 5, market: 3, strategy: 8 }
    unreadByType.value = { system: 1, trade: 2, market: 0, strategy: 3 }
  }
}

// 刷新数据
function refreshData() {
  loadStats()
  loadRecentNotifications()
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadStats()
  loadRecentNotifications()

  // 每30秒刷新
  dataTimer = window.setInterval(() => {
    loadStats()
    loadRecentNotifications()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: refreshData
})
</script>

<style scoped lang="scss">
.notification-panel {
  height: 100%;
  background: rgba(20, 40, 80, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .panel-header {
    height: 32px;
    flex-shrink: 0;
    padding: 0 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);

    .panel-title {
      font-size: 13px;
      color: #00ffcc;
      font-weight: 500;
    }

    .unread-badge {
      background: #ff4466;
      color: #fff;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 500;
    }
  }
}

// 统计区域
.stats-section {
  flex-shrink: 0;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(100, 150, 255, 0.15);

  .stats-row {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;

    .stat-card {
      flex: 1;
      background: rgba(30, 50, 100, 0.4);
      border-radius: 6px;
      padding: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      transition: all 0.2s;
      border: 1px solid rgba(100, 150, 255, 0.1);

      &:hover {
        background: rgba(50, 70, 120, 0.5);
        border-color: rgba(100, 150, 255, 0.3);
      }

      .stat-icon {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;

        &.system { background: rgba(0, 170, 255, 0.3); color: #00aaff; }
        &.trade { background: rgba(255, 68, 102, 0.3); color: #ff4466; }
        &.market { background: rgba(0, 255, 136, 0.3); color: #00ff88; }
        &.strategy { background: rgba(255, 170, 0, 0.3); color: #ffaa00; }
      }

      .stat-info {
        flex: 1;
        display: flex;
        flex-direction: column;

        .stat-value {
          font-size: 16px;
          font-weight: 600;
          color: #fff;
        }

        .stat-label {
          font-size: 10px;
          color: rgba(255, 255, 255, 0.6);
        }
      }

      .unread-dot {
        background: #ff4466;
        color: #fff;
        font-size: 10px;
        padding: 1px 5px;
        border-radius: 8px;
        min-width: 18px;
        text-align: center;
      }
    }
  }

  .stats-summary {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.6);

    .unread-summary {
      color: #ff4466;
      font-weight: 500;
    }
  }
}

// 通知列表
.notification-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;

  .list-header {
    flex-shrink: 0;
    padding: 8px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .list-title {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
    }
  }

  .list-content {
    flex: 1;
    padding: 0 12px 10px;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(100, 150, 255, 0.3);
      border-radius: 2px;
    }

    .empty-tip {
      color: rgba(255, 255, 255, 0.5);
      font-size: 12px;
      text-align: center;
      padding: 20px;
    }

    .notify-item {
      padding: 10px;
      margin-bottom: 6px;
      background: rgba(30, 50, 100, 0.3);
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      transition: all 0.2s;
      border: 1px solid rgba(100, 150, 255, 0.1);

      &:last-child {
        margin-bottom: 0;
      }

      &:hover {
        background: rgba(50, 70, 120, 0.4);
      }

      &.unread {
        background: rgba(40, 60, 110, 0.5);
        border-color: rgba(255, 68, 102, 0.3);
      }

      .notify-icon {
        width: 24px;
        height: 24px;
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

      .unread-indicator {
        width: 8px;
        height: 8px;
        background: #ff4466;
        border-radius: 50%;
        flex-shrink: 0;
      }
    }
  }
}
</style>