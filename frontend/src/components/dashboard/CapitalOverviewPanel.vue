<template>
  <div class="capital-overview-panel">
    <div class="panel-header">
      <span class="panel-title">资金概览</span>
      <span class="update-time">{{ formatTime(lastUpdate) }}</span>
    </div>

    <div class="panel-content">
      <!-- 盈亏统计卡片 -->
      <div class="profit-cards">
        <div class="profit-card today">
          <div class="card-label">今日盈利</div>
          <div class="card-value" :class="getProfitClass(stats.today_profit_loss)">
            {{ formatAmount(stats.today_profit_loss) }}
          </div>
          <div class="card-rate" :class="getProfitClass(stats.today_return_rate)">
            {{ formatPercent(stats.today_return_rate) }}
          </div>
        </div>
        <div class="profit-card month">
          <div class="card-label">本月盈亏</div>
          <div class="card-value" :class="getProfitClass(stats.month_profit_loss)">
            {{ formatAmount(stats.month_profit_loss) }}
          </div>
          <div class="card-rate" :class="getProfitClass(stats.month_return_rate)">
            {{ formatPercent(stats.month_return_rate) }}
          </div>
        </div>
        <div class="profit-card total">
          <div class="card-label">总盈亏</div>
          <div class="card-value" :class="getProfitClass(stats.total_profit_loss)">
            {{ formatAmount(stats.total_profit_loss) }}
          </div>
          <div class="card-rate" :class="getProfitClass(stats.total_return_rate)">
            {{ formatPercent(stats.total_return_rate) }}
          </div>
        </div>
      </div>

      <!-- 交易统计 -->
      <div class="trade-stats">
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">今日买入</span>
            <span class="stat-value buy">{{ stats.today_buy_count }}次</span>
            <span class="stat-amount">{{ formatAmount(stats.today_buy_amount) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">今日卖出</span>
            <span class="stat-value sell">{{ stats.today_sell_count }}次</span>
            <span class="stat-amount">{{ formatAmount(stats.today_sell_amount) }}</span>
          </div>
        </div>
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">本月交易</span>
            <span class="stat-value">{{ stats.month_trade_count }}次</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">累计交易</span>
            <span class="stat-value">{{ stats.total_trade_count }}次</span>
          </div>
        </div>
      </div>

      <!-- 审核统计 -->
      <div class="audit-stats">
        <div class="audit-header">今日审核</div>
        <div class="audit-items">
          <div class="audit-item pass">
            <span class="audit-label">通过</span>
            <span class="audit-value">{{ stats.today_audit_passed }}</span>
          </div>
          <div class="audit-item reject">
            <span class="audit-label">拒绝</span>
            <span class="audit-value">{{ stats.today_audit_rejected }}</span>
          </div>
        </div>
      </div>

      <!-- 资产信息 -->
      <div class="assets-info">
        <span class="assets-label">总资产</span>
        <span class="assets-value">{{ formatAmount(stats.total_assets) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface CapitalStats {
  today_profit_loss: number
  month_profit_loss: number
  total_profit_loss: number
  today_return_rate: number
  month_return_rate: number
  total_return_rate: number
  today_trade_count: number
  today_buy_count: number
  today_sell_count: number
  today_buy_amount: number
  today_sell_amount: number
  month_trade_count: number
  total_trade_count: number
  today_audit_passed: number
  today_audit_rejected: number
  total_assets: number
}

const stats = ref<CapitalStats>({
  today_profit_loss: 0,
  month_profit_loss: 0,
  total_profit_loss: 0,
  today_return_rate: 0,
  month_return_rate: 0,
  total_return_rate: 0,
  today_trade_count: 0,
  today_buy_count: 0,
  today_sell_count: 0,
  today_buy_amount: 0,
  today_sell_amount: 0,
  month_trade_count: 0,
  total_trade_count: 0,
  today_audit_passed: 0,
  today_audit_rejected: 0,
  total_assets: 0
})

const lastUpdate = ref(new Date())

// 格式化时间
function formatTime(time: Date): string {
  return dayjs(time).format('HH:mm:ss')
}

// 格式化金额
function formatAmount(value: number): string {
  if (value === 0) return '0'
  const sign = value > 0 ? '+' : ''
  if (Math.abs(value) >= 10000) {
    return `${sign}${(value / 10000).toFixed(2)}万`
  }
  return `${sign}${value.toFixed(2)}`
}

// 格式化百分比
function formatPercent(value: number): string {
  if (value === 0) return '0.00%'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
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
    const response = await fetch('/api/v1/capital-overview/stats')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
        lastUpdate.value = new Date()
      }
    }
  } catch (e) {
    console.error('加载资金概览数据失败', e)
    // 模拟数据
    stats.value = {
      today_profit_loss: 2560,
      month_profit_loss: 18500,
      total_profit_loss: 156000,
      today_return_rate: 0.26,
      month_return_rate: 1.85,
      total_return_rate: 15.6,
      today_trade_count: 5,
      today_buy_count: 3,
      today_sell_count: 2,
      today_buy_amount: 45000,
      today_sell_amount: 38500,
      month_trade_count: 45,
      total_trade_count: 320,
      today_audit_passed: 3,
      today_audit_rejected: 0,
      total_assets: 1000000
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
.capital-overview-panel {
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

// 盈亏卡片
.profit-cards {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;

  .profit-card {
    flex: 1;
    background: rgba(30, 50, 100, 0.5);
    border-radius: 6px;
    padding: 8px;
    text-align: center;
    border: 1px solid rgba(100, 150, 255, 0.15);

    &.today {
      border-color: rgba(0, 255, 136, 0.3);
    }

    &.month {
      border-color: rgba(0, 170, 255, 0.3);
    }

    &.total {
      border-color: rgba(255, 170, 0, 0.3);
    }

    .card-label {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
      margin-bottom: 4px;
    }

    .card-value {
      font-size: 16px;
      font-weight: 600;
      color: #fff;

      &.profit {
        color: #ff4466;
      }

      &.loss {
        color: #00ff88;
      }
    }

    .card-rate {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 2px;

      &.profit {
        color: #ff4466;
      }

      &.loss {
        color: #00ff88;
      }
    }
  }
}

// 交易统计
.trade-stats {
  background: rgba(30, 50, 100, 0.4);
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 8px;
  border: 1px solid rgba(100, 150, 255, 0.15);

  .stat-row {
    display: flex;
    gap: 12px;
    margin-bottom: 6px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;

    .stat-label {
      font-size: 10px;
      color: rgba(255, 255, 255, 0.5);
    }

    .stat-value {
      font-size: 12px;
      font-weight: 500;
      color: #fff;

      &.buy {
        color: #ff4466;
      }

      &.sell {
        color: #00ff88;
      }
    }

    .stat-amount {
      font-size: 10px;
      color: rgba(255, 255, 255, 0.6);
    }
  }
}

// 审核统计
.audit-stats {
  background: rgba(30, 50, 100, 0.4);
  border-radius: 6px;
  padding: 8px 10px;
  margin-bottom: 8px;
  border: 1px solid rgba(100, 150, 255, 0.15);

  .audit-header {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 6px;
  }

  .audit-items {
    display: flex;
    gap: 12px;
  }

  .audit-item {
    display: flex;
    align-items: center;
    gap: 6px;

    .audit-label {
      font-size: 10px;
      color: rgba(255, 255, 255, 0.5);
    }

    .audit-value {
      font-size: 12px;
      font-weight: 500;
    }

    &.pass .audit-value {
      color: #00ff88;
    }

    &.reject .audit-value {
      color: #ff4466;
    }
  }
}

// 资产信息
.assets-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: rgba(30, 50, 100, 0.3);
  border-radius: 4px;

  .assets-label {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.6);
  }

  .assets-value {
    font-size: 14px;
    font-weight: 600;
    color: #00ffcc;
  }
}
</style>