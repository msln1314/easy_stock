<template>
  <div class="strategy-filter">
    <!-- 全部策略 -->
    <div class="filter-section">
      <div
        class="filter-item all"
        :class="{ active: !activeFilter }"
        @click="handleFilterAll"
      >
        <span class="label">全部策略</span>
        <span class="count">{{ store.stats.total }}</span>
      </div>
    </div>

    <!-- 执行模式 -->
    <div class="filter-section mt-4">
      <div class="section-title mb-2">执行模式</div>
      <div
        v-for="mode in modeFilters"
        :key="mode.value"
        class="filter-item"
        :class="{ active: activeFilter?.type === 'mode' && activeFilter?.value === mode.value }"
        @click="handleFilter('mode', mode.value)"
      >
        <span class="label">{{ mode.label }}</span>
        <span class="count">{{ store.stats.by_execute_mode[mode.value] || 0 }}</span>
      </div>
    </div>

    <!-- 运行状态 -->
    <div class="filter-section mt-4">
      <div class="section-title mb-2">运行状态</div>
      <div
        v-for="status in statusFilters"
        :key="status.value"
        class="filter-item"
        :class="{ active: activeFilter?.type === 'status' && activeFilter?.value === status.value }"
        @click="handleFilter('status', status.value)"
      >
        <span class="label">{{ status.label }}</span>
        <span class="count">{{ store.stats.by_status[status.value] || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useStrategyStore } from '@/stores/strategy'

const store = useStrategyStore()

interface Filter {
  type: 'mode' | 'status'
  value: string
}

const activeFilter = ref<Filter | null>(null)

const modeFilters = [
  { label: '自动交易', value: 'auto' },
  { label: '信号提醒', value: 'alert' },
  { label: '模拟运行', value: 'simulate' }
]

const statusFilters = [
  { label: '运行中', value: 'running' },
  { label: '已暂停', value: 'paused' },
  { label: '已停止', value: 'stopped' }
]

function handleFilterAll() {
  activeFilter.value = null
  store.clearFilters()
}

function handleFilter(type: 'mode' | 'status', value: string) {
  activeFilter.value = { type, value }
  if (type === 'mode') {
    store.setFilters({ execute_mode: value })
  } else {
    store.setFilters({ status: value })
  }
}
</script>

<style scoped lang="scss">
.strategy-filter {
  .section-title {
    font-size: 12px;
    color: #6b7280;
    font-weight: 500;
  }

  .filter-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 4px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #f3f4f6;
    }

    &.active {
      background: #e8f4ff;
      color: #2080f0;
    }

    .label {
      font-size: 14px;
    }

    .count {
      font-size: 12px;
      background: #f3f4f6;
      padding: 2px 8px;
      border-radius: 10px;
    }
  }

  .filter-item.all.active .count {
    background: #2080f0;
    color: #fff;
  }
}
</style>