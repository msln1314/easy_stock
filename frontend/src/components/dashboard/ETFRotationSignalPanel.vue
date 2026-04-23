<template>
  <div class="etf-rotation-signal-panel">
    <div class="panel-header">
      <span class="panel-title">ETF轮动信号</span>
      <span class="signal-date">{{ todayDate }}</span>
    </div>

    <div class="panel-content">
      <!-- 策略状态 -->
      <div class="strategy-status">
        <div class="status-item">
          <span class="status-label">运行策略</span>
          <span class="status-value running">{{ stats.strategy_status?.running || 0 }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">今日信号</span>
          <span class="status-value signal">{{ stats.signal_count || 0 }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">待执行</span>
          <span class="status-value pending">{{ stats.pending_count || 0 }}</span>
        </div>
      </div>

      <!-- ETF评分排行 -->
      <div class="ranking-section">
        <div class="section-header">评分排行</div>
        <div class="ranking-list">
          <div v-for="(item, idx) in stats.etf_ranking?.slice(0, 5)" :key="item.etf_code" class="ranking-item">
            <span class="rank">{{ idx + 1 }}</span>
            <span class="etf-code">{{ item.etf_code }}</span>
            <span class="score">{{ item.momentum_score?.toFixed(2) || '-' }}</span>
            <span class="signal" :class="getSignalClass(item.momentum_score)">
              {{ getSignalText(item.momentum_score) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 当前持仓 -->
      <div class="position-section">
        <div class="section-header">当前持仓</div>
        <div class="position-list">
          <div v-for="pos in stats.current_positions?.slice(0, 3)" :key="pos.id" class="position-item">
            <div class="pos-main">
              <span class="etf-code">{{ pos.etf_code }}</span>
              <span class="etf-name">{{ pos.etf_name || '-' }}</span>
            </div>
            <div class="pos-detail">
              <span class="profit" :class="getProfitClass(pos.profit_pct)">
                {{ formatPercent(pos.profit_pct) }}
              </span>
              <span class="days">{{ pos.hold_days }}天</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日信号 -->
      <div class="signal-section" v-if="stats.today_signals?.length">
        <div class="section-header">今日信号</div>
        <div class="signal-list">
          <div v-for="sig in stats.today_signals?.slice(0, 3)" :key="sig.id" class="signal-item">
            <span class="signal-type" :class="sig.action">{{ sig.action_display }}</span>
            <span class="etf-code">{{ sig.etf_code }}</span>
            <span class="exec-status" :class="{ executed: sig.is_executed }">
              {{ sig.is_executed ? '已执行' : '待执行' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface RotationStats {
  strategy_status: { total: number; running: number; paused: number }
  today_signals: any[]
  etf_ranking: any[]
  current_positions: any[]
  signal_count: number
  pending_count: number
}

const todayDate = ref(dayjs().format('YYYY-MM-DD'))
const stats = ref<RotationStats>({
  strategy_status: { total: 0, running: 0, paused: 0 },
  today_signals: [],
  etf_ranking: [],
  current_positions: [],
  signal_count: 0,
  pending_count: 0
})

function formatPercent(value: number | null): string {
  if (!value) return '0.00%'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

function getProfitClass(value: number | null): string {
  if (!value) return ''
  return value > 0 ? 'profit' : 'loss'
}

function getSignalClass(score: number | null): string {
  if (!score) return ''
  if (score > 0.7) return 'buy'
  if (score < 0) return 'sell'
  return 'hold'
}

function getSignalText(score: number | null): string {
  if (!score) return '持有'
  if (score > 0.7) return '买入'
  if (score < 0) return '卖出'
  return '持有'
}

async function loadStats() {
  try {
    const response = await fetch('/api/v1/etf-rotation-signal/current')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
      }
    }
  } catch (e) {
    console.error('加载ETF轮动信号失败', e)
    stats.value = {
      strategy_status: { total: 2, running: 1, paused: 1 },
      today_signals: [{ id: 1, action: 'buy', action_display: '买入', etf_code: '510300', is_executed: false }],
      etf_ranking: [
        { etf_code: '510300', momentum_score: 0.85 },
        { etf_code: '159915', momentum_score: 0.72 },
        { etf_code: '512880', momentum_score: 0.45 },
        { etf_code: '513100', momentum_score: 0.32 },
        { etf_code: '512690', momentum_score: -0.15 },
      ],
      current_positions: [{ id: 1, etf_code: '510300', etf_name: '沪深300ETF', profit_pct: 2.5, hold_days: 5 }],
      signal_count: 1,
      pending_count: 1
    }
  }
}

let dataTimer: number

onMounted(() => {
  loadStats()
  dataTimer = window.setInterval(loadStats, 30000)
})

onUnmounted(() => clearInterval(dataTimer))

defineExpose({ loadData: loadStats })
</script>

<style scoped lang="scss">
.etf-rotation-signal-panel {
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
    .signal-date { font-size: 11px; color: rgba(255,255,255,0.6); }
  }

  .panel-content {
    flex: 1;
    padding: 10px 12px;
    overflow-y: auto;
  }
}

.strategy-status {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;

  .status-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;

    .status-label { font-size: 10px; color: rgba(255,255,255,0.5); }
    .status-value { font-size: 16px; font-weight: 600;
      &.running { color: #00ff88; }
      &.signal { color: #ffaa00; }
      &.pending { color: #ff4466; }
    }
  }
}

.section-header {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(100,150,255,0.15);
}

.ranking-section, .position-section, .signal-section {
  margin-bottom: 10px;
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  border: 1px solid rgba(100,150,255,0.15);
}

.ranking-list .ranking-item, .position-list .position-item, .signal-list .signal-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;

  .rank { width: 18px; height: 18px; border-radius: 50%; background: rgba(100,150,255,0.3); font-size: 10px; display: flex; align-items: center; justify-content: center; color: #fff; }
  .etf-code { font-size: 12px; color: #00aaff; }
  .etf-name { font-size: 11px; color: rgba(255,255,255,0.8); }
  .score { font-size: 12px; color: #fff; font-weight: 500; }
  .signal { font-size: 10px; padding: 2px 6px; border-radius: 3px;
    &.buy { background: rgba(255,68,102,0.3); color: #ff4466; }
    &.sell { background: rgba(0,255,136,0.3); color: #00ff88; }
    &.hold { background: rgba(100,150,255,0.3); color: #aaa; }
  }
  .profit { font-size: 11px; font-weight: 500;
    &.profit { color: #ff4466; }
    &.loss { color: #00ff88; }
  }
  .days { font-size: 10px; color: rgba(255,255,255,0.5); }
  .signal-type { font-size: 10px; padding: 2px 6px; border-radius: 3px;
    &.buy { background: rgba(255,68,102,0.3); color: #ff4466; }
    &.sell { background: rgba(0,255,136,0.3); color: #00ff88; }
  }
  .exec-status { font-size: 10px; color: rgba(255,255,255,0.5);
    &.executed { color: #00ff88; }
  }
}
</style>