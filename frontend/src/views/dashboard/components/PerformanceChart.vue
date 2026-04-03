<template>
  <div class="performance-chart">
    <v-chart ref="chartRef" :option="chartOption" autoresize style="height: 100%; width: 100%" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { VChart, echarts } from '@/utils/echarts'

interface PerformanceData {
  dates: string[]
  values: number[]
}

const props = defineProps<{
  data: PerformanceData
}>()

const chartRef = ref()

const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(20, 40, 80, 0.8)',
    borderColor: 'rgba(100, 150, 255, 0.3)',
    textStyle: { color: '#fff' },
    formatter: (params: any) => {
      const date = params[0].axisValue
      const value = params[0].value
      return `${date}<br/>收益率: <span style="color: #00ff88">${(value * 100).toFixed(2)}%</span>`
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: props.data.dates || [],
    axisLine: { lineStyle: { color: 'rgba(100, 150, 255, 0.3)' } },
    axisLabel: { color: 'rgba(255, 255, 255, 0.6)', fontSize: 10 },
    splitLine: { show: false }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: 'rgba(100, 150, 255, 0.3)' } },
    axisLabel: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: 10,
      formatter: (value: number) => `${(value * 100).toFixed(0)}%`
    },
    splitLine: { lineStyle: { color: 'rgba(100, 150, 255, 0.1)' } }
  },
  series: [
    {
      name: '累计收益率',
      type: 'line',
      data: props.data.values || [],
      smooth: true,
      symbol: 'none',
      lineStyle: {
        color: '#00ff88',
        width: 2
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(0, 255, 136, 0.3)' },
            { offset: 1, color: 'rgba(0, 255, 136, 0.05)' }
          ]
        }
      }
    }
  ]
}))
</script>

<style scoped lang="scss">
.performance-chart {
  height: 100%;
  width: 100%;
}
</style>