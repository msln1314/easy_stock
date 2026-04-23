<template>
  <div class="fund-flow-panel">
    <div class="panel-header">
      <span class="panel-title">资金流向</span>
      <span class="flow-date">{{ todayDate }}</span>
    </div>

    <div class="panel-content">
      <!-- 今日资金流向 -->
      <div class="flow-overview">
        <div class="flow-item main">
          <div class="flow-label">主力资金</div>
          <div class="flow-value" :class="getFlowClass(stats.today_flow?.main_net)">
            {{ formatFlow(stats.today_flow?.main_net) }}
          </div>
        </div>
        <div class="flow-item retail">
          <div class="flow-label">散户资金</div>
          <div class="flow-value" :class="getFlowClass(stats.today_flow?.retail_net)">
            {{ formatFlow(stats.today_flow?.retail_net) }}
          </div>
        </div>
      </div>

      <!-- 板块流向 -->
      <div class="sector-section">
        <div class="section-header">板块资金TOP5</div>
        <div class="sector-list">
          <div v-for="item in stats.sector_flow?.slice(0,5)" :key="item.sector" class="sector-item">
            <span class="sector-name">{{ item.sector }}</span>
            <span class="sector-flow" :class="getFlowClass(item.net_flow)">
              {{ formatFlow(item.net_flow) }}
            </span>
            <span class="sector-change" :class="getChangeClass(item.change_pct)">
              {{ item.change_pct > 0 ? '+' : '' }}{{ item.change_pct }}%
            </span>
          </div>
        </div>
      </div>

      <!-- 个股流入 -->
      <div class="stock-section">
        <div class="section-header">流入TOP3</div>
        <div class="stock-list">
          <div v-for="item in stats.stock_flow_top5?.slice(0,3)" :key="item.stock_code" class="stock-item inflow">
            <span class="stock-code">{{ item.stock_code }}</span>
            <span class="stock-name">{{ item.stock_name }}</span>
            <span class="stock-flow">{{ formatFlow(item.net_flow) }}</span>
          </div>
        </div>
      </div>

      <!-- 个股流出 -->
      <div class="stock-section outflow">
        <div class="section-header">流出TOP3</div>
        <div class="stock-list">
          <div v-for="item in stats.stock_flow_bottom5?.slice(0,3)" :key="item.stock_code" class="stock-item outflow">
            <span class="stock-code">{{ item.stock_code }}</span>
            <span class="stock-name">{{ item.stock_name }}</span>
            <span class="stock-flow">{{ formatFlow(item.net_flow) }}</span>
          </div>
        </div>
      </div>

      <!-- 大单统计 -->
      <div class="large-order-section">
        <div class="section-header">大单统计</div>
        <div class="order-stats">
          <div class="order-item">
            <span class="order-label">大单买入</span>
            <span class="order-value buy">{{ stats.large_order?.buy_count }}笔</span>
          </div>
          <div class="order-item">
            <span class="order-label">大单卖出</span>
            <span class="order-value sell">{{ stats.large_order?.sell_count }}笔</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface FundFlowStats {
  today_flow: { main_net: number; retail_net: number }
  sector_flow: any[]
  stock_flow_top5: any[]
  stock_flow_bottom5: any[]
  large_order: { buy_count: number; sell_count: number }
}

const todayDate = ref(dayjs().format('YYYY-MM-DD'))
const stats = ref<FundFlowStats>({
  today_flow: { main_net: 0, retail_net: 0 },
  sector_flow: [],
  stock_flow_top5: [],
  stock_flow_bottom5: [],
  large_order: { buy_count: 0, sell_count: 0 }
})

function formatFlow(value: number): string {
  if (!value) return '0'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(0)}万`
}

function getFlowClass(value: number): string {
  if (!value) return ''
  return value > 0 ? 'inflow' : 'outflow'
}

function getChangeClass(value: number): string {
  if (!value) return ''
  return value > 0 ? 'rise' : 'fall'
}

async function loadStats() {
  try {
    const response = await fetch('/api/v1/fund-flow/overview')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
      }
    }
  } catch (e) {
    console.error('加载资金流向失败', e)
    stats.value = {
      today_flow: { main_net: 3700, retail_net: -1700 },
      sector_flow: [
        { sector: '科技', net_flow: 2800, change_pct: 1.5 },
        { sector: '医药', net_flow: 1500, change_pct: 0.8 },
        { sector: '消费', net_flow: 1200, change_pct: 0.6 },
        { sector: '金融', net_flow: -800, change_pct: -0.5 },
        { sector: '地产', net_flow: -1500, change_pct: -1.2 },
      ],
      stock_flow_top5: [
        { stock_code: '000001', stock_name: '平安银行', net_flow: 850 },
        { stock_code: '600036', stock_name: '招商银行', net_flow: 720 },
        { stock_code: '000333', stock_name: '美的集团', net_flow: 560 },
      ],
      stock_flow_bottom5: [
        { stock_code: '600519', stock_name: '贵州茅台', net_flow: -420 },
        { stock_code: '601318', stock_name: '中国平安', net_flow: -380 },
        { stock_code: '000002', stock_name: '万科A', net_flow: -320 },
      ],
      large_order: { buy_count: 125, sell_count: 88 }
    }
  }
}

let dataTimer: number

onMounted(() => { loadStats(); dataTimer = window.setInterval(loadStats, 30000) })
onUnmounted(() => clearInterval(dataTimer))

defineExpose({ loadData: loadStats })
</script>

<style scoped lang="scss">
.fund-flow-panel {
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
    .flow-date { font-size: 11px; color: rgba(255,255,255,0.6); }
  }

  .panel-content { flex: 1; padding: 10px 12px; overflow-y: auto; }
}

.flow-overview {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;

  .flow-item {
    flex: 1;
    background: rgba(30,50,100,0.5);
    border-radius: 6px;
    padding: 8px;
    text-align: center;
    border: 1px solid rgba(100,150,255,0.15);

    .flow-label { font-size: 11px; color: rgba(255,255,255,0.6); }
    .flow-value { font-size: 16px; font-weight: 600;
      &.inflow { color: #ff4466; }
      &.outflow { color: #00ff88; }
    }
  }
}

.section-header {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 6px;
}

.sector-section, .stock-section, .large-order-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);
}

.sector-item, .stock-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;

  .sector-name, .stock-code { font-size: 12px; color: #00aaff; }
  .stock-name { font-size: 11px; color: rgba(255,255,255,0.8); }
  .sector-flow, .stock-flow { font-size: 12px; font-weight: 500;
    &.inflow { color: #ff4466; }
    &.outflow { color: #00ff88; }
  }
  .sector-change { font-size: 10px;
    &.rise { color: #ff4466; }
    &.fall { color: #00ff88; }
  }
}

.order-stats {
  display: flex;
  gap: 12px;
  .order-item { display: flex; align-items: center; gap: 6px;
    .order-label { font-size: 10px; color: rgba(255,255,255,0.5); }
    .order-value { font-size: 12px; font-weight: 500;
      &.buy { color: #ff4466; }
      &.sell { color: #00ff88; }
    }
  }
}
</style>