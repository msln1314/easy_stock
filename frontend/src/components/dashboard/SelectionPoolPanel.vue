<template>
  <div class="selection-pool-panel">
    <div class="panel-header">
      <span class="panel-title">选股池排序</span>
      <span class="panel-count">共 {{ stocks.length }} 只</span>
    </div>
    <div class="panel-content scroll-content">
      <div v-if="stocks.length === 0" class="empty-tip">
        暂无选股数据
      </div>
      <div v-else class="stock-list">
        <div class="stock-item" v-for="(stock, idx) in stocks" :key="stock.code">
          <span class="rank-num">{{ idx + 1 }}</span>
          <span class="stock-code">{{ stock.code }}</span>
          <span class="stock-name">{{ stock.name }}</span>
          <span class="stock-score">{{ stock.score }}</span>
          <span class="stock-entry">{{ formatPrice(stock.entryPrice) }}</span>
          <span class="stock-current">{{ formatPrice(stock.currentPrice) }}</span>
          <span class="stock-change" :class="stock.change >= 0 ? 'rise' : 'fall'">
            {{ formatChange(stock.change) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchTodayPool } from '@/api/stockPick'

interface PoolStock {
  code: string
  name: string
  score: number
  entryPrice: number | null
  currentPrice: number | null
  change: number
  monitorType?: string
}

const stocks = ref<PoolStock[]>([])

// 格式化价格
function formatPrice(value: number | null): string {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

// 格式化涨跌幅
function formatChange(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return sign + value.toFixed(2) + '%'
}

// 加载选股池数据
async function loadSelectionPool() {
  try {
    // 先从监控股票池获取
    const response = await fetch('/api/v1/monitor/stocks')
    const result = await response.json()

    if (result.code === 200 && result.data) {
      stocks.value = result.data
        .filter((item: any) => item.stock_code && item.stock_code !== '2222')
        .map((item: any) => ({
          code: item.stock_code,
          name: item.stock_name,
          score: item.conditions?.length || 0,
          entryPrice: item.entry_price,
          currentPrice: item.last_price,
          change: item.change_percent || 0,
          monitorType: item.monitor_type
        }))

      // 刷新实时行情
      refreshQuotes()
    }
  } catch (e) {
    console.error('加载选股池失败', e)
  }
}

// 刷新实时行情
async function refreshQuotes() {
  const codes = stocks.value.slice(0, 20).map(s => s.code)

  for (const code of codes) {
    try {
      const qmtCode = code.startsWith('6') ? `${code}.SH` : `${code}.SZ`
      const response = await fetch(`/api/v1/position/quote/${qmtCode}`)
      const result = await response.json()

      if (result.code === 200 && result.data && result.data.price) {
        const stock = stocks.value.find(s => s.code === code)
        if (stock) {
          const preClose = result.data.pre_close || 0
          const price = result.data.price || 0
          stock.currentPrice = price
          stock.change = preClose > 0 ? ((price - preClose) / preClose * 100) : 0
        }
      }
    } catch (e) {
      console.error(`获取 ${code} 行情失败`, e)
    }
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadSelectionPool()
  dataTimer = window.setInterval(() => {
    loadSelectionPool()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadSelectionPool
})
</script>

<style scoped lang="scss">
.selection-pool-panel {
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
      color: #00aaff;
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

.stock-item {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(100, 150, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;

  .rank-num {
    color: #00ffcc;
    font-weight: 600;
    min-width: 20px;
  }

  .stock-code {
    color: #00aaff;
    min-width: 60px;
  }

  .stock-name {
    color: rgba(255, 255, 255, 0.9);
    min-width: 70px;
  }

  .stock-score {
    color: #00ff88;
    font-weight: 500;
    min-width: 30px;
  }

  .stock-entry {
    color: rgba(255, 255, 255, 0.7);
    min-width: 50px;
  }

  .stock-current {
    color: rgba(255, 255, 255, 0.8);
    min-width: 50px;
  }

  .stock-change {
    min-width: 60px;
    font-weight: 500;
  }
}

.rise { color: #ff4466; }
.fall { color: #00ff88; }
</style>