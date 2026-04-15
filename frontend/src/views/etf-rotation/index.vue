<template>
  <div class="etf-rotation-page">
    <n-card title="ETF轮动策略监控">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="handleCreateStrategy">
            新建策略
          </n-button>
          <n-button @click="handleEtfPool">
            ETF池配置
          </n-button>
          <n-button @click="handleRefresh">
            刷新数据
          </n-button>
        </n-space>
      </template>

      <!-- 策略选择 -->
      <n-space vertical>
        <n-select
          v-model:value="selectedStrategyId"
          :options="strategyOptions"
          placeholder="选择策略"
          @update:value="handleStrategyChange"
          style="width: 200px"
        />

        <n-spin :show="loading">
          <n-grid :cols="2" :x-gap="16" :y-gap="16">
            <!-- 当前持仓 -->
            <n-grid-item>
              <n-card title="当前持仓" size="small">
                <n-empty v-if="positions.length === 0" description="暂无持仓" />
                <n-list v-else bordered>
                  <n-list-item v-for="pos in positions" :key="pos.etf_code">
                    <n-thing :title="pos.etf_name" :description="pos.etf_code">
                      <template #header-extra>
                        <n-tag :type="pos.profit_pct >= 0 ? 'success' : 'error'">
                          {{ pos.profit_pct >= 0 ? '+' : '' }}{{ pos.profit_pct?.toFixed(2) }}%
                        </n-tag>
                      </template>
                      <n-space>
                        <span>持有{{ pos.hold_days }}天</span>
                        <span>收盘: {{ pos.current_price }}</span>
                      </n-space>
                    </n-thing>
                  </n-list-item>
                </n-list>
              </n-card>
            </n-grid-item>

            <!-- 评分排名 -->
            <n-grid-item>
              <n-card title="今日评分排名" size="small">
                <template #header-extra>
                  <n-text depth="3">{{ scores.trade_date }}</n-text>
                </template>
                <n-data-table
                  :columns="scoreColumns"
                  :data="scores.scores"
                  :pagination="false"
                  size="small"
                />
              </n-card>
            </n-grid-item>

            <!-- 策略表现 -->
            <n-grid-item :span="2">
              <n-card title="策略表现" size="small">
                <n-space>
                  <n-statistic label="总收益" :value="performance.total_return">
                    <template #suffix>%</template>
                  </n-statistic>
                  <n-statistic label="最大回撤" :value="performance.max_drawdown">
                    <template #suffix>%</template>
                  </n-statistic>
                  <n-statistic label="夏普比率" :value="performance.sharpe_ratio" />
                  <n-statistic label="交易次数" :value="performance.trade_count" />
                </n-space>
              </n-card>
            </n-grid-item>

            <!-- 最新信号 -->
            <n-grid-item :span="2">
              <n-card title="最新信号" size="small">
                <n-empty v-if="signals.length === 0" description="暂无信号" />
                <n-list v-else bordered>
                  <n-list-item v-for="signal in signals" :key="signal.id">
                    <n-thing :title="`${signal.signal_date} ${signal.action_display}`">
                      <template #header-extra>
                        <n-tag :type="signal.action === 'buy' ? 'success' : 'warning'">
                          {{ signal.etf_name }}
                        </n-tag>
                      </template>
                      <n-text>{{ signal.reason }}</n-text>
                      <template #action>
                        <n-space>
                          <n-button size="small" @click="handleExecuteSignal(signal)">
                            执行
                          </n-button>
                          <n-button size="small" tertiary @click="handleIgnoreSignal(signal)">
                            忽略
                          </n-button>
                        </n-space>
                      </template>
                    </n-thing>
                  </n-list-item>
                </n-list>
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-spin>
      </n-space>

      <!-- 底部操作 -->
      <template #footer>
        <n-space>
          <n-button @click="handleBacktest">回测分析</n-button>
          <n-button @click="handleSignalHistory">信号历史</n-button>
          <n-button @click="handleGenerateSignals" type="primary">
            生成信号
          </n-button>
        </n-space>
      </template>
    </n-card>

    <!-- 新建策略对话框 -->
    <n-modal v-model:show="showCreateModal" preset="card" title="新建轮动策略" style="width: 600px">
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="120">
        <n-form-item label="策略名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入策略名称" />
        </n-form-item>
        <n-form-item label="策略描述" path="description">
          <n-input v-model:value="formData.description" placeholder="请输入策略描述" />
        </n-form-item>
        <n-form-item label="斜率周期" path="slope_period">
          <n-input-number v-model:value="formData.slope_period" :min="5" :max="60" />
        </n-form-item>
        <n-form-item label="RSRS周期" path="rsrs_period">
          <n-input-number v-model:value="formData.rsrs_period" :min="5" :max="30" />
        </n-form-item>
        <n-form-item label="买入阈值" path="rsrs_buy_threshold">
          <n-input-number v-model:value="formData.rsrs_buy_threshold" :min="0.5" :max="1.5" :step="0.1" />
        </n-form-item>
        <n-form-item label="卖出阈值" path="rsrs_sell_threshold">
          <n-input-number v-model:value="formData.rsrs_sell_threshold" :min="-1.5" :max="-0.5" :step="0.1" />
        </n-form-item>
        <n-form-item label="持仓数量" path="hold_count">
          <n-input-number v-model:value="formData.hold_count" :min="1" :max="5" />
        </n-form-item>
        <n-form-item label="调仓频率" path="rebalance_freq">
          <n-select v-model:value="formData.rebalance_freq" :options="freqOptions" />
        </n-form-item>
        <n-form-item label="执行模式" path="execute_mode">
          <n-select v-model:value="formData.execute_mode" :options="modeOptions" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmitCreate">创建</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import { NTag, NButton, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  getRotationStrategies,
  getRotationStrategyStats,
  createRotationStrategy,
  getLatestScores,
  getSignals,
  generateSignals,
  updateRotationStrategyStatus
} from '@/api/etfRotation'
import type {
  RotationStrategyListItem,
  RotationStrategyCreate,
  EtfScore,
  RotationSignal,
  ScoreResponse
} from '@/types/etfRotation'

const message = useMessage()

// 状态
const loading = ref(false)
const selectedStrategyId = ref<number | null>(null)
const strategies = ref<RotationStrategyListItem[]>([])
const scores = ref<ScoreResponse>({ trade_date: '', strategy_name: '', scores: [] })
const signals = ref<RotationSignal[]>([])
const positions = ref<any[]>([])
const performance = reactive({
  total_return: 0,
  max_drawdown: 0,
  sharpe_ratio: 0,
  trade_count: 0
})

// 新建策略
const showCreateModal = ref(false)
const formRef = ref()
const formData = reactive<RotationStrategyCreate>({
  name: '',
  description: '',
  slope_period: 20,
  rsrs_period: 18,
  rsrs_z_window: 100,
  rsrs_buy_threshold: 0.7,
  rsrs_sell_threshold: -0.7,
  ma_period: 20,
  hold_count: 2,
  rebalance_freq: 'weekly',
  execute_mode: 'simulate'
})
const formRules = {
  name: { required: true, message: '请输入策略名称' }
}

// 下拉选项
const strategyOptions = computed(() =>
  strategies.value.map(s => ({ label: s.name, value: s.id }))
)
const freqOptions = [
  { label: '每日', value: 'daily' },
  { label: '每周', value: 'weekly' },
  { label: '每月', value: 'monthly' }
]
const modeOptions = [
  { label: '模拟运行', value: 'simulate' },
  { label: '信号提醒', value: 'alert' }
]

// 评分表格列
const scoreColumns: DataTableColumns<EtfScore> = [
  { title: '排名', key: 'rank', width: 60 },
  { title: 'ETF名称', key: 'etf_name', width: 100 },
  { title: '代码', key: 'etf_code', width: 80 },
  { title: '评分', key: 'momentum_score', width: 80 },
  { title: 'RSRS Z', key: 'rsrs_z_score', width: 80 },
  {
    title: '信号',
    key: 'signal',
    width: 80,
    render(row) {
      if (row.rsrs_z_score > 0.7 && row.close_price > row.ma_value) {
        return h(NTag, { type: 'success', size: 'small' }, { default: () => '买入候选' })
      }
      if (row.rsrs_z_score < -0.7) {
        return h(NTag, { type: 'warning', size: 'small' }, { default: () => '卖出信号' })
      }
      return h(NTag, { type: 'default', size: 'small' }, { default: () => '观察' })
    }
  }
]

// 加载策略列表
async function loadStrategies() {
  try {
    strategies.value = await getRotationStrategies()
    if (strategies.value.length > 0 && !selectedStrategyId.value) {
      selectedStrategyId.value = strategies.value[0].id
      await loadData()
    }
  } catch (e) {
    message.error('加载策略列表失败')
  }
}

// 加载评分和信号数据
async function loadData() {
  if (!selectedStrategyId.value) return

  loading.value = true
  try {
    scores.value = await getLatestScores(selectedStrategyId.value)
    signals.value = await getSignals(selectedStrategyId.value, { limit: 5 })
  } catch (e) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 切换策略
function handleStrategyChange() {
  loadData()
}

// 刷新数据
function handleRefresh() {
  loadData()
}

// 新建策略
function handleCreateStrategy() {
  showCreateModal.value = true
}

async function handleSubmitCreate() {
  try {
    await formRef.value?.validate()
    await createRotationStrategy(formData)
    message.success('策略创建成功')
    showCreateModal.value = false
    await loadStrategies()
  } catch (e) {
    // 验证失败或API错误
  }
}

// ETF池配置
function handleEtfPool() {
  // 跳转到ETF池配置页面
  window.location.href = '/policy/etf-rotation/pool'
}

// 回测分析
function handleBacktest() {
  // 跳转到回测页面
  window.location.href = '/policy/etf-rotation/backtest'
}

// 信号历史
function handleSignalHistory() {
  message.info('信号历史功能开发中')
}

// 生成信号
async function handleGenerateSignals() {
  if (!selectedStrategyId.value) return

  try {
    const result = await generateSignals(selectedStrategyId.value)
    message.success(`生成 ${result.generated_count} 个信号`)
    await loadData()
  } catch (e) {
    message.error('生成信号失败')
  }
}

// 执行信号
function handleExecuteSignal(signal: RotationSignal) {
  message.info(`执行信号: ${signal.action_display} ${signal.etf_name}`)
}

// 忽略信号
function handleIgnoreSignal(signal: RotationSignal) {
  message.info(`忽略信号: ${signal.etf_name}`)
}

// 初始化
onMounted(() => {
  loadStrategies()
})
</script>

<style scoped>
.etf-rotation-page {
  padding: 16px;
}
</style>