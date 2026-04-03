<template>
  <div class="system-monitor-panel">
    <div class="monitor-grid">
      <div class="monitor-item" v-for="item in monitorItems" :key="item.key">
        <div class="monitor-ring">
          <v-chart :option="item.chartOption" style="height: 80px; width: 80px" />
        </div>
        <div class="monitor-info">
          <div class="monitor-name">{{ item.name }}</div>
          <div class="monitor-status" :class="item.statusClass">
            <span class="status-dot"></span>
            {{ item.statusText }}
          </div>
          <div class="monitor-value" v-if="item.value">{{ item.value }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'

use([CanvasRenderer, PieChart])

interface SystemStatus {
  api_status?: string
  data_sync_status?: string
  uptime?: number
  cpu_usage?: number
  memory_usage?: number
  last_update?: string
}

const props = defineProps<{
  data: SystemStatus
}>()

interface MonitorItem {
  key: string
  name: string
  status: string
  statusClass: string
  statusText: string
  value?: string
  chartOption: any
}

function createRingOption(value: number, color: string) {
  return {
    series: [{
      type: 'pie',
      radius: ['70%', '90%'],
      center: ['50%', '50%'],
      silent: true,
      data: [
        { value: value, name: 'used', itemStyle: { color: color } },
        { value: 100 - value, name: 'unused', itemStyle: { color: 'rgba(100, 150, 255, 0.1)' } }
      ],
      label: { show: false }
    }]
  }
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    HEALTHY: 'healthy',
    WARNING: 'warning',
    ERROR: 'error'
  }
  return map[status] || 'healthy'
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    HEALTHY: '健康',
    WARNING: '警告',
    ERROR: '异常'
  }
  return map[status] || '健康'
}

function formatUptime(seconds: number): string {
  if (!seconds) return '-'
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  if (days > 0) return `${days}天${hours}时`
  return `${hours}小时`
}

const monitorItems = computed<MonitorItem[]>(() => {
  const data = props.data
  return [
    {
      key: 'api',
      name: 'API状态',
      status: data.api_status || 'HEALTHY',
      statusClass: getStatusClass(data.api_status || 'HEALTHY'),
      statusText: getStatusText(data.api_status || 'HEALTHY'),
      chartOption: createRingOption(100, getStatusClass(data.api_status) === 'healthy' ? '#00ff00' : '#ffaa00')
    },
    {
      key: 'sync',
      name: '数据同步',
      status: data.data_sync_status || 'HEALTHY',
      statusClass: getStatusClass(data.data_sync_status || 'HEALTHY'),
      statusText: getStatusText(data.data_sync_status || 'HEALTHY'),
      chartOption: createRingOption(100, getStatusClass(data.data_sync_status) === 'healthy' ? '#00ff00' : '#ffaa00')
    },
    {
      key: 'cpu',
      name: 'CPU',
      status: data.cpu_usage > 80 ? 'WARNING' : 'HEALTHY',
      statusClass: data.cpu_usage > 80 ? 'warning' : 'healthy',
      statusText: data.cpu_usage > 80 ? '偏高' : '正常',
      value: `${data.cpu_usage?.toFixed(1) || '-'}%`,
      chartOption: createRingOption(data.cpu_usage || 0, data.cpu_usage > 80 ? '#ffaa00' : '#00aaff')
    },
    {
      key: 'memory',
      name: '内存',
      status: data.memory_usage > 80 ? 'WARNING' : 'HEALTHY',
      statusClass: data.memory_usage > 80 ? 'warning' : 'healthy',
      statusText: data.memory_usage > 80 ? '偏高' : '正常',
      value: `${data.memory_usage?.toFixed(1) || '-'}%`,
      chartOption: createRingOption(data.memory_usage || 0, data.memory_usage > 80 ? '#ffaa00' : '#00aaff')
    },
    {
      key: 'uptime',
      name: '运行时间',
      status: 'HEALTHY',
      statusClass: 'healthy',
      statusText: '稳定运行',
      value: formatUptime(data.uptime || 0),
      chartOption: createRingOption(100, '#00aaff')
    }
  ]
})
</script>

<style scoped lang="scss">
.system-monitor-panel {
  height: 100%;
  padding: 10px;
}

.monitor-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: space-around;
}

.monitor-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(0, 50, 100, 0.3);
  border-radius: 8px;
  min-width: 120px;

  .monitor-info {
    .monitor-name {
      color: #fff;
      font-size: 14px;
      margin-bottom: 5px;
    }

    .monitor-status {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
      }

      &.healthy .status-dot { background: #00ff00; }
      &.warning .status-dot { background: #ffaa00; }
      &.error .status-dot { background: #ff4466; }

      &.healthy { color: #00ff00; }
      &.warning { color: #ffaa00; }
      &.error { color: #ff4466; }
    }

    .monitor-value {
      color: #00aaff;
      font-size: 12px;
      margin-top: 3px;
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>