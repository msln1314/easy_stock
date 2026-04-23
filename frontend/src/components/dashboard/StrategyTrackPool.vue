<template>
  <div class="strategy-track-pool">
    <div class="panel-header">
      <span class="panel-title">策略选股池</span>
      <span class="pool-date">{{ todayDate }}</span>
    </div>
    <div class="panel-content">
      <div v-if="stocks.length === 0" class="empty-tip">今日暂无策略选股</div>
      <div v-else class="stock-list">
        <div
          class="stock-item"
          v-for="stock in stocks"
          :key="stock.id"
          :class="stock.status"
        >
          <div class="stock-main">
            <span class="stock-code">{{ stock.stock_code }}</span>
            <span class="stock-name">{{ stock.stock_name }}</span>
            <span class="strategy-tag">{{ stock.strategy_key }}</span>
          </div>
          <div class="stock-meta">
            <span class="anomaly-type" :class="stock.anomaly_type">{{ formatAnomalyType(stock.anomaly_type) }}</span>
            <span class="confidence">
              <n-progress
                type="line"
                :percentage="stock.confidence"
                :show-indicator="false"
                :height="4"
                :color="getConfidenceColor(stock.confidence)"
                rail-color="rgba(100, 150, 255, 0.2)"
              />
              <span class="confidence-value">{{ stock.confidence }}%</span>
            </span>
            <span class="status-tag" :class="stock.status">{{ formatStatus(stock.status) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { NProgress } from 'naive-ui'
import dayjs from 'dayjs'

interface StockItem {
  id: number
  stock_code: string
  stock_name: string
  strategy_key: string
  anomaly_type: string
  confidence: number
  status: string
}

const todayDate = ref(dayjs().format('YYYY-MM-DD'))
const stocks = ref<StockItem[]>([])

// 异动类型映射
const anomalyTypeMap: Record<string, string> = {
  'breakout': '突破',
  'signal_buy': '买入信号',
  'pattern': '形态',
  'volume': '量异动'
}

// 状态映射
const statusMap: Record<string, string> = {
  'pending': '待观察',
  'verified': '已验证',
  'failed': '已失效',
  'expired': '已过期'
}

// 格式化异动类型
function formatAnomalyType(type: string): string {
  return anomalyTypeMap[type] || type
}

// 格式化状态
function formatStatus(status: string): string {
  return statusMap[status] || status
}

// 获取置信度颜色
function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return '#00ff88'
  if (confidence >= 60) return '#00ffcc'
  if (confidence >= 40) return '#ffaa00'
  return '#ff4466'
}

// 加载策略选股池数据
async function loadStrategyPool() {
  try {
    const response = await fetch('/api/v1/stock-pick/track-pool/today')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stocks.value = result.data.map((item: any) => ({
          id: item.id,
          stock_code: item.stock_code,
          stock_name: item.stock_name || '-',
          strategy_key: item.strategy_key,
          anomaly_type: item.anomaly_type,
          confidence: parseFloat(item.confidence) || 50,
          status: item.status
        }))
      }
    }
  } catch (e) {
    console.error('加载策略选股池失败', e)
    // 模拟数据
    stocks.value = [
      { id: 1, stock_code: '000001', stock_name: '平安银行', strategy_key: '趋势突破', anomaly_type: 'breakout', confidence: 85, status: 'pending' },
      { id: 2, stock_code: '600036', stock_name: '招商银行', strategy_key: '量价异动', anomaly_type: 'volume', confidence: 72, status: 'verified' },
      { id: 3, stock_code: '000333', stock_name: '美的集团', strategy_key: '形态识别', anomaly_type: 'pattern', confidence: 68, status: 'pending' },
      { id: 4, stock_code: '002475', stock_name: '立讯精密', strategy_key: '趋势突破', anomaly_type: 'signal_buy', confidence: 55, status: 'pending' },
      { id: 5, stock_code: '300750', stock_name: '宁德时代', strategy_key: '量价异动', anomaly_type: 'volume', confidence: 90, status: 'verified' }
    ]
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadStrategyPool()
  // 每30秒刷新
  dataTimer = window.setInterval(() => {
    loadStrategyPool()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadStrategyPool
})
</script>

<style scoped lang="scss">
.strategy-track-pool {
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

    .pool-date {
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

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stock-item {
  background: rgba(30, 50, 100, 0.5);
  border-radius: 6px;
  padding: 8px 10px;
  border: 1px solid rgba(100, 150, 255, 0.15);

  &.verified {
    border-color: rgba(0, 255, 136, 0.3);
  }

  &.failed, &.expired {
    border-color: rgba(255, 68, 102, 0.3);
    opacity: 0.7;
  }

  .stock-main {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;

    .stock-code {
      color: #00aaff;
      font-size: 13px;
      font-weight: 500;
    }

    .stock-name {
      color: rgba(255, 255, 255, 0.9);
      font-size: 12px;
    }

    .strategy-tag {
      background: rgba(100, 150, 255, 0.3);
      color: #00ffcc;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 3px;
    }
  }

  .stock-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;

    .anomaly-type {
      color: rgba(255, 255, 255, 0.7);
      padding: 2px 6px;
      border-radius: 3px;
      background: rgba(50, 70, 120, 0.5);

      &.breakout { color: #ff4466; }
      &.signal_buy { color: #00ff88; }
      &.pattern { color: #00aaff; }
      &.volume { color: #ffaa00; }
    }

    .confidence {
      display: flex;
      align-items: center;
      gap: 4px;
      flex: 1;
      max-width: 100px;

      .confidence-value {
        color: rgba(255, 255, 255, 0.8);
        font-size: 10px;
      }
    }

    .status-tag {
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 3px;

      &.pending {
        background: rgba(255, 170, 0, 0.3);
        color: #ffaa00;
      }

      &.verified {
        background: rgba(0, 255, 136, 0.3);
        color: #00ff88;
      }

      &.failed, &.expired {
        background: rgba(255, 68, 102, 0.3);
        color: #ff4466;
      }
    }
  }
}
</style>