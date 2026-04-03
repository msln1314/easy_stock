<template>
  <div class="strategy-card">
    <!-- 头部 -->
    <div class="card-header flex-between mb-3">
      <div class="title-area">
        <h3 class="strategy-name text-base font-medium">{{ strategy.name }}</h3>
        <p v-if="strategy.description" class="strategy-desc text-sm text-gray-500 mt-1">
          {{ strategy.description }}
        </p>
      </div>
      <div class="tags flex gap-2">
        <n-tag :type="statusType" size="small">{{ statusText }}</n-tag>
        <n-tag :type="modeType" size="small">{{ modeText }}</n-tag>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions flex gap-2 mt-3">
      <n-button size="small" @click="$emit('edit', strategy.id)">
        <template #icon>
          <n-icon><CreateOutline /></n-icon>
        </template>
        编辑
      </n-button>
      <n-button
        size="small"
        :type="strategy.status === 'running' ? 'warning' : 'success'"
        @click="$emit('toggle-status', strategy.id, strategy.status)"
      >
        {{ strategy.status === 'running' ? '暂停' : '启动' }}
      </n-button>
      <n-button size="small" type="error" @click="$emit('delete', strategy.id)">
        <template #icon>
          <n-icon><TrashOutline /></n-icon>
        </template>
        删除
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NTag, NButton, NIcon } from 'naive-ui'
import { CreateOutline, TrashOutline } from '@vicons/ionicons5'
import type { StrategyListItem } from '@/types/strategy'

const props = defineProps<{
  strategy: StrategyListItem
}>()

defineEmits<{
  edit: [id: number]
  delete: [id: number]
  toggleStatus: [id: number, currentStatus: string]
}>()

const statusType = computed(() => {
  const typeMap: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
    running: 'success',
    paused: 'warning',
    stopped: 'error'
  }
  return typeMap[props.strategy.status] || 'default'
})

const statusText = computed(() => {
  const textMap: Record<string, string> = {
    running: '运行中',
    paused: '已暂停',
    stopped: '已停止'
  }
  return textMap[props.strategy.status] || props.strategy.status
})

const modeType = computed(() => {
  const typeMap: Record<string, 'info' | 'default'> = {
    auto: 'info',
    alert: 'default',
    simulate: 'default'
  }
  return typeMap[props.strategy.execute_mode] || 'default'
})

const modeText = computed(() => {
  const textMap: Record<string, string> = {
    auto: '自动',
    alert: '提醒',
    simulate: '模拟'
  }
  return textMap[props.strategy.execute_mode] || props.strategy.execute_mode
})
</script>

<style scoped lang="scss">
.strategy-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;

  &:hover {
    border-color: #2080f0;
    box-shadow: 0 4px 12px rgba(32, 128, 240, 0.1);
  }

  .strategy-name {
    color: #1f2937;
  }

  .strategy-desc {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .card-actions {
    border-top: 1px solid #f3f4f6;
    padding-top: 12px;
  }
}
</style>