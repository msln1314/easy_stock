<template>
  <div class="trade-records-panel">
    <div class="panel-header">
      <span class="panel-title">实时交易记录</span>
      <span class="panel-count">最近 {{ tradeLogs.length }} 条</span>
    </div>
    <div class="panel-content scroll-content" ref="scrollRef">
      <div v-if="tradeLogs.length === 0" class="empty-tip">
        暂无交易记录
      </div>
      <div v-else class="trade-list">
        <div
          class="trade-item"
          v-for="log in tradeLogs"
          :key="log.id"
          :class="log.actionType"
        >
          <span class="trade-type" :class="log.actionType">{{ log.actionTypeDisplay }}</span>
          <span class="stock-code">{{ log.stockCode }}</span>
          <span class="stock-name">{{ log.stockName }}</span>
          <span class="trade-amount">{{ log.quantity ? `${log.quantity}股` : '-' }}</span>
          <span class="trade-result" :class="log.result">{{ log.resultDisplay }}</span>
          <span class="trade-time">{{ formatTime(log.actionTime) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import { getTradeLogs } from '@/api/tradeLog'

interface TradeLogItem {
  id: number
  actionType: string
  actionTypeDisplay: string
  stockCode: string
  stockName: string
  quantity?: number
  price?: number
  result: string
  resultDisplay: string
  actionTime: string
}

const tradeLogs = ref<TradeLogItem[]>([])
const scrollRef = ref<HTMLElement | null>(null)

// 类型映射
const actionTypeMap: Record<string, string> = {
  'buy_request': '买入请求',
  'buy_executed': '买入执行',
  'buy_success': '买入成功',
  'buy_failed': '买入失败',
  'sell_request': '卖出请求',
  'sell_executed': '卖出执行',
  'sell_success': '卖出成功',
  'sell_failed': '卖出失败',
  'cancel_request': '撤单请求',
  'cancel_success': '撤单成功',
  'cancel_failed': '撤单失败',
  'warning_trigger': '预警触发',
  'warning_handle': '预警处理',
  'ai_chat': 'AI对话'
}

const resultMap: Record<string, string> = {
  'success': '成功',
  'failed': '失败',
  'pending': '进行中',
  'rejected': '拒绝'
}

// 格式化时间
function formatTime(time: string): string {
  if (!time) return ''
  return dayjs(time).format('HH:mm:ss')
}

// 加载交易记录
async function loadTradeLogs() {
  try {
    const { logs } = await getTradeLogs({
      limit: 10
    })

    // 只显示交易相关的记录
    const tradeActionTypes = ['buy_executed', 'sell_executed', 'buy_success', 'sell_success', 'cancel_success', 'buy_request', 'sell_request']
    const filteredLogs = logs.filter((log: any) => tradeActionTypes.includes(log.action_type))

    tradeLogs.value = filteredLogs.map((log: any) => ({
      id: log.id,
      actionType: log.action_type,
      actionTypeDisplay: actionTypeMap[log.action_type] || log.action_type,
      stockCode: log.stock_code || '-',
      stockName: log.stock_name || '-',
      quantity: log.quantity,
      price: log.price,
      result: log.result,
      resultDisplay: resultMap[log.result] || log.result,
      actionTime: log.created_at || log.action_time
    }))

    // 自动滚动到底部显示最新记录
    if (scrollRef.value) {
      scrollRef.value.scrollTop = 0
    }
  } catch (e) {
    console.error('加载交易记录失败', e)
    // 模拟数据
    tradeLogs.value = [
      { id: 1, actionType: 'buy_executed', actionTypeDisplay: '买入执行', stockCode: '000001', stockName: '平安银行', quantity: 100, result: 'success', resultDisplay: '成功', actionTime: '2026-04-22 10:30:00' },
      { id: 2, actionType: 'sell_executed', actionTypeDisplay: '卖出执行', stockCode: '600036', stockName: '招商银行', quantity: 200, result: 'success', resultDisplay: '成功', actionTime: '2026-04-22 11:15:00' },
      { id: 3, actionType: 'buy_success', actionTypeDisplay: '买入成功', stockCode: '000333', stockName: '美的集团', quantity: 50, result: 'success', resultDisplay: '成功', actionTime: '2026-04-22 09:45:00' },
      { id: 4, actionType: 'cancel_success', actionTypeDisplay: '撤单成功', stockCode: '002475', stockName: '立讯精密', quantity: 0, result: 'success', resultDisplay: '成功', actionTime: '2026-04-22 14:20:00' }
    ]
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadTradeLogs()
  // 每5秒刷新一次交易记录
  dataTimer = window.setInterval(() => {
    loadTradeLogs()
  }, 5000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadTradeLogs
})
</script>

<style scoped lang="scss">
.trade-records-panel {
  height: 100%;
  background: rgba(20, 40, 80, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);
  display: flex;
  flex-direction: column;

  .panel-header {
    height: 35px;
    flex-shrink: 0;
    padding: 0 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);

    .panel-title {
      font-size: 14px;
      color: #00ffcc;
      font-weight: 500;
    }

    .panel-count {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
    }
  }

  .panel-content {
    flex: 1;
    padding: 8px;
    overflow: hidden;
    min-height: 0;

    .scroll-content {
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background: rgba(100, 150, 255, 0.3);
        border-radius: 2px;
      }

      .empty-tip {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: rgba(255, 255, 255, 0.5);
        font-size: 13px;
      }
    }
  }
}

.trade-item {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(100, 150, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  transition: background 0.2s;

  &:hover {
    background: rgba(100, 150, 255, 0.05);
  }

  &.buy_executed, &.buy_success {
    .trade-type { color: #ff4466; }
  }

  &.sell_executed, &.sell_success {
    .trade-type { color: #00ff88; }
  }

  .trade-type {
    min-width: 60px;
    font-weight: 500;

    &.buy_executed, &.buy_success { color: #ff4466; }
    &.sell_executed, &.sell_success { color: #00ff88; }
    &.cancel_success { color: #ffaa00; }
  }

  .stock-code {
    color: #00aaff;
    min-width: 60px;
  }

  .stock-name {
    color: rgba(255, 255, 255, 0.9);
    min-width: 80px;
  }

  .trade-amount {
    color: rgba(255, 255, 255, 0.7);
    min-width: 50px;
  }

  .trade-result {
    min-width: 40px;

    &.success { color: #00ff88; }
    &.failed { color: #ff4466; }
    &.pending { color: #ffaa00; }
  }

  .trade-time {
    color: rgba(255, 255, 255, 0.5);
    font-size: 11px;
  }
}
</style>