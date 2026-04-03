<template>
  <div class="alert-list">
    <n-list bordered>
      <n-list-item v-for="alert in alerts" :key="alert.id">
        <n-thing :title="alert.title" :description="alert.content">
          <template #header-extra>
            <n-button v-if="!alert.is_resolved" size="small" type="primary" @click="$emit('resolve', alert.id)">
              处理
            </n-button>
            <n-tag v-else type="success" size="small">已处理</n-tag>
          </template>
          <template #footer>
            <div class="alert-meta">
              <n-tag :type="getAlertType(alert.alert_level)" size="small">{{ alert.alert_level }}</n-tag>
              <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
            </div>
          </template>
        </n-thing>
      </n-list-item>
    </n-list>
  </div>
</template>

<script setup lang="ts">
import { NList, NListItem, NThing, NButton, NTag } from 'naive-ui'
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

defineEmits<{
  resolve: [id: number]
}>()

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
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped lang="scss">
.alert-list {
  :deep(.n-list) {
    background: transparent;
  }

  .alert-meta {
    display: flex;
    gap: 10px;
    align-items: center;

    .alert-time {
      color: rgba(255, 255, 255, 0.6);
      font-size: 12px;
    }
  }
}
</style>