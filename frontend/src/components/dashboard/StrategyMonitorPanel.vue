<template>
  <div class="strategy-monitor-panel">
    <div class="panel-header">
      <span class="panel-title">策略监控</span>
      <span class="update-time">{{ formatTime(lastUpdate) }}</span>
    </div>

    <div class="panel-content">
      <!-- 策略统计卡片 -->
      <div class="stats-row">
        <div class="stat-item total">
          <div class="stat-value">{{ stats.total_strategies }}</div>
          <div class="stat-label">总策略</div>
        </div>
        <div class="stat-item running">
          <div class="stat-value">{{ stats.running }}</div>
          <div class="stat-label">运行中</div>
        </div>
        <div class="stat-item abnormal">
          <div class="stat-value">{{ stats.abnormal }}</div>
          <div class="stat-label">异常</div>
          <span class="stat-badge" v-if="stats.abnormal > 0">!</span>
        </div>
      </div>

      <!-- 收益统计 -->
      <div class="profit-section">
        <div class="profit-row">
          <div class="profit-item">
            <span class="profit-label">总收益率</span>
            <span class="profit-value" :class="getProfitClass(stats.total_return)">
              {{ formatPercent(stats.total_return) }}
            </span>
          </div>
          <div class="profit-item">
            <span class="profit-label">今日收益</span>
            <span class="profit-value" :class="getProfitClass(stats.today_return)">
              {{ formatPercent(stats.today_return) }}
            </span>
          </div>
        </div>
        <div class="profit-row">
          <div class="profit-item">
            <span class="profit-label">今日盈亏</span>
            <span class="profit-value" :class="getProfitClass(stats.today_profit_loss)">
              {{ formatAmount(stats.today_profit_loss) }}
            </span>
          </div>
          <div class="profit-item">
            <span class="profit-label">成功率</span>
            <span class="profit-value success-rate">{{ stats.strategy_success_rate }}%</span>
          </div>
        </div>
      </div>

      <!-- 今日股池 -->
      <div class="pool-section">
        <div class="pool-header">
          <span class="pool-title">今日股池</span>
          <span class="pool-count">{{ stats.today_pool_count }}只</span>
        </div>
        <div class="pool-stats">
          <div class="pool-stat">
            <span class="pool-stat-label">执行成功</span>
            <span class="pool-stat-value success">{{ stats.today_success }}</span>
          </div>
          <div class="pool-stat">
            <span class="pool-stat-label">执行失败</span>
            <span class="pool-stat-value danger" v-if="stats.today_failed > 0">{{ stats.today_failed }}</span>
            <span class="pool-stat-value" v-else>0</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface StrategyMonitorStats {
  total_strategies: number
  pick_strategies: number
  rotation_strategies: number
  running: number
  paused: number
  abnormal: number
  today_running: number
  today_failed: number
  today_success: number
  total_return: number
  today_return: number
  today_profit_loss: number
  today_pool_count: number
  strategy_success_rate: number
}

const stats = ref<StrategyMonitorStats>({
  total_strategies: 0,
  pick_strategies: 0,
  rotation_strategies: 0,
  running: 0,
  paused: 0,
  abnormal: 0,
  today_running: 0,
  today_failed: 0,
  today_success: 0,
  total_return: 0,
  today_return: 0,
  today_profit_loss: 0,
  today_pool_count: 0,
  strategy_success_rate: 0
})

const lastUpdate = ref(new Date())

// 格式化时间
function formatTime(time: Date): string {
  return dayjs(time).format('HH:mm:ss')
}

// 格式化百分比
function formatPercent(value: number): string {
  if (value === 0) return '0.00%'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

// 格式化金额
function formatAmount(value: number): string {
  const sign = value > 0 ? '+' : ''
  if (Math.abs(value) >= 10000) {
    return `${sign}${(value / 10000).toFixed(2)}万`
  }
  return `${sign}${value.toFixed(2)}`
}

// 获取收益样式类
function getProfitClass(value: number): string {
  if (value > 0) return 'profit'
  if (value < 0) return 'loss'
  return ''
}

// 加载统计数据
async function loadStats() {
  try {
    const response = await fetch('/api/v1/strategy-monitor/stats')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
        lastUpdate.value = new Date()
      }
    }
  } catch (e) {
    console.error('加载策略监控数据失败', e)
    // 模拟数据
    stats.value = {
      total_strategies: 12,
      pick_strategies: 8,
      rotation_strategies: 4,
      running: 10,
      paused: 2,
      abnormal: 1,
      today_running: 3,
      today_failed: 0,
      today_success: 8,
      total_return: 15.6,
      today_return: 0.8,
      today_profit_loss: 2560,
      today_pool_count: 5,
      strategy_success_rate: 72.5
    }
    lastUpdate.value = new Date()
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadStats()
  dataTimer = window.setInterval(() => {
    loadStats()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadStats
})
</script>

<style scoped lang="scss">
.strategy-monitor-panel {
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

    .update-time {
      font-size: 10px;
      color: rgba(255, 255, 255, 0.5);
    }
  }

  .panel-content {
    flex: 1;
    padding: 10px 12px;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(100, 150, 255, 0.3);
      border-radius: 2px;
    }
  }
}

// 统计卡片行
.stats-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;

  .stat-item {
    flex: 1;
    background: rgba(30, 50, 100, 0.5);
    border-radius: 6px;
    padding: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    border: 1px solid rgba(100, 150, 255, 0.15);

    &.total {
      border-color: rgba(0, 170, 255, 0.3);
      .stat-value { color: #00aaff; }
    }

    &.running {
      border-color: rgba(0, 255, 136, 0.3);
      .stat-value { color: #00ff88; }
    }

    &.abnormal {
      border-color: rgba(255, 68, 102, 0.3);
      .stat-value { color: #ff4466; }
    }

    .stat-value {
      font-size: 20px;
      font-weight: 600;
    }

    .stat-label {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 2px;
    }

    .stat-badge {
      background: #ff4466;
      color: #fff;
      font-size: 10px;
      font-weight: bold;
      width: 16px;
      height: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      position: absolute;
      top: -4px;
      right: -4px;
    }
  }
}

// 收益统计
.profit-section {
  background: rgba(30, 50, 100, 0.4);
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid rgba(100, 150, 255, 0.15);

  .profit-row {
    display: flex;
    gap: 12px;
    margin-bottom: 6px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .profit-item {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .profit-label {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
    }

    .profit-value {
      font-size: 14px;
      font-weight: 600;
      color: #fff;

      &.profit {
        color: #ff4466;
      }

      &.loss {
        color: #00ff88;
      }

      &.success-rate {
        color: #00ffcc;
      }
    }
  }
}

// 今日股池
.pool-section {
  background: rgba(30, 50, 100, 0.4);
  border-radius: 6px;
  padding: 10px;
  border: 1px solid rgba(100, 150, 255, 0.15);

  .pool-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .pool-title {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
    }

    .pool-count {
      font-size: 11px;
      color: #00ffcc;
    }
  }

  .pool-stats {
    display: flex;
    gap: 12px;

    .pool-stat {
      display: flex;
      align-items: center;
      gap: 4px;

      .pool-stat-label {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.5);
      }

      .pool-stat-value {
        font-size: 12px;
        font-weight: 500;
        color: #fff;

        &.success {
          color: #00ff88;
        }

        &.danger {
          color: #ff4466;
        }
      }
    }
  }
}
</style>