<template>
  <div class="signal-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>卖出信号明细</h2>
        <n-space>
          <n-button type="primary" @click="loadSignals" :loading="loading">
            <template #icon>
              <n-icon><RefreshOutline /></n-icon>
            </template>
            刷新
          </n-button>
          <n-button type="error" @click="clearHandledSignals" :loading="clearing">
            清理已处理
          </n-button>
        </n-space>
      </div>
      <div class="header-right">
        <n-space align="center">
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            size="small"
            @update:value="loadSignals"
          />
          <n-select
            v-model:value="filterAction"
            :options="actionOptions"
            placeholder="处理动作"
            clearable
            size="small"
            style="width: 100px"
          />
        </n-space>
      </div>
    </div>

    <!-- 统计行 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ signals.length }}</div>
        <div class="stat-label">信号总数</div>
      </div>
      <div class="stat-card sell">
        <div class="stat-value">{{ sellCount }}</div>
        <div class="stat-label">卖出信号</div>
      </div>
      <div class="stat-card watch">
        <div class="stat-value">{{ watchCount }}</div>
        <div class="stat-label">关注信号</div>
      </div>
      <div class="stat-card ignore">
        <div class="stat-value">{{ ignoreCount }}</div>
        <div class="stat-label">忽略信号</div>
      </div>
    </div>

    <!-- 信号列表 -->
    <div class="signal-panel">
      <n-spin :show="loading">
        <n-data-table
          :columns="signalColumns"
          :data="filteredSignals"
          :row-key="(row: SignalRecord) => row.id"
          striped
          size="small"
          :pagination="pagination"
        />
        <n-empty v-if="!loading && filteredSignals.length === 0" description="暂无卖出信号" class="py-8" />
      </n-spin>
    </div>

    <!-- 信号详情弹窗 -->
    <n-modal v-model:show="showDetailModal" preset="card" title="信号详情" style="width: 700px">
      <div class="detail-content" v-if="selectedSignal">
        <n-tabs type="line">
          <n-tab-pane name="basic" tab="基本信息">
            <n-descriptions label-placement="left" :column="2">
              <n-descriptions-item label="股票代码">
                <n-tag type="info">{{ selectedSignal.stock_code }}</n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="股票名称">{{ selectedSignal.stock_name }}</n-descriptions-item>
              <n-descriptions-item label="信号类型">
                <n-tag :type="getActionType(selectedSignal.handle_action)">
                  {{ selectedSignal.handle_action || '待处理' }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="预警级别">
                <n-tag :type="getLevelType(selectedSignal.warning_level)">
                  {{ getLevelLabel(selectedSignal.warning_level) }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="触发价格">
                <span :class="selectedSignal.change_percent >= 0 ? 'rise' : 'fall'">
                  {{ formatPrice(selectedSignal.price) }}
                </span>
              </n-descriptions-item>
              <n-descriptions-item label="涨跌幅">
                <span :class="selectedSignal.change_percent >= 0 ? 'rise' : 'fall'">
                  {{ formatChange(selectedSignal.change_percent) }}
                </span>
              </n-descriptions-item>
              <n-descriptions-item label="触发条件" :span="2">{{ selectedSignal.condition_name }}</n-descriptions-item>
              <n-descriptions-item label="触发时间" :span="2">{{ formatDateTime(selectedSignal.trigger_time) }}</n-descriptions-item>
              <n-descriptions-item label="处理时间" :span="2">
                {{ selectedSignal.handled_at ? formatDateTime(selectedSignal.handled_at) : '--' }}
              </n-descriptions-item>
            </n-descriptions>
          </n-tab-pane>
          <n-tab-pane name="indicator" tab="指标详情">
            <div class="indicator-detail">
              <div class="indicator-title">触发时的指标值</div>
              <n-code
                v-if="selectedSignal.trigger_value"
                :code="JSON.stringify(selectedSignal.trigger_value, null, 2)"
                language="json"
              />
              <div v-else class="no-data">暂无指标数据</div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton, NIcon, NSpin, NTag, NModal, NDataTable, NEmpty, NSpace,
  NDescriptions, NDescriptionsItem, NTabs, NTabPane, NCode, NDatePicker, NSelect, useMessage
} from 'naive-ui'
import { RefreshOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import {
  fetchWarningStocks,
  handleWarningStock,
  clearHandledStocks,
  type WarningStock
} from '@/api/warning'

const message = useMessage()

// 类型
interface SignalRecord extends WarningStock {
  handled_at?: string
  is_group?: boolean
  triggered_conditions?: Array<{
    condition_key: string
    condition_name: string
    triggered: boolean
  }>
}

// 数据
const signals = ref<SignalRecord[]>([])
const loading = ref(false)
const clearing = ref(false)

// 筛选
const dateRange = ref<[number, number] | null>(null)
const filterAction = ref<string | null>(null)

// 弹窗
const showDetailModal = ref(false)
const selectedSignal = ref<SignalRecord | null>(null)

// 分页
const pagination = {
  pageSize: 20
}

// 选项
const actionOptions = [
  { label: '卖出', value: 'SELL' },
  { label: '关注', value: 'WATCH' },
  { label: '忽略', value: 'IGNORE' }
]

// 统计
const sellCount = computed(() => signals.value.filter(s => s.handle_action === 'SELL').length)
const watchCount = computed(() => signals.value.filter(s => s.handle_action === 'WATCH').length)
const ignoreCount = computed(() => signals.value.filter(s => s.handle_action === 'IGNORE').length)

// 筛选后的列表
const filteredSignals = computed(() => {
  let result = signals.value
  if (filterAction.value) {
    result = result.filter(s => s.handle_action === filterAction.value)
  }
  if (dateRange.value) {
    const [start, end] = dateRange.value
    result = result.filter(s => {
      const time = new Date(s.trigger_time).getTime()
      return time >= start && time <= end
    })
  }
  return result
})

// 表格列
const signalColumns = [
  {
    title: '代码', key: 'stock_code', width: 100,
    render: (row: SignalRecord) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.stock_code })
  },
  { title: '名称', key: 'stock_name', width: 100 },
  {
    title: '价格', key: 'price', width: 90,
    render: (row: SignalRecord) => h('span', {
      class: row.change_percent >= 0 ? 'rise' : 'fall'
    }, formatPrice(row.price))
  },
  {
    title: '涨跌幅', key: 'change_percent', width: 90,
    render: (row: SignalRecord) => h('span', {
      class: row.change_percent >= 0 ? 'rise' : 'fall'
    }, formatChange(row.change_percent))
  },
  {
    title: '触发条件', key: 'condition_name', width: 180,
    render: (row: SignalRecord) => {
      if (row.is_group && row.triggered_conditions) {
        // 组合条件：显示组合名 + 满足的条件标签
        const tags = row.triggered_conditions.map((c: any) =>
          h(NTag, {
            type: c.triggered ? 'success' : 'default',
            size: 'small',
            bordered: false,
            style: 'margin: 2px'
          }, { default: () => c.condition_name })
        )

        return h(NSpace, { vertical: false, size: 2, wrap: true }, {
          default: () => [
            h('span', { style: 'font-weight: 500' }, row.condition_name),
            h('span', { style: 'color: #999' }, ' ('),
            ...tags,
            h('span', { style: 'color: #999' }, ')')
          ]
        })
      }

      // 普通条件
      return h(NTag, {
        type: getLevelType(row.warning_level), size: 'small'
      }, { default: () => row.condition_name })
    }
  },
  {
    title: '处理动作', key: 'handle_action', width: 90,
    render: (row: SignalRecord) => {
      if (!row.handle_action) return '--'
      return h(NTag, {
        type: getActionType(row.handle_action), size: 'small'
      }, { default: () => row.handle_action })
    }
  },
  {
    title: '触发时间', key: 'trigger_time', width: 150,
    render: (row: SignalRecord) => formatDateTime(row.trigger_time)
  },
  {
    title: '处理时间', key: 'handled_at', width: 150,
    render: (row: SignalRecord) => row.handled_at ? formatDateTime(row.handled_at) : '--'
  },
  {
    title: '操作', key: 'actions', width: 150,
    render: (row: SignalRecord) => h(NSpace, {}, {
      default: () => [
        h(NButton, { size: 'tiny', onClick: () => showSignalDetail(row) }, { default: () => '详情' }),
        !row.is_handled && h(NButton, { size: 'tiny', type: 'error', onClick: () => handleSignal(row, 'SELL') }, { default: () => '卖出' }),
        !row.is_handled && h(NButton, { size: 'tiny', onClick: () => handleSignal(row, 'IGNORE') }, { default: () => '忽略' })
      ].filter(Boolean)
    })
  }
]

// 辅助函数
function getLevelType(level: string): 'error' | 'warning' | 'info' {
  if (level === 'critical') return 'error'
  if (level === 'warning') return 'warning'
  return 'info'
}

function getLevelLabel(level: string): string {
  const labels: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '提示'
  }
  return labels[level] || level
}

function getActionType(action: string): 'error' | 'warning' | 'info' | 'success' {
  if (action === 'SELL') return 'error'
  if (action === 'WATCH') return 'warning'
  if (action === 'IGNORE') return 'info'
  return 'success'
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
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 显示信号详情
function showSignalDetail(signal: SignalRecord) {
  selectedSignal.value = signal
  showDetailModal.value = true
}

// 处理信号
async function handleSignal(signal: SignalRecord, action: 'SELL' | 'WATCH' | 'IGNORE') {
  try {
    await handleWarningStock(signal.id, action)
    message.success('处理成功')
    signal.is_handled = true
    signal.handle_action = action
    signal.handled_at = new Date().toISOString()
  } catch (error) {
    message.error('处理失败')
  }
}

// 加载信号
async function loadSignals() {
  loading.value = true
  try {
    const data = await fetchWarningStocks({ limit: 200 })
    signals.value = data as SignalRecord[]
  } catch (error) {
    console.error('加载信号失败:', error)
  } finally {
    loading.value = false
  }
}

// 清理已处理信号
async function clearHandledSignals() {
  clearing.value = true
  try {
    await clearHandledStocks()
    message.success('清理成功')
    loadSignals()
  } catch (error) {
    message.error('清理失败')
  } finally {
    clearing.value = false
  }
}

onMounted(() => {
  loadSignals()
})
</script>

<style scoped lang="scss">
.signal-page {
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
    border-left: 4px solid #2080f0;

    &.sell {
      border-left-color: #d03050;
      .stat-value { color: #d03050; }
    }
    &.watch {
      border-left-color: #f0a020;
      .stat-value { color: #f0a020; }
    }
    &.ignore {
      border-left-color: #909399;
      .stat-value { color: #909399; }
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #2080f0;
    }

    .stat-label {
      font-size: 14px;
      color: #666;
      margin-top: 4px;
    }
  }
}

.signal-panel {
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

.detail-content {
  padding: 8px 0;
}

.indicator-detail {
  .indicator-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 12px;
  }

  .no-data {
    color: #999;
    text-align: center;
    padding: 20px;
  }
}
</style>