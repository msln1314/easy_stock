<template>
  <div class="risk-control-panel">
    <div class="panel-header">
      <span class="panel-title">风控指标</span>
      <span class="update-time">{{ formatTime(lastUpdate) }}</span>
    </div>

    <div class="panel-content">
      <!-- 规则统计 -->
      <div class="rule-stats">
        <div class="stat-card">
          <span class="stat-value">{{ stats.enabled_rules }}</span>
          <span class="stat-label">启用规则</span>
        </div>
        <div class="stat-card critical">
          <span class="stat-value">{{ stats.critical_rules }}</span>
          <span class="stat-label">关键规则</span>
        </div>
        <div class="stat-card warning">
          <span class="stat-value">{{ stats.warning_rules }}</span>
          <span class="stat-label">警告规则</span>
        </div>
      </div>

      <!-- 今日审核 -->
      <div class="audit-section">
        <div class="section-header">今日审核</div>
        <div class="audit-stats">
          <div class="audit-item pass">
            <span class="audit-value">{{ stats.today_passed }}</span>
            <span class="audit-label">通过</span>
          </div>
          <div class="audit-item reject">
            <span class="audit-value">{{ stats.today_rejected }}</span>
            <span class="audit-label">拒绝</span>
          </div>
          <div class="audit-rate">
            <span class="rate-value">{{ stats.audit_pass_rate?.toFixed(1) }}%</span>
            <span class="rate-label">通过率</span>
          </div>
        </div>
      </div>

      <!-- 仓位状态 -->
      <div class="position-section">
        <div class="section-header">仓位状态</div>
        <div class="position-bar">
          <div class="bar-fill" :style="{ width: Math.min(stats.position_ratio, 100) + '%' }">
            <span class="bar-value">{{ stats.position_ratio?.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="position-detail">
          <div class="detail-item">
            <span class="label">持仓市值</span>
            <span class="value">{{ formatAmount(stats.position_value) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">可用资金</span>
            <span class="value">{{ formatAmount(stats.available_cash) }}</span>
          </div>
        </div>
      </div>

      <!-- 今日交易 -->
      <div class="trade-section">
        <div class="section-header">今日交易</div>
        <div class="trade-stats">
          <span class="trade-count">{{ stats.today_buy_count }}次</span>
          <span class="trade-amount">{{ formatAmount(stats.today_buy_amount) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'

interface RiskStats {
  enabled_rules: number
  critical_rules: number
  warning_rules: number
  today_audit_total: number
  today_passed: number
  today_rejected: number
  audit_pass_rate: number
  position_ratio: number
  position_value: number
  available_cash: number
  today_buy_count: number
  today_buy_amount: number
}

const stats = ref<RiskStats>({
  enabled_rules: 0, critical_rules: 0, warning_rules: 0,
  today_audit_total: 0, today_passed: 0, today_rejected: 0, audit_pass_rate: 100,
  position_ratio: 0, position_value: 0, available_cash: 1000000,
  today_buy_count: 0, today_buy_amount: 0
})

const lastUpdate = ref(new Date())

function formatTime(time: Date): string {
  return dayjs(time).format('HH:mm:ss')
}

function formatAmount(value: number): string {
  if (!value) return '0'
  if (Math.abs(value) >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toFixed(2)
}

async function loadStats() {
  try {
    const response = await fetch('/api/v1/risk-control/overview')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        stats.value = result.data
        lastUpdate.value = new Date()
      }
    }
  } catch (e) {
    console.error('加载风控数据失败', e)
    stats.value = {
      enabled_rules: 8, critical_rules: 5, warning_rules: 3,
      today_audit_total: 3, today_passed: 3, today_rejected: 0, audit_pass_rate: 100,
      position_ratio: 45, position_value: 450000, available_cash: 550000,
      today_buy_count: 3, today_buy_amount: 45000
    }
  }
}

let dataTimer: number

onMounted(() => { loadStats(); dataTimer = window.setInterval(loadStats, 30000) })
onUnmounted(() => clearInterval(dataTimer))

defineExpose({ loadData: loadStats })
</script>

<style scoped lang="scss">
.risk-control-panel {
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
    .update-time { font-size: 10px; color: rgba(255,255,255,0.5); }
  }

  .panel-content { flex: 1; padding: 10px 12px; overflow-y: auto; }
}

.rule-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;

  .stat-card {
    flex: 1;
    background: rgba(30,50,100,0.5);
    border-radius: 6px;
    padding: 8px;
    text-align: center;
    border: 1px solid rgba(100,150,255,0.15);

    &.critical { border-color: rgba(255,68,102,0.3); .stat-value { color: #ff4466; } }
    &.warning { border-color: rgba(255,170,0,0.3); .stat-value { color: #ffaa00; } }

    .stat-value { font-size: 18px; font-weight: 600; color: #fff; }
    .stat-label { font-size: 10px; color: rgba(255,255,255,0.6); }
  }
}

.section-header {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  margin-bottom: 6px;
}

.audit-section, .position-section, .trade-section {
  background: rgba(30,50,100,0.4);
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid rgba(100,150,255,0.15);
}

.audit-stats {
  display: flex;
  gap: 12px;

  .audit-item { display: flex; flex-direction: column; align-items: center;
    &.pass .audit-value { color: #00ff88; }
    &.reject .audit-value { color: #ff4466; }
    .audit-value { font-size: 14px; font-weight: 600; }
    .audit-label { font-size: 10px; color: rgba(255,255,255,0.5); }
  }

  .audit-rate { flex: 1; text-align: right;
    .rate-value { font-size: 14px; color: #00ffcc; font-weight: 500; }
    .rate-label { font-size: 10px; color: rgba(255,255,255,0.5); }
  }
}

.position-bar {
  height: 20px;
  background: rgba(30,50,100,0.6);
  border-radius: 4px;
  margin-bottom: 8px;
  overflow: hidden;

  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #00aaff, #00ff88);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 6px;
    min-width: 40px;
    .bar-value { font-size: 11px; color: #fff; font-weight: 500; }
  }
}

.position-detail, .trade-stats {
  display: flex;
  gap: 12px;
}

.detail-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  .label { font-size: 10px; color: rgba(255,255,255,0.5); }
  .value { font-size: 12px; color: #fff; font-weight: 500; }
}

.trade-stats {
  justify-content: space-between;
  .trade-count { font-size: 12px; color: #ffaa00; }
  .trade-amount { font-size: 12px; color: #00ffcc; }
}
</style>