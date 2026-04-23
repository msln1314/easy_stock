<template>
  <div class="sell-warning-panel">
    <div class="panel-header">
      <span class="panel-title">卖出预警池</span>
      <span class="panel-count">共 {{ warningStocks.length }} 只</span>
    </div>
    <div class="panel-content scroll-content">
      <div v-if="warningStocks.length === 0" class="empty-tip">
        暂无预警股票
      </div>
      <div v-else class="stock-list">
        <div class="stock-item" v-for="stock in warningStocks" :key="stock.code">
          <span class="stock-code">{{ stock.code }}</span>
          <span class="stock-name">{{ stock.name }}</span>
          <span class="warning-reason">{{ stock.reason }}</span>
          <span class="warning-time">{{ formatTime(stock.triggerTime) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface WarningStock {
  code: string
  name: string
  reason: string
  triggerTime: string
  strategy?: string
}

const warningStocks = ref<WarningStock[]>([])

// 格式化时间
function formatTime(time: string): string {
  if (!time) return ''
  return dayjs(time).format('HH:mm')
}

// 加载预警股票数据
async function loadWarningStocks() {
  try {
    const response = await fetch('/api/v1/warning/stocks?status=active')
    const result = await response.json()
    if (result.code === 200 && result.data) {
      warningStocks.value = result.data.map((item: any) => ({
        code: item.stock_code,
        name: item.stock_name,
        reason: item.warning_reason || item.condition_name,
        triggerTime: item.trigger_time || item.created_at,
        strategy: item.strategy_name
      }))
    }
  } catch (e) {
    console.error('加载预警股票失败', e)
    // 模拟数据
    warningStocks.value = [
      { code: '000001', name: '平安银行', reason: '跌破止损线', triggerTime: '2026-04-22 10:30:00' },
      { code: '600036', name: '招商银行', reason: '技术指标转弱', triggerTime: '2026-04-22 11:15:00' },
      { code: '000333', name: '美的集团', reason: '成交量萎缩', triggerTime: '2026-04-22 09:45:00' }
    ]
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadWarningStocks()
  dataTimer = window.setInterval(() => {
    loadWarningStocks()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadWarningStocks
})
</script>

<style scoped lang="scss">
.sell-warning-panel {
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
      color: #ff4466;
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
        background: rgba(255, 100, 100, 0.3);
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
  border-bottom: 1px solid rgba(255, 100, 100, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;

  .stock-code {
    color: #00aaff;
    min-width: 60px;
  }

  .stock-name {
    color: rgba(255, 255, 255, 0.9);
    min-width: 80px;
  }

  .warning-reason {
    color: #ff4466;
    min-width: 100px;
  }

  .warning-time {
    color: rgba(255, 255, 255, 0.5);
    font-size: 11px;
  }
}
</style>