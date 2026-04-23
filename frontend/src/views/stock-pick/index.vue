<template>
  <div class="stock-pick-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>选股策略</h2>
        <n-space>
          <n-button type="primary" @click="showAddModal = true">
            <template #icon>
              <n-icon><AddOutline /></n-icon>
            </template>
            新建策略
          </n-button>
        </n-space>
      </div>
    </div>

    <!-- Tab切换 -->
    <n-tabs v-model:value="activeTab" type="line" animated>
      <n-tab-pane name="strategies" tab="策略列表">
        <n-spin :show="loadingStrategies">
          <n-data-table
            :columns="strategyColumns"
            :data="strategies"
            :row-key="(row: StockPickStrategy) => row.id"
            striped
            size="small"
          />
        </n-spin>
      </n-tab-pane>

      <n-tab-pane name="today" tab="今日股池">
        <n-spin :show="loadingToday">
          <n-data-table
            :columns="poolColumns"
            :data="todayPool"
            :row-key="(row: StrategyTrackRecord) => row.id"
            striped
            size="small"
          />
        </n-spin>
      </n-tab-pane>

      <n-tab-pane name="tomorrow" tab="明日股池">
        <n-spin :show="loadingTomorrow">
          <n-data-table
            :columns="poolColumns"
            :data="tomorrowPool"
            :row-key="(row: StrategyTrackRecord) => row.id"
            striped
            size="small"
          />
        </n-spin>
      </n-tab-pane>
    </n-tabs>

    <!-- 新建策略弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="新建选股策略" style="width: 900px">
      <n-form ref="addFormRef" :model="addForm" label-placement="left" label-width="100">
        <n-form-item label="策略KEY" required>
          <n-input v-model:value="addForm.strategy_key" placeholder="如：MA_CROSS_5_10" />
        </n-form-item>
        <n-form-item label="策略名称" required>
          <n-input v-model:value="addForm.strategy_name" placeholder="如：均线交叉选股" />
        </n-form-item>
        <n-form-item label="策略类型">
          <n-select v-model:value="addForm.strategy_type" :options="strategyTypeOptions" />
        </n-form-item>
        <n-form-item label="策略描述">
          <n-input v-model:value="addForm.description" type="textarea" placeholder="策略说明" />
        </n-form-item>

        <n-divider>选股配置</n-divider>
        <StrategyConfigEditor ref="configEditorRef" v-model="addForm.strategy_config" />

        <n-divider>执行设置</n-divider>
        <n-grid :cols="3" :x-gap="16">
          <n-gi>
            <n-form-item label="持续时间">
              <n-input-number v-model:value="addForm.duration_days" :min="1" :max="30">
                <template #suffix>天</template>
              </n-input-number>
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="生成时间">
              <n-time-picker v-model:value="generateTimeValue" format="HH:mm" />
            </n-form-item>
          </n-gi>
          <n-gi>
            <n-form-item label="提前生成">
              <n-input-number v-model:value="addForm.advance_days" :min="0" :max="7">
                <template #suffix>天</template>
              </n-input-number>
            </n-form-item>
          </n-gi>
        </n-grid>
        <n-form-item label="自动生成">
          <n-switch v-model:value="addForm.auto_generate" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleAddStrategy" :loading="adding">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 策略详情弹窗 -->
    <n-modal v-model:show="showDetailModal" preset="card" :title="currentStrategy?.strategy_name" style="width: 800px">
      <template v-if="currentStrategy">
        <n-descriptions label-placement="left" :column="2" bordered size="small">
          <n-descriptions-item label="策略KEY">
            <n-tag type="info" size="small">{{ currentStrategy.strategy_key }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="策略类型">
            {{ currentStrategy.strategy_type_display }}
          </n-descriptions-item>
          <n-descriptions-item label="持续时间">
            {{ currentStrategy.duration_days }} 天
          </n-descriptions-item>
          <n-descriptions-item label="生成时间">
            {{ currentStrategy.generate_time }}
          </n-descriptions-item>
          <n-descriptions-item label="提前生成">
            {{ currentStrategy.advance_days }} 天
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="currentStrategy.is_active ? 'success' : 'warning'" size="small">
              {{ currentStrategy.is_active ? '启用' : '禁用' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="累计生成">
            {{ currentStrategy.total_generated }} 只
          </n-descriptions-item>
          <n-descriptions-item label="成功率">
            {{ currentStrategy.success_rate ? currentStrategy.success_rate + '%' : '--' }}
          </n-descriptions-item>
        </n-descriptions>

        <n-divider>策略配置</n-divider>
        <n-code :code="JSON.stringify(currentStrategy.strategy_config, null, 2)" language="json" />

        <n-divider>追踪记录</n-divider>
        <n-data-table :columns="poolColumns" :data="strategyRecords" size="small" />
      </template>

      <template #footer>
        <n-space justify="end">
          <n-button type="info" @click="handleExecuteStrategy" :loading="executing">执行策略</n-button>
          <n-button @click="showDetailModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import {
  NButton, NIcon, NInput, NSpin, NTag, NModal, NDataTable,
  NForm, NFormItem, NSelect, NInputNumber, NSwitch, NTimePicker,
  NSpace, NTabs, NTabPane, NDescriptions, NDescriptionsItem, NDivider, NCode,
  NGrid, NGi, useMessage
} from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import {
  fetchStockPickStrategies, createStockPickStrategy, deleteStockPickStrategy,
  executeStrategy, fetchTodayPool, fetchTomorrowPool, fetchTrackPool,
  StockPickStrategy, StrategyTrackRecord, StrategyConfig
} from '@/api/stockPick'
import StrategyConfigEditor from '@/components/StrategyConfigEditor.vue'

const message = useMessage()

const activeTab = ref('strategies')

const strategies = ref<StockPickStrategy[]>([])
const todayPool = ref<StrategyTrackRecord[]>([])
const tomorrowPool = ref<StrategyTrackRecord[]>([])
const strategyRecords = ref<StrategyTrackRecord[]>([])

const loadingStrategies = ref(false)
const loadingToday = ref(false)
const loadingTomorrow = ref(false)
const adding = ref(false)
const executing = ref(false)

const showAddModal = ref(false)
const showDetailModal = ref(false)
const currentStrategy = ref<StockPickStrategy | null>(null)

const addFormRef = ref()
const configEditorRef = ref()
const addForm = ref({
  strategy_key: '',
  strategy_name: '',
  strategy_type: 'technical',
  description: '',
  strategy_config: {
    indicators: [],
    conditions: [],
    logic: 'AND'
  } as StrategyConfig,
  duration_days: 3,
  generate_time: '09:00',
  advance_days: 1,
  auto_generate: true
})

const generateTimeValue = ref(Date.now())

const strategyTypeOptions = [
  { label: '技术指标', value: 'technical' },
  { label: '因子选股', value: 'factor' },
  { label: '形态识别', value: 'pattern' },
  { label: '组合策略', value: 'combination' }
]

const strategyColumns = [
  {
    title: 'KEY', key: 'strategy_key', width: 140,
    render: (row: StockPickStrategy) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.strategy_key })
  },
  { title: '名称', key: 'strategy_name', width: 150 },
  { title: '类型', key: 'strategy_type_display', width: 100 },
  { title: '持续时间', key: 'duration_days', width: 80, render: (row: StockPickStrategy) => `${row.duration_days}天` },
  { title: '生成时间', key: 'generate_time', width: 90 },
  {
    title: '状态', key: 'is_active', width: 80,
    render: (row: StockPickStrategy) => h(NTag, {
      type: row.is_active ? 'success' : 'warning', size: 'small'
    }, { default: () => row.is_active ? '启用' : '禁用' })
  },
  { title: '累计生成', key: 'total_generated', width: 80 },
  {
    title: '成功率', key: 'success_rate', width: 80,
    render: (row: StockPickStrategy) => row.success_rate ? `${row.success_rate}%` : '--'
  },
  {
    title: '操作', key: 'actions', width: 180,
    render: (row: StockPickStrategy) => h(NSpace, {}, {
      default: () => [
        h(NButton, { size: 'tiny', type: 'info', onClick: () => openDetail(row) }, { default: () => '详情' }),
        h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDeleteStrategy(row) }, { default: () => '删除' })
      ]
    })
  }
]

const poolColumns = [
  {
    title: '代码', key: 'stock_code', width: 100,
    render: (row: StrategyTrackRecord) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.stock_code })
  },
  { title: '名称', key: 'stock_name', width: 100 },
  {
    title: '策略', key: 'strategy_key', width: 140,
    render: (row: StrategyTrackRecord) => h(NTag, { size: 'small', bordered: false }, { default: () => row.strategy_key })
  },
  { title: '异动类型', key: 'anomaly_type_display', width: 100 },
  {
    title: '置信度', key: 'confidence', width: 80,
    render: (row: StrategyTrackRecord) => {
      const color = row.confidence >= 70 ? '#18a058' : row.confidence >= 50 ? '#f0a020' : '#d03050'
      return h('span', { style: { color, fontWeight: 'bold' } }, `${row.confidence}%`)
    }
  },
  {
    title: '状态', key: 'status_display', width: 80,
    render: (row: StrategyTrackRecord) => {
      const typeMap: Record<string, 'success' | 'warning' | 'error' | 'info'> = {
        pending: 'warning', verified: 'success', failed: 'error', expired: 'info'
      }
      return h(NTag, { type: typeMap[row.status] || 'default', size: 'small' }, { default: () => row.status_display })
    }
  },
  {
    title: '目标日期', key: 'target_date', width: 110,
    render: (row: StrategyTrackRecord) => dayjs(row.target_date).format('MM-DD')
  },
  {
    title: '入场价', key: 'entry_price', width: 90,
    render: (row: StrategyTrackRecord) => row.entry_price ? row.entry_price.toFixed(2) : '--'
  },
  {
    title: '最大收益', key: 'max_return', width: 90,
    render: (row: StrategyTrackRecord) => {
      if (row.max_return == null) return '--'
      const color = row.max_return >= 0 ? '#18a058' : '#d03050'
      return h('span', { style: { color } }, `${row.max_return >= 0 ? '+' : ''}${row.max_return.toFixed(2)}%`)
    }
  }
]

async function loadStrategies() {
  loadingStrategies.value = true
  try {
    strategies.value = await fetchStockPickStrategies()
  } catch (error) {
    console.error('加载策略失败:', error)
  } finally {
    loadingStrategies.value = false
  }
}

async function loadTodayPool() {
  loadingToday.value = true
  try {
    todayPool.value = await fetchTodayPool()
  } catch (error) {
    console.error('加载今日股池失败:', error)
  } finally {
    loadingToday.value = false
  }
}

async function loadTomorrowPool() {
  loadingTomorrow.value = true
  try {
    tomorrowPool.value = await fetchTomorrowPool()
  } catch (error) {
    console.error('加载明日股池失败:', error)
  } finally {
    loadingTomorrow.value = false
  }
}

async function handleAddStrategy() {
  if (!addForm.value.strategy_key || !addForm.value.strategy_name) {
    message.warning('请填写策略KEY和名称')
    return
  }

  adding.value = true
  try {
    const hours = new Date(generateTimeValue.value).getHours().toString().padStart(2, '0')
    const minutes = new Date(generateTimeValue.value).getMinutes().toString().padStart(2, '0')
    addForm.value.generate_time = `${hours}:${minutes}`

    await createStockPickStrategy(addForm.value)
    message.success('创建成功')
    showAddModal.value = false
    addForm.value = {
      strategy_key: '',
      strategy_name: '',
      strategy_type: 'technical',
      description: '',
      strategy_config: {},
      duration_days: 3,
      generate_time: '09:00',
      advance_days: 1,
      auto_generate: true
    }
    loadStrategies()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '创建失败')
  } finally {
    adding.value = false
  }
}

async function handleDeleteStrategy(strategy: StockPickStrategy) {
  try {
    await deleteStockPickStrategy(strategy.id)
    message.success('删除成功')
    loadStrategies()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '删除失败')
  }
}

async function openDetail(strategy: StockPickStrategy) {
  currentStrategy.value = strategy
  showDetailModal.value = true

  try {
    strategyRecords.value = await fetchTrackPool({ strategy_id: strategy.id, limit: 20 })
  } catch (error) {
    strategyRecords.value = []
  }
}

async function handleExecuteStrategy() {
  if (!currentStrategy.value) return

  executing.value = true
  try {
    const result = await executeStrategy(currentStrategy.value.id)
    message.success(result.message)
    strategyRecords.value = await fetchTrackPool({ strategy_id: currentStrategy.value.id, limit: 20 })
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '执行失败')
  } finally {
    executing.value = false
  }
}

onMounted(() => {
  loadStrategies()
  loadTodayPool()
  loadTomorrowPool()
})
</script>

<style scoped lang="scss">
.stock-pick-page {
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
}

.ml-2 {
  margin-left: 8px;
}

.text-gray-500 {
  color: #666;
  font-size: 13px;
}
</style>