<template>
  <div class="market-sentiment-panel">
    <div class="panel-header">
      <span class="panel-title">市场情绪</span>
      <span class="sentiment-date">{{ todayDate }}</span>
    </div>

    <div class="panel-content">
      <!-- 涨跌统计 -->
      <div class="rise-fall-section">
        <div class="rise-fall-stats">
          <div class="stat-item rise">
            <span class="stat-value">{{ stats.rise_fall?.rise_count }}</span>
            <span class="stat-label">上涨</span>
          </div>
          <div class="stat-item fall">
            <span class="stat-value">{{ stats.rise_fall?.fall_count }}</span>
            <span class="stat-label">下跌</span>
          </div>
          <div class="stat-item ratio">
            <span class="stat-value">{{ stats.rise_fall?.rise_ratio }}%</span>
            <span class="stat-label">涨跌比</span>
          </div>
        </div>
      </div>

      <!-- 涨停跌停 -->
      <div class="limit-section">
        <div class="limit-item up">
          <span class="limit-value">{{ stats.limit_stats?.limit_up_count }}</span>
          <span class="limit-label">涨停</span>
          <span class="near-value">+{{ stats.limit_stats?.near_limit_up }}近涨停</span>
        </div>
        <div class="limit-item down">
          <span class="limit-value">{{ stats.limit_stats?.limit_down_count }}</span>
          <span class="limit-label">跌停</span>
          <span class="near-value">{{ stats.limit_stats?.near_limit_down }}近跌停</span>
        </div>
      </div>

      <!-- 市场强弱 -->
      <div class="strength-section">
        <div class="strength-header">
          <span class="strength-label">强弱指数</span>
          <span class="strength-value" :class="getStrengthClass(stats.strength_index?.value)">
            {{ stats.strength_index?.value?.toFixed(1) }}
          </span>
        </div>
        <div class="strength-bar">
          <div class="bar-bg">
            <div class="bar-fill" :style="{ width: stats.strength_index?.value + '%' }"></div>
            <span class="bar-level">{{ stats.strength_index?.level }}</span>
          </div>
        </div>
        <div class="strength-trend">
          <span class="trend-label">趋势</span>
          <span class="trend-value" :class="stats.strength_index?.trend === '上升' ? 'up' : 'down'">
            {{ stats.strength_index?.trend }}
          </span>
        </div>
      </div>

      <!-- 北向资金 -->
      <div class="north-flow-section">
        <div class="flow-header">北向资金</div>
        <div class="flow-stats">
          <span class="flow-value" :class="stats.north_flow?.status === '流入' ? 'inflow' : 'outflow'">
            {{ stats.north_flow?.today_flow }}亿
          </span>
          <span class="flow-status">{{ stats.north_flow?.status }}</span>
        </div>
      </div>

      <!-- 热门板块 -->
      <div class="hot-sector-section">
        <div class="section-header">热门板块</div>
        <div class="sector-list">
          <div v-for="sector in stats.hot_sectors?.slice(0, 3)" :key="sector.sector" class="sector-item">
            <span class="sector-name">{{ sector.sector }}</span>
            <span class="sector-heat">{{ sector.heat }}°</span>
            <span class="sector-change" :class="sector.change_avg > 0 ? 'rise' : 'fall'">
              +{{ sector.change_avg }}%
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

interface MarketSentimentStats {
  rise_fall: { rise_count: number; fall_count: number; rise_ratio: number }
  limit_stats: { limit_up_count: number; limit_down_count: number; near_limit_up: number; near_limit_down: number }
  strength_index: { value: number; level: string; trend: string }
  north_flow: { today_flow: number; month_flow: number; status: string }
  hot_sectors: any[]
}

const todayDate = ref(dayjs().format('YYYY-MM-DD'))
const stats = ref<MarketSentimentStats>({
  rise_fall: { rise_count: 0, fall_count: 0, rise_ratio: 0 },
  limit_stats: { limit_up_count: 0, limit_down_count: 0, near_limit_up: 0, near_limit_down: 0 },
  strength_index: { value: 0, level: '', trend: '' },
  north_flow: { today_flow: 0, month_flow: 0, status: '' },
  hot_sectors: []
})

function getStrengthClass(value: number): string {
  if (value >= 70) return 'strong'
  if (value >= 50) return 'neutral'
  return 'weak'
}

async function loadStats() {
  try {
    const response = await fetch('/api/v1/market-sentiment/overview')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
      }
    }
  } catch (e) {
    console.error('加载市场情绪失败', e)
    stats.value = {
      rise_fall: { rise_count: 1856, fall_count: 2342, rise_ratio: 44.2 },
      limit_stats: { limit_up_count: 25, limit_down_count: 8, near_limit_up: 45, near_limit_down: 12 },
      strength_index: { value: 62.5, level: '中性偏强', trend: '上升' },
      north_flow: { today_flow: 28.5, month_flow: 156.8, status: '流入' },
      hot_sectors: [
        { sector: '人工智能', heat: 95, change_avg: 3.5 },
        { sector: '机器人', heat: 88, change_avg: 2.8 },
        { sector: '算力', heat: 82, change_avg: 2.2 },
      ]
    }
  }
}

let dataTimer: number

onMounted(() => { loadStats(); dataTimer = window.setInterval(loadStats, 30000) })
onUnmounted(() => clearInterval(dataTimer))

defineExpose({ loadData: loadStats })
</script>

<style scoped lang="scss">
.market-sentiment-panel {
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
    .sentiment-date { font-size: 11px; color: rgba(255,255,255,0.6); }
  }

  .panel-content { flex: 1; padding: 10px 12px; overflow-y: auto; }
}

.rise-fall-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);

  .rise-fall-stats {
    display: flex;
    gap: 12px;

    .stat-item {
      flex: 1;
      text-align: center;
      .stat-value { font-size: 18px; font-weight: 600;
        &.rise { color: #ff4466; }
        &.fall { color: #00ff88; }
        &.ratio { color: #ffaa00; }
      }
      .stat-label { font-size: 10px; color: rgba(255,255,255,0.6); }
    }
  }
}

.limit-section {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;

  .limit-item {
    flex: 1;
    background: rgba(30,50,100,0.4);
    border-radius: 6px;
    padding: 8px;
    text-align: center;
    border: 1px solid rgba(100,150,255,0.15);

    &.up { border-color: rgba(255,68,102,0.3); .limit-value { color: #ff4466; } }
    &.down { border-color: rgba(0,255,136,0.3); .limit-value { color: #00ff88; } }

    .limit-value { font-size: 20px; font-weight: 600; }
    .limit-label { font-size: 11px; color: rgba(255,255,255,0.7); }
    .near-value { font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 2px; }
  }
}

.strength-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);

  .strength-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    .strength-label { font-size: 11px; color: rgba(255,255,255,0.7); }
    .strength-value { font-size: 16px; font-weight: 600;
      &.strong { color: #ff4466; }
      &.neutral { color: #ffaa00; }
      &.weak { color: #00ff88; }
    }
  }

  .strength-bar {
    .bar-bg {
      height: 20px;
      background: rgba(30,50,100,0.6);
      border-radius: 4px;
      overflow: hidden;
      position: relative;

      .bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #00ff88, #ffaa00, #ff4466);
        border-radius: 4px;
      }

      .bar-level {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 10px;
        color: #fff;
      }
    }
  }

  .strength-trend {
    display: flex;
    justify-content: space-between;
    margin-top: 6px;
    .trend-label { font-size: 10px; color: rgba(255,255,255,0.5); }
    .trend-value { font-size: 12px; font-weight: 500;
      &.up { color: #ff4466; }
      &.down { color: #00ff88; }
    }
  }
}

.north-flow-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);

  .flow-header { font-size: 11px; color: rgba(255,255,255,0.7); margin-bottom: 6px; }
  .flow-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .flow-value { font-size: 18px; font-weight: 600;
      &.inflow { color: #ff4466; }
      &.outflow { color: #00ff88; }
    }
    .flow-status { font-size: 12px; color: rgba(255,255,255,0.7); }
  }
}

.section-header {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 6px;
}

.hot-sector-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  border: 1px solid rgba(100,150,255,0.15);
}

.sector-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;

  .sector-name { font-size: 12px; color: #fff; }
  .sector-heat { font-size: 12px; color: #ff4466; font-weight: 500; }
  .sector-change { font-size: 11px;
    &.rise { color: #ff4466; }
    &.fall { color: #00ff88; }
  }
}
</style>