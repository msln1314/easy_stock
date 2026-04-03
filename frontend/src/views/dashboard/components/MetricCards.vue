<template>
  <div class="metric-cards">
    <div class="metric-card" v-for="(item, key) in metrics" :key="key">
      <div class="metric-icon">
        <n-icon size="24" :component="item.icon" />
      </div>
      <div class="metric-content">
        <div class="metric-value" :class="item.class">
          {{ item.displayValue }}
        </div>
        <div class="metric-label">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { NIcon } from 'naive-ui'
import { TrendingUpOutline, TrophyOutline, TrendingDownOutline, PulseOutline } from '@vicons/ionicons5'

interface PerformanceMetrics {
  total_return?: number
  win_rate?: number
  max_drawdown?: number
  sharpe_ratio?: number
  total_trades?: number
  profit_trades?: number
  loss_trades?: number
}

const props = defineProps<{
  data: PerformanceMetrics
}>()

interface MetricItem {
  label: string
  value: number | undefined
  displayValue: string
  icon: any
  class: string
  format: (v: number) => string
}

const metrics = computed(() => {
  const data = props.data
  return {
    totalReturn: {
      label: '累计收益',
      value: data.total_return,
      displayValue: formatPercent(data.total_return),
      icon: TrendingUpOutline,
      class: data.total_return >= 0 ? 'positive' : 'negative'
    },
    winRate: {
      label: '胜率',
      value: data.win_rate,
      displayValue: formatPercent(data.win_rate),
      icon: TrophyOutline,
      class: 'neutral'
    },
    maxDrawdown: {
      label: '最大回撤',
      value: data.max_drawdown,
      displayValue: formatPercent(data.max_drawdown),
      icon: TrendingDownOutline,
      class: 'negative'
    },
    sharpeRatio: {
      label: '夏普比率',
      value: data.sharpe_ratio,
      displayValue: data.sharpe_ratio?.toFixed(2) || '-',
      icon: PulseOutline,
      class: data.sharpe_ratio >= 1 ? 'positive' : 'neutral'
    }
  }
})

function formatPercent(value: number | undefined): string {
  if (!value) return '-'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${(value * 100).toFixed(2)}%`
}
</script>

<style scoped lang="scss">
.metric-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  height: 100%;
  padding: 10px;
}

.metric-card {
  background: rgba(0, 50, 100, 0.3);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(100, 150, 255, 0.2);

  .metric-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: rgba(0, 170, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #00aaff;
  }

  .metric-content {
    flex: 1;

    .metric-value {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 5px;

      &.positive {
        color: #00ff88;
      }

      &.negative {
        color: #ff4466;
      }

      &.neutral {
        color: #00aaff;
      }
    }

    .metric-label {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.6);
    }
  }
}
</style>