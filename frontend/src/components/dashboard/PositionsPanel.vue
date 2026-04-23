<template>
  <div class="positions-panel">
    <div class="panel-header">
      <span class="panel-title">持仓信息</span>
      <div class="panel-info">
        <span class="info-item">总资产: ¥{{ formatMoney(balanceInfo.total_asset) }}</span>
        <span class="info-item">可用: ¥{{ formatMoney(balanceInfo.available_cash) }}</span>
        <span class="info-item">市值: ¥{{ formatMoney(totalMarketValue) }}</span>
      </div>
    </div>
    <div class="panel-content scroll-content">
      <div v-if="positions.length === 0" class="empty-tip">
        <span v-if="qmtStatus === 'error'">QMT服务未连接</span>
        <span v-else>暂无持仓数据</span>
      </div>
      <div v-else class="position-list">
        <div class="position-item" v-for="p in positions" :key="p.code">
          <span class="stock-code">{{ p.code }}</span>
          <span class="stock-name">{{ p.name }}</span>
          <span class="position-size">{{ p.size }}股</span>
          <span class="position-cost">成本: {{ p.cost.toFixed(2) }}</span>
          <span class="position-current">现价: {{ p.current.toFixed(2) }}</span>
          <span class="position-profit" :class="p.profit >= 0 ? 'rise' : 'fall'">
            {{ p.profit >= 0 ? '+' : '' }}{{ p.profit.toFixed(2) }} ({{ p.profitPercent >= 0 ? '+' : '' }}{{ p.profitPercent.toFixed(2) }}%)
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { fetchPositions, fetchBalance } from '@/api/dashboard'

// 持仓信息
const positions = ref<any[]>([])
const balanceInfo = ref({
  total_asset: 0,
  available_cash: 0,
  market_value: 0,
  profit_today: 0,
  profit_total: 0
})

// QMT状态（由父组件传入或自行检测）
const qmtStatus = ref<'healthy' | 'error' | 'warning'>('warning')

const totalMarketValue = computed(() => {
  const total = positions.value.reduce((sum, p) => sum + p.market_value, 0)
  return total
})

// 格式化金额
function formatMoney(value: number): string {
  if (!value) return '0'
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toLocaleString()
}

// 加载持仓和资金数据
async function loadPositionData() {
  try {
    const [posData, balData] = await Promise.all([
      fetchPositions(),
      fetchBalance()
    ])
    positions.value = (posData.positions || []).map((p: any) => ({
      code: p.stock_code,
      name: p.stock_name,
      size: p.quantity,
      cost: p.cost_price,
      current: p.current_price,
      profit: p.profit,
      profitPercent: p.profit_rate,
      market_value: p.market_value
    }))
    balanceInfo.value = balData
    qmtStatus.value = 'healthy'
  } catch (e) {
    console.error('加载持仓数据失败', e)
    const err = e as any
    if (err?.response?.status === 503 || err?.code === 'ERR_NETWORK' || err?.message?.includes('Network Error')) {
      qmtStatus.value = 'error'
    }
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadPositionData()
  dataTimer = window.setInterval(() => {
    loadPositionData()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

// 暴露给父组件
defineExpose({
  qmtStatus,
  loadData: loadPositionData
})
</script>

<style scoped lang="scss">
.positions-panel {
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

    .panel-info {
      display: flex;
      gap: 15px;

      .info-item {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.8);
      }
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

.position-item {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(100, 150, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;

  .stock-code {
    color: #00aaff;
    min-width: 70px;
  }

  .stock-name {
    color: rgba(255, 255, 255, 0.9);
    min-width: 70px;
  }

  .position-size {
    color: rgba(255, 255, 255, 0.7);
    min-width: 70px;
  }

  .position-cost {
    color: rgba(255, 255, 255, 0.6);
    min-width: 80px;
  }

  .position-current {
    color: rgba(255, 255, 255, 0.7);
    min-width: 80px;
  }

  .position-profit {
    min-width: 120px;
    font-weight: 500;
  }
}

.rise { color: #ff4466; }
.fall { color: #00ff88; }
</style>