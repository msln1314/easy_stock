<template>
  <div class="market-overview-panel">
    <!-- 涨跌比 + 板块资金 + 策略数 + 因子数 + 市场情绪 -->
    <div class="stats-row">
      <div class="stat-item limit-ratio">
        <div class="limit-values">
          <span class="limit-up">{{ limitUpCount }}</span>
          <span class="limit-sep">/</span>
          <span class="limit-down">{{ limitDownCount }}</span>
        </div>
        <div class="stat-label">涨停/跌停</div>
      </div>
      <div class="stat-item sector-funds">
        <div class="sector-list">
          <div class="sector-item" v-for="sector in topSectors" :key="sector.name">
            <span class="sector-name">{{ sector.name }}</span>
            <span class="sector-amount" :class="sector.amount >= 0 ? 'rise' : 'fall'">
              {{ formatSectorAmount(sector.amount) }}
            </span>
          </div>
        </div>
        <div class="stat-label">板块资金TOP5</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ strategyCount }}</div>
        <div class="stat-label">策略数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ factorCount }}</div>
        <div class="stat-label">因子数</div>
      </div>
      <div class="stat-item market-sentiment">
        <div class="sentiment-value" :class="marketSentimentClass">{{ marketSentimentText }}</div>
        <div class="stat-label">市场情绪</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 统计数据
const strategyCount = ref(12)
const factorCount = ref(45)
const marketSentiment = ref<'bullish' | 'bearish' | 'neutral'>('bullish')
const marketSentimentText = computed(() => marketSentiment.value === 'bullish' ? '看涨' : marketSentiment.value === 'bearish' ? '看跌' : '中性')
const marketSentimentClass = computed(() => marketSentiment.value)

// 涨停跌停统计
const limitUpCount = ref(0)
const limitDownCount = ref(0)

// 板块资金TOP5
const topSectors = ref<{ name: string; amount: number }[]>([])

// 格式化板块资金
function formatSectorAmount(value: number): string {
  if (!value) return '-'
  const absValue = Math.abs(value)
  const sign = value >= 0 ? '+' : '-'
  if (absValue >= 100000000) {
    return sign + (absValue / 100000000).toFixed(2) + '亿'
  } else if (absValue >= 10000) {
    return sign + (absValue / 10000).toFixed(2) + '万'
  }
  return sign + absValue.toFixed(0)
}

// 加载市场数据
async function loadMarketData() {
  try {
    const response = await fetch('/api/v1/position/market-stats')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        limitUpCount.value = result.data.limit_up_count || 0
        limitDownCount.value = result.data.limit_down_count || 0
        topSectors.value = result.data.top_sectors || []
        strategyCount.value = result.data.strategy_count || 12
        factorCount.value = result.data.factor_count || 45
      }
    }
  } catch (e) {
    console.error('加载市场数据失败', e)
    // 模拟数据
    limitUpCount.value = 45
    limitDownCount.value = 12
    topSectors.value = [
      { name: '半导体', amount: 156000000 },
      { name: '新能源', amount: 89000000 },
      { name: '医药', amount: 45000000 },
      { name: '白酒', amount: -23000000 },
      { name: '地产', amount: -56000000 }
    ]
  }
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadMarketData()
  dataTimer = window.setInterval(() => {
    loadMarketData()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(dataTimer)
})

defineExpose({
  loadData: loadMarketData
})
</script>

<style scoped lang="scss">
.market-overview-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.stats-row {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 10px;

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #00ffcc;
    }

    .stat-label {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
      margin-top: 4px;
    }
  }

  .limit-ratio {
    min-width: 70px;

    .limit-values {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      font-size: 20px;
      font-weight: 600;

      .limit-up {
        color: #ff4466;
      }

      .limit-down {
        color: #00ff88;
      }

      .limit-sep {
        color: rgba(255, 255, 255, 0.5);
        margin: 0 2px;
      }
    }
  }

  .sector-funds {
    min-width: 350px;

    .sector-list {
      display: flex;
      align-items: center;
      justify-content: space-around;
      gap: 8px;
      height: 32px;

      .sector-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 10px;

        .sector-name {
          color: rgba(255, 255, 255, 0.8);
          margin-bottom: 2px;
        }

        .sector-amount {
          font-weight: 500;
          font-size: 11px;
        }
      }
    }
  }

  .market-sentiment {
    .sentiment-value {
      font-size: 18px;
      font-weight: 600;

      &.bullish { color: #ff4466; }
      &.bearish { color: #00ff88; }
      &.neutral { color: #ffaa00; }
    }
  }
}

// 涨跌颜色
.rise { color: #ff4466; }
.fall { color: #00ff88; }
</style>