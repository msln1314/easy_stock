<template>
  <div class="warning-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>卖出预警</h2>
        <n-space>
          <n-button type="primary" @click="loadWarningStocks" :loading="loading">
            <template #icon>
              <n-icon><RefreshOutline /></n-icon>
            </template>
            刷新
          </n-button>
          <n-button type="warning" @click="showConfigModal = true">
            <template #icon>
              <n-icon><SettingsOutline /></n-icon>
            </template>
            预警条件配置
          </n-button>
        </n-space>
      </div>
      <div class="header-right">
        <n-space align="center">
          <n-select
            v-model:value="filterLevel"
            :options="levelOptions"
            placeholder="预警级别"
            clearable
            size="small"
            style="width: 120px"
          />
          <n-select
            v-model:value="filterHandled"
            :options="handledOptions"
            placeholder="处理状态"
            clearable
            size="small"
            style="width: 100px"
          />
        </n-space>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card critical">
        <div class="stat-value">{{ stats.critical }}</div>
        <div class="stat-label">严重预警</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-value">{{ stats.warning }}</div>
        <div class="stat-label">警告预警</div>
      </div>
      <div class="stat-card info">
        <div class="stat-value">{{ stats.info }}</div>
        <div class="stat-label">提示信息</div>
      </div>
      <div class="stat-card handled">
        <div class="stat-value">{{ stats.handled }}</div>
        <div class="stat-label">已处理</div>
      </div>
    </div>

    <!-- 预警列表 -->
    <div class="warning-panel">
      <n-spin :show="loading">
        <n-data-table
          :columns="warningColumns"
          :data="filteredWarnings"
          :row-key="(row: WarningStock) => row.id"
          striped
          size="small"
        />
        <n-empty v-if="!loading && filteredWarnings.length === 0" description="暂无预警记录" class="py-8" />
      </n-spin>
    </div>

    <!-- 预警条件配置弹窗 -->
    <n-modal v-model:show="showConfigModal" preset="card" title="预警条件配置" style="width: 800px">
      <div class="config-content">
        <n-spin :show="loadingConditions">
          <div class="condition-groups">
            <!-- 按周期分组显示 -->
            <div class="condition-group" v-for="(conditions, period) in groupedConditions" :key="period">
              <div class="group-title">{{ getPeriodLabel(period) }}</div>
              <div class="condition-list">
                <div class="condition-item" v-for="cond in conditions" :key="cond.id">
                  <div class="condition-main">
                    <n-switch
                      :value="cond.is_enabled"
                      @update:value="(val) => toggleCondition(cond, val)"
                    />
                    <span class="condition-name">{{ cond.condition_name }}</span>
                    <n-tag :type="getPriorityType(cond.priority)" size="small" :bordered="false">
                      {{ getPriorityLabel(cond.priority) }}
                    </n-tag>
                  </div>
                  <div class="condition-desc">{{ cond.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </n-spin>
      </div>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="showConfigModal = false">关闭</n-button>
          <n-button type="primary" @click="initConditions" :loading="initializing">
            初始化预置条件
          </n-button>
        </div>
      </template>
    </n-modal>

    <!-- 预警详情弹窗 -->
    <n-modal v-model:show="showDetailModal" preset="card" title="预警详情" style="width: 600px">
      <div class="detail-content" v-if="selectedWarning">
        <n-descriptions label-placement="left" :column="2">
          <n-descriptions-item label="股票代码">
            <n-tag type="info">{{ selectedWarning.stock_code }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="股票名称">{{ selectedWarning.stock_name }}</n-descriptions-item>
          <n-descriptions-item label="当前价格">
            <span :class="selectedWarning.change_percent >= 0 ? 'rise' : 'fall'">
              {{ formatPrice(selectedWarning.price) }}
            </span>
          </n-descriptions-item>
          <n-descriptions-item label="涨跌幅">
            <span :class="selectedWarning.change_percent >= 0 ? 'rise' : 'fall'">
              {{ formatChange(selectedWarning.change_percent) }}
            </span>
          </n-descriptions-item>
          <n-descriptions-item label="预警条件" :span="2">
            <n-tag :type="getWarningType(selectedWarning.warning_level)">
              {{ selectedWarning.condition_name }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="触发时间" :span="2">
            {{ formatDateTime(selectedWarning.trigger_time) }}
          </n-descriptions-item>
          <n-descriptions-item label="触发指标值" :span="2">
            <n-code :code="JSON.stringify(selectedWarning.trigger_value, null, 2)" language="json" />
          </n-descriptions-item>
        </n-descriptions>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="handleWarning(selectedWarning, 'IGNORE')">忽略</n-button>
          <n-button type="warning" @click="handleWarning(selectedWarning, 'WATCH')">关注</n-button>
          <n-button type="error" @click="handleWarning(selectedWarning, 'SELL')">卖出</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton, NIcon, NSelect, NSpin, NTag, NModal, NDataTable, NEmpty,
  NSpace, NSwitch, NDescriptions, NDescriptionsItem, NCode, useMessage
} from 'naive-ui'
import { RefreshOutline, SettingsOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import {
  fetchWarningStocks,
  fetchWarningConditions,
  updateWarningCondition,
  handleWarningStock,
  initWarningConditions,
  type WarningStock,
  type WarningCondition
} from '@/api/warning'

const message = useMessage()

// 数据
const warningStocks = ref<WarningStock[]>([])
const conditions = ref<WarningCondition[]>([])
const loading = ref(false)
const loadingConditions = ref(false)
const initializing = ref(false)

// 筛选
const filterLevel = ref<string | null>(null)
const filterHandled = ref<boolean | null>(null)

// 弹窗
const showConfigModal = ref(false)
const showDetailModal = ref(false)
const selectedWarning = ref<WarningStock | null>(null)

// 选项
const levelOptions = [
  { label: '严重', value: 'critical' },
  { label: '警告', value: 'warning' },
  { label: '提示', value: 'info' }
]

const handledOptions = [
  { label: '未处理', value: false },
  { label: '已处理', value: true }
]

// 统计数据
const stats = computed(() => {
  const all = warningStocks.value
  return {
    critical: all.filter(s => s.warning_level === 'critical' && !s.is_handled).length,
    warning: all.filter(s => s.warning_level === 'warning' && !s.is_handled).length,
    info: all.filter(s => s.warning_level === 'info' && !s.is_handled).length,
    handled: all.filter(s => s.is_handled).length
  }
})

// 筛选后的列表
const filteredWarnings = computed(() => {
  let result = warningStocks.value
  if (filterLevel.value) {
    result = result.filter(s => s.warning_level === filterLevel.value)
  }
  if (filterHandled.value !== null) {
    result = result.filter(s => s.is_handled === filterHandled.value)
  }
  return result
})

// 按周期分组的预警条件
const groupedConditions = computed(() => {
  const groups: Record<string, WarningCondition[]> = {}
  for (const cond of conditions.value) {
    if (!groups[cond.period]) {
      groups[cond.period] = []
    }
    groups[cond.period].push(cond)
  }
  return groups
})

// 表格列
const warningColumns = [
  {
    title: '代码', key: 'stock_code', width: 100,
    render: (row: WarningStock) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.stock_code })
  },
  { title: '名称', key: 'stock_name', width: 100 },
  {
    title: '价格', key: 'price', width: 90,
    render: (row: WarningStock) => h('span', {
      class: row.change_percent >= 0 ? 'rise' : 'fall'
    }, formatPrice(row.price))
  },
  {
    title: '涨跌幅', key: 'change_percent', width: 90,
    render: (row: WarningStock) => h('span', {
      class: row.change_percent >= 0 ? 'rise' : 'fall'
    }, formatChange(row.change_percent))
  },
  {
    title: '预警条件', key: 'condition_name', width: 140,
    render: (row: WarningStock) => h(NTag, {
      type: getWarningType(row.warning_level), size: 'small'
    }, { default: () => row.condition_name })
  },
  {
    title: '级别', key: 'warning_level', width: 80,
    render: (row: WarningStock) => h(NTag, {
      type: getPriorityType(row.warning_level), size: 'small', bordered: false
    }, { default: () => getPriorityLabel(row.warning_level) })
  },
  {
    title: '触发时间', key: 'trigger_time', width: 140,
    render: (row: WarningStock) => formatDateTime(row.trigger_time)
  },
  {
    title: '状态', key: 'is_handled', width: 80,
    render: (row: WarningStock) => h(NTag, {
      type: row.is_handled ? 'success' : 'warning', size: 'small'
    }, { default: () => row.is_handled ? '已处理' : '待处理' })
  },
  {
    title: '处理', key: 'handle_action', width: 80,
    render: (row: WarningStock) => row.handle_action || '--'
  },
  {
    title: '操作', key: 'actions', width: 200,
    render: (row: WarningStock) => h(NSpace, {}, {
      default: () => [
        h(NButton, { size: 'tiny', onClick: () => showWarningDetail(row) }, { default: () => '详情' }),
        !row.is_handled && h(NButton, { size: 'tiny', type: 'warning', onClick: () => handleWarning(row, 'WATCH') }, { default: () => '关注' }),
        !row.is_handled && h(NButton, { size: 'tiny', type: 'error', onClick: () => handleWarning(row, 'SELL') }, { default: () => '卖出' }),
        !row.is_handled && h(NButton, { size: 'tiny', onClick: () => handleWarning(row, 'IGNORE') }, { default: () => '忽略' })
      ].filter(Boolean)
    })
  }
]

// 辅助函数
function getWarningType(level: string): 'error' | 'warning' | 'info' {
  if (level === 'critical') return 'error'
  if (level === 'warning') return 'warning'
  return 'info'
}

function getPriorityType(priority: string): 'error' | 'warning' | 'info' | 'success' {
  if (priority === 'critical') return 'error'
  if (priority === 'warning') return 'warning'
  if (priority === 'info') return 'info'
  return 'success'
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '提示'
  }
  return labels[priority] || priority
}

function getPeriodLabel(period: string): string {
  const labels: Record<string, string> = {
    '30min': '30分钟',
    '60min': '60分钟',
    'daily': '日线',
    'weekly': '周线'
  }
  return labels[period] || period
}

function formatPrice(price: number | null | undefined): string {
  if (price == null) return '--'
  return price.toFixed(2)
}

function formatChange(change: number | null | undefined): string {
  if (change == null) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${(change * 100).toFixed(2)}%`
}

function formatDateTime(time: string): string {
  if (!time) return '--'
  return dayjs(time).format('MM-DD HH:mm:ss')
}

// 显示预警详情
function showWarningDetail(warning: WarningStock) {
  selectedWarning.value = warning
  showDetailModal.value = true
}

// 切换预警条件启用状态
async function toggleCondition(condition: WarningCondition, enabled: boolean) {
  try {
    await updateWarningCondition(condition.id, { is_enabled: enabled })
    condition.is_enabled = enabled
    message.success(enabled ? '已启用' : '已禁用')
  } catch (error) {
    message.error('操作失败')
  }
}

// 处理预警股票
async function handleWarning(stock: WarningStock | null, action: 'IGNORE' | 'SELL' | 'WATCH') {
  if (!stock) return

  try {
    await handleWarningStock(stock.id, action)
    message.success('处理成功')
    showDetailModal.value = false
    loadWarningStocks()
  } catch (error) {
    message.error('处理失败')
  }
}

// 加载预警股票
async function loadWarningStocks() {
  loading.value = true
  try {
    const data = await fetchWarningStocks({ limit: 100 })
    warningStocks.value = data
  } catch (error) {
    console.error('加载预警股票失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载预警条件
async function loadConditions() {
  loadingConditions.value = true
  try {
    const data = await fetchWarningConditions()
    conditions.value = data
  } catch (error) {
    console.error('加载预警条件失败:', error)
  } finally {
    loadingConditions.value = false
  }
}

// 初始化预置条件
async function initConditions() {
  initializing.value = true
  try {
    await initWarningConditions()
    message.success('初始化成功')
    await loadConditions()
  } catch (error) {
    message.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

onMounted(() => {
  loadWarningStocks()
  loadConditions()
})
</script>

<style scoped lang="scss">
.warning-page {
  padding: 16px;
  height: calc(100vh - 50px - 32px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
  }
}

.stats-row {
  display: flex;
  gap: 16px;

  .stat-card {
    flex: 1;
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    border-left: 4px solid #ddd;

    &.critical {
      border-left-color: #d03050;
      .stat-value { color: #d03050; }
    }
    &.warning {
      border-left-color: #f0a020;
      .stat-value { color: #f0a020; }
    }
    &.info {
      border-left-color: #2080f0;
      .stat-value { color: #2080f0; }
    }
    &.handled {
      border-left-color: #18a058;
      .stat-value { color: #18a058; }
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
    }

    .stat-label {
      font-size: 14px;
      color: #666;
      margin-top: 4px;
    }
  }
}

.warning-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  flex: 1;
}

.py-8 {
  padding-top: 32px;
  padding-bottom: 32px;
}

.rise { color: #18a058; }
.fall { color: #d03050; }

.config-content {
  max-height: 500px;
  overflow-y: auto;

  .condition-groups {
    .condition-group {
      margin-bottom: 20px;

      .group-title {
        font-size: 14px;
        font-weight: 500;
        color: #2080f0;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid rgba(100, 150, 255, 0.2);
      }

      .condition-list {
        .condition-item {
          padding: 10px 0;
          border-bottom: 1px solid rgba(100, 150, 255, 0.1);

          .condition-main {
            display: flex;
            align-items: center;
            gap: 12px;

            .condition-name {
              font-weight: 500;
            }
          }

          .condition-desc {
            font-size: 12px;
            color: #999;
            margin-top: 6px;
            padding-left: 40px;
          }
        }
      }
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: space-between;
}

.detail-content {
  padding: 8px 0;
}
</style>