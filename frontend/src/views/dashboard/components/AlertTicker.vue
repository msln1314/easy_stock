<template>
  <div class="alert-ticker">
    <div class="ticker-content" ref="tickerRef">
      <span class="ticker-item" v-for="alert in visibleAlerts" :key="alert.id">
        <n-tag :type="getAlertType(alert.alert_level)" size="small" bordered>
          {{ alert.alert_level }}
        </n-tag>
        <span class="alert-title">{{ alert.title }}</span>
        <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { NTag } from 'naive-ui'
import dayjs from 'dayjs'

interface Alert {
  id: number
  alert_type: string
  alert_level: string
  title: string
  content: string
  is_resolved: boolean
  created_at: string
}

const props = defineProps<{
  alerts: Alert[]
}>()

const tickerRef = ref<HTMLElement>()
let scrollTimer: number

const visibleAlerts = computed(() => {
  return props.alerts.filter(a => !a.is_resolved)
})

function getAlertType(level: string): 'success' | 'warning' | 'error' | 'default' {
  const map: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    INFO: 'default',
    WARNING: 'warning',
    ERROR: 'error',
    CRITICAL: 'error'
  }
  return map[level] || 'default'
}

function formatTime(time: string): string {
  if (!time) return '-'
  return dayjs(time).format('HH:mm')
}

onMounted(() => {
  // 横向滚动动画
  if (tickerRef.value) {
    scrollTimer = window.setInterval(() => {
      if (tickerRef.value) {
        tickerRef.value.scrollLeft += 1
        if (tickerRef.value.scrollLeft >= tickerRef.value.scrollWidth - tickerRef.value.clientWidth) {
          tickerRef.value.scrollLeft = 0
        }
      }
    }, 30)
  }
})

onUnmounted(() => {
  clearInterval(scrollTimer)
})
</script>

<style scoped lang="scss">
.alert-ticker {
  height: 100%;
  padding: 8px 20px;
  display: flex;
  align-items: center;

  .ticker-content {
    display: flex;
    gap: 30px;
    overflow: hidden;
    white-space: nowrap;

    .ticker-item {
      display: flex;
      gap: 10px;
      align-items: center;

      .alert-title {
        color: #fff;
        font-size: 14px;
      }

      .alert-time {
        color: rgba(255, 255, 255, 0.5);
        font-size: 12px;
      }
    }
  }
}
</style>