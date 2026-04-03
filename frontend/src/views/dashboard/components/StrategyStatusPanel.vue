<template>
  <div class="strategy-status-panel">
    <div class="strategy-list">
      <div class="strategy-card" v-for="strategy in data" :key="strategy.id">
        <div class="strategy-header">
          <span class="strategy-name">{{ strategy.strategy_name }}</span>
          <n-tag :type="getStatusType(strategy.execution_status)" size="small" bordered>
            {{ getStatusText(strategy.execution_status) }}
          </n-tag>
        </div>
        <div class="strategy-info">
          <div class="info-item">
            <span class="info-label">股票:</span>
            <span class="info-value">{{ strategy.stock_code }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">信号:</span>
            <n-tag :type="getSignalType(strategy.signal_type)" size="small" bordered>
              {{ strategy.signal_type }}
            </n-tag>
          </div>
          <div class="info-item">
            <span class="info-label">持仓:</span>
            <span class="info-value">{{ strategy.position_size }}股</span>
          </div>
          <div class="info-item">
            <span class="info-label">时间:</span>
            <span class="info-value">{{ formatTime(strategy.executed_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NTag } from 'naive-ui'
import dayjs from 'dayjs'

interface StrategyExecution {
  id: number
  strategy_name: string
  stock_code: string
  signal_type: string
  execution_status: string
  position_size: number
  executed_at: string
}

const props = defineProps<{
  data: StrategyExecution[]
}>()

function getStatusType(status: string): 'success' | 'warning' | 'error' | 'default' {
  const map: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    EXECUTED: 'success',
    PENDING: 'warning',
    FAILED: 'error',
    HOLD: 'default'
  }
  return map[status] || 'default'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    EXECUTED: '已执行',
    PENDING: '待执行',
    FAILED: '失败',
    HOLD: '持有'
  }
  return map[status] || status
}

function getSignalType(signal: string): 'success' | 'error' | 'default' {
  const map: Record<string, 'success' | 'error' | 'default'> = {
    BUY: 'success',
    SELL: 'error',
    HOLD: 'default'
  }
  return map[signal] || 'default'
}

function formatTime(time: string): string {
  if (!time) return '-'
  return dayjs(time).format('MM-DD HH:mm')
}
</script>

<style scoped lang="scss">
.strategy-status-panel {
  height: 100%;
  overflow: auto;
}

.strategy-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.strategy-card {
  background: rgba(0, 50, 100, 0.3);
  border: 1px solid rgba(100, 150, 255, 0.2);
  border-radius: 6px;
  padding: 12px;
  width: calc(50% - 5px);

  .strategy-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;

    .strategy-name {
      color: #fff;
      font-weight: 500;
      font-size: 14px;
    }
  }

  .strategy-info {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .info-item {
      display: flex;
      gap: 4px;
      align-items: center;

      .info-label {
        color: rgba(255, 255, 255, 0.5);
        font-size: 12px;
      }

      .info-value {
        color: #fff;
        font-size: 12px;
      }
    }
  }
}
</style>