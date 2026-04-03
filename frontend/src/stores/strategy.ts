/**
 * 策略列表状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { StrategyListItem, StrategyStats, StrategyQueryParams } from '@/types/strategy'
import { getStrategies, getStrategyStats, deleteStrategy, updateStrategyStatus } from '@/api/strategy'

export const useStrategyStore = defineStore('strategy', () => {
  // 状态
  const strategies = ref<StrategyListItem[]>([])
  const stats = ref<StrategyStats>({
    total: 0,
    by_execute_mode: { auto: 0, alert: 0, simulate: 0 },
    by_status: { running: 0, paused: 0, stopped: 0 }
  })
  const loading = ref(false)
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(10)

  // 筛选条件
  const filters = ref<StrategyQueryParams>({
    execute_mode: undefined,
    status: undefined,
    keyword: undefined
  })

  // 计算属性
  const hasMore = computed(() => strategies.value.length < total.value)

  // 加载策略列表
  async function loadStrategies() {
    loading.value = true
    try {
      const result = await getStrategies({
        ...filters.value,
        page: page.value,
        page_size: pageSize.value
      })
      strategies.value = result.items
      total.value = result.total
    } finally {
      loading.value = false
    }
  }

  // 加载统计信息
  async function loadStats() {
    try {
      stats.value = await getStrategyStats()
    } catch (error) {
      console.error('加载统计失败:', error)
    }
  }

  // 删除策略
  async function removeStrategy(id: number) {
    await deleteStrategy(id)
    await loadStrategies()
    await loadStats()
  }

  // 更新状态
  async function changeStatus(id: number, status: string) {
    await updateStrategyStatus(id, status)
    await loadStrategies()
    await loadStats()
  }

  // 设置筛选条件
  function setFilters(newFilters: StrategyQueryParams) {
    filters.value = { ...newFilters }
    page.value = 1
    loadStrategies()
  }

  // 清除筛选
  function clearFilters() {
    filters.value = {
      execute_mode: undefined,
      status: undefined,
      keyword: undefined
    }
    page.value = 1
    loadStrategies()
  }

  // 分页
  function setPage(newPage: number) {
    page.value = newPage
    loadStrategies()
  }

  // 初始化
  function init() {
    loadStrategies()
    loadStats()
  }

  return {
    strategies,
    stats,
    loading,
    total,
    page,
    pageSize,
    filters,
    hasMore,
    loadStrategies,
    loadStats,
    removeStrategy,
    changeStatus,
    setFilters,
    clearFilters,
    setPage,
    init
  }
})