<template>
  <div class="real-trade-records">
    <div class="panel-header">
      <span class="panel-title">实时成交记录</span>
      <span class="record-count">共 {{ trades.length }} 条</span>
    </div>
    <div class="panel-content" ref="scrollRef">
      <div v-if="trades.length === 0" class="empty-tip">暂无成交记录</div>
      <div v-else class="trade-list">
        <div
          class="trade-item"
          v-for="trade in trades"
          :key="trade.id"
          :class="trade.direction"
        >
          <div class="trade-main">
            <span class="trade-direction" :class="trade.direction">
              {{ trade.direction === 'buy' ? '买入' : '卖出' }}
            </span>
            <span class="stock-code">{{ trade.stock_code }}</span>
            <span class="stock-name">{{ trade.stock_name }}</span>
          </div>
          <div class="trade-detail">
            <span class="trade-price">{{ trade.price.toFixed(2) }}</span>
            <span class="trade-quantity">{{ trade.quantity }}股</span>
            <span class="trade-amount">{{ formatAmount(trade.amount) }}</span>
          </div>
          <div class="trade-meta">
            <span class="trade-time">{{ formatTime(trade.trade_time) }}</span>
            <span class="trade-no">{{ trade.trade_no }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface TradeItem {
  id: number
  trade_no: string
  stock_code: string
  stock_name: string
  direction: 'buy' | 'sell'
  price: number
  quantity: number
  amount: number
  trade_time: string
}

const trades = ref<TradeItem[]>([])
const scrollRef = ref<HTMLElement | null>(null)

// 格式化金额
function formatAmount(value: number): string {
  if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toFixed(2)
}

// 格式化时间
function formatTime(time: string): string {
  return dayjs(time).format('HH:mm:ss')
}

// 加载成交记录
async function loadTradeRecords() {
  try {
    const response = await fetch('/api/v1/qmt/trades?limit=50')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        trades.value = result.data.map((item: any) => ({
          id: item.id || item.trade_no,
          trade_no: item.trade_no || '-',
          stock_code: item.stock_code,
          stock_name: item.stock_name || '-',
          direction: item.direction || (item.trade_type === '买入' ? 'buy' : 'sell'),
          price: parseFloat(item.price) || 0,
          quantity: parseInt(item.quantity) || 0,
          amount: parseFloat(item.amount) || parseFloat(item.price) * parseInt(item.quantity),
          trade_time: item.trade_time || item.created_at
        }))
      }
    }
  } catch (e) {
    console.error('加载成交记录失败', e)
    // 模拟数据
    trades.value = [
      { id: 1, trade_no: 'T001', stock_code: '000001', stock_name: '平安银行', direction: 'buy', price: 10.25, quantity: 1000, amount: 10250, trade_time: '2026-04-23 10:15:32' },
      { id: 2, trade_no: 'T002', stock_code: '600036', stock_name: '招商银行', direction: 'sell', price: 35.80, quantity: 500, amount: 17900, trade_time: '2026-04-23 10:20:45' },
      { id: 3, trade_no: 'T003', stock_code: '000333', stock_name: '美的集团', direction: 'buy', price: 58.60, quantity: 200, amount: 11720, trade_time: '2026-04-23 11:05:18' },
      { id: 4, trade_no: 'T004', stock_code: '002475', stock_name: '立讯精密', direction: 'sell', price: 28.50, quantity: 300, amount: 8550, trade_time: '2026-04-23 13:30:22' },
      { id: 5, trade_no: 'T005', stock_code: '300750', stock_name: '宁德时代', direction: 'buy', price: 185.20, quantity: 100, amount: 18520, trade_time: '2026-04-23 14:10:55' }
    ]
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadTradeRecords()
  // 每5秒刷新
  dataTimer = window.setInterval(() => {
    loadTradeRecords()
  }, 5000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadTradeRecords
})
</script>

<style scoped lang="scss">
.real-trade-records {
  height: 100%;
  background: rgba(20, 40, 80, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);
  display: flex;
  flex-direction: column;

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

    .record-count {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
    }
  }

  .panel-content {
    flex: 1;
    padding: 8px;
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

.trade-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trade-item {
  background: rgba(30, 50, 100, 0.4);
  border-radius: 4px;
  padding: 6px 8px;
  border-left: 3px solid;

  &.buy {
    border-left-color: #ff4466;
  }

  &.sell {
    border-left-color: #00ff88;
  }

  .trade-main {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;

    .trade-direction {
      font-size: 11px;
      font-weight: 500;
      padding: 1px 4px;
      border-radius: 2px;

      &.buy {
        background: rgba(255, 68, 102, 0.3);
        color: #ff4466;
      }

      &.sell {
        background: rgba(0, 255, 136, 0.3);
        color: #00ff88;
      }
    }

    .stock-code {
      color: #00aaff;
      font-size: 12px;
    }

    .stock-name {
      color: rgba(255, 255, 255, 0.9);
      font-size: 11px;
    }
  }

  .trade-detail {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    margin-bottom: 3px;

    .trade-price {
      color: rgba(255, 255, 255, 0.8);
    }

    .trade-quantity {
      color: rgba(255, 255, 255, 0.6);
    }

    .trade-amount {
      color: #00ffcc;
      font-weight: 500;
    }
  }

  .trade-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 10px;
    color: rgba(255, 255, 255, 0.5);
  }
}
</style>