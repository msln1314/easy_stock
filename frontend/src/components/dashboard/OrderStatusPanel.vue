<template>
  <div class="order-status-panel">
    <div class="panel-header">
      <span class="panel-title">委托状态</span>
      <span class="order-count">今日 {{ stats.total_orders }} 笔</span>
    </div>

    <div class="panel-content">
      <!-- 状态统计 -->
      <div class="status-stats">
        <div class="status-card pending">
          <span class="status-value">{{ stats.status_count?.pending || 0 }}</span>
          <span class="status-label">待成交</span>
        </div>
        <div class="status-card filled">
          <span class="status-value">{{ stats.status_count?.filled || 0 }}</span>
          <span class="status-label">已成交</span>
        </div>
        <div class="status-card partial">
          <span class="status-value">{{ stats.status_count?.partial || 0 }}</span>
          <span class="status-label">部分成交</span>
        </div>
        <div class="status-card cancelled">
          <span class="status-value">{{ stats.status_count?.cancelled || 0 }}</span>
          <span class="status-label">已撤单</span>
        </div>
      </div>

      <!-- 成交率 -->
      <div class="success-rate-section">
        <div class="rate-header">
          <span class="rate-label">成交成功率</span>
          <span class="rate-value">{{ stats.success_rate?.toFixed(1) }}%</span>
        </div>
        <div class="rate-bar">
          <div class="bar-fill" :style="{ width: stats.success_rate + '%' }"></div>
        </div>
      </div>

      <!-- 买卖统计 -->
      <div class="trade-stats">
        <div class="trade-item buy">
          <span class="trade-label">买入委托</span>
          <span class="trade-value">{{ stats.direction_count?.buy || 0 }}笔</span>
          <span class="trade-amount">{{ formatAmount(stats.buy_amount) }}</span>
        </div>
        <div class="trade-item sell">
          <span class="trade-label">卖出委托</span>
          <span class="trade-value">{{ stats.direction_count?.sell || 0 }}笔</span>
          <span class="trade-amount">{{ formatAmount(stats.sell_amount) }}</span>
        </div>
      </div>

      <!-- 委托列表 -->
      <div class="order-list-section">
        <div class="section-header">最新委托</div>
        <div class="order-list">
          <div v-for="order in stats.orders?.slice(0, 5)" :key="order.order_id" class="order-item">
            <span class="order-direction" :class="order.direction">
              {{ order.direction_display }}
            </span>
            <span class="order-stock">{{ order.stock_code }}</span>
            <span class="order-status" :class="order.status">
              {{ order.status_display }}
            </span>
            <span class="order-time">{{ formatTime(order.order_time) }}</span>
          </div>
        </div>
      </div>

      <!-- 待成交金额 -->
      <div class="pending-section" v-if="stats.pending_amount > 0">
        <span class="pending-label">待成交金额</span>
        <span class="pending-value">{{ formatAmount(stats.pending_amount) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface OrderStats {
  total_orders: number
  status_count: { pending: number; filled: number; partial: number; cancelled: number; rejected: number }
  direction_count: { buy: number; sell: number }
  success_rate: number
  buy_amount: number
  sell_amount: number
  orders: any[]
  pending_amount: number
}

const stats = ref<OrderStats>({
  total_orders: 0,
  status_count: { pending: 0, filled: 0, partial: 0, cancelled: 0, rejected: 0 },
  direction_count: { buy: 0, sell: 0 },
  success_rate: 0,
  buy_amount: 0,
  sell_amount: 0,
  orders: [],
  pending_amount: 0
})

function formatAmount(value: number): string {
  if (!value) return '0'
  if (Math.abs(value) >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toFixed(2)
}

function formatTime(time: string): string {
  if (!time) return ''
  return dayjs(time).format('HH:mm')
}

async function loadStats() {
  try {
    const response = await fetch('/api/v1/order-status/overview')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
      }
    }
  } catch (e) {
    console.error('加载委托状态失败', e)
    stats.value = {
      total_orders: 5,
      status_count: { pending: 1, filled: 1, partial: 1, cancelled: 1, rejected: 1 },
      direction_count: { buy: 3, sell: 2 },
      success_rate: 20,
      buy_amount: 45000,
      sell_amount: 23600,
      orders: [
        { order_id: 'ORD001', stock_code: '000001', direction: 'buy', direction_display: '买入', status: 'filled', status_display: '已成交', order_time: '2026-04-23 10:15:00' },
        { order_id: 'ORD002', stock_code: '600036', direction: 'buy', direction_display: '买入', status: 'pending', status_display: '待成交', order_time: '2026-04-23 10:20:00' },
        { order_id: 'ORD003', stock_code: '000333', direction: 'sell', direction_display: '卖出', status: 'partial', status_display: '部分成交', order_time: '2026-04-23 11:05:00' },
        { order_id: 'ORD004', stock_code: '002475', direction: 'sell', direction_display: '卖出', status: 'cancelled', status_display: '已撤单', order_time: '2026-04-23 13:30:00' },
        { order_id: 'ORD005', stock_code: '300750', direction: 'buy', direction_display: '买入', status: 'rejected', status_display: '已拒绝', order_time: '2026-04-23 14:10:00' },
      ],
      pending_amount: 17900
    }
  }
}

let dataTimer: number

onMounted(() => { loadStats(); dataTimer = window.setInterval(loadStats, 10000) })
onUnmounted(() => clearInterval(dataTimer))

defineExpose({ loadData: loadStats })
</script>

<style scoped lang="scss">
.order-status-panel {
  height: 100%;
  background: rgba(20, 40, 80, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .panel-header {
    height: 32px;
    padding: 0 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);
    .panel-title { font-size: 13px; color: #00ffcc; font-weight: 500; }
    .order-count { font-size: 11px; color: rgba(255,255,255,0.6); }
  }

  .panel-content { flex: 1; padding: 10px 12px; overflow-y: auto; }
}

.status-stats {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;

  .status-card {
    flex: 1;
    background: rgba(30,50,100,0.5);
    border-radius: 6px;
    padding: 6px;
    text-align: center;
    border: 1px solid rgba(100,150,255,0.15);

    &.pending { border-color: rgba(255,170,0,0.3); .status-value { color: #ffaa00; } }
    &.filled { border-color: rgba(0,255,136,0.3); .status-value { color: #00ff88; } }
    &.partial { border-color: rgba(0,170,255,0.3); .status-value { color: #00aaff; } }
    &.cancelled { border-color: rgba(255,255,255,0.2); .status-value { color: rgba(255,255,255,0.6); } }

    .status-value { font-size: 16px; font-weight: 600; }
    .status-label { font-size: 10px; color: rgba(255,255,255,0.6); }
  }
}

.success-rate-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);

  .rate-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    .rate-label { font-size: 11px; color: rgba(255,255,255,0.7); }
    .rate-value { font-size: 12px; color: #00ffcc; font-weight: 500; }
  }

  .rate-bar {
    height: 8px;
    background: rgba(30,50,100,0.6);
    border-radius: 4px;
    overflow: hidden;
    .bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #00aaff, #00ff88);
      border-radius: 4px;
    }
  }
}

.trade-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;

  .trade-item {
    flex: 1;
    background: rgba(30,50,100,0.4);
    border-radius: 6px;
    padding: 8px;
    border: 1px solid rgba(100,150,255,0.15);

    &.buy { border-color: rgba(255,68,102,0.3); }
    &.sell { border-color: rgba(0,255,136,0.3); }

    .trade-label { font-size: 10px; color: rgba(255,255,255,0.6); }
    .trade-value { font-size: 14px; color: #fff; font-weight: 500; }
    .trade-amount { font-size: 11px; color: #00ffcc; }
  }
}

.section-header {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 6px;
}

.order-list-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);
}

.order-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;

  .order-direction {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 3px;
    &.buy { background: rgba(255,68,102,0.3); color: #ff4466; }
    &.sell { background: rgba(0,255,136,0.3); color: #00ff88; }
  }

  .order-stock { font-size: 12px; color: #00aaff; }
  .order-status { font-size: 10px;
    &.filled { color: #00ff88; }
    &.pending { color: #ffaa00; }
    &.partial { color: #00aaff; }
    &.cancelled { color: rgba(255,255,255,0.5); }
    &.rejected { color: #ff4466; }
  }
  .order-time { font-size: 10px; color: rgba(255,255,255,0.5); }
}

.pending-section {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background: rgba(255,170,0,0.2);
  border-radius: 4px;

  .pending-label { font-size: 11px; color: rgba(255,255,255,0.7); }
  .pending-value { font-size: 12px; color: #ffaa00; font-weight: 500; }
}
</style>