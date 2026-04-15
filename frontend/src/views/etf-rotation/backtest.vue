<template>
  <div class="backtest-page">
    <n-card title="回测分析">
      <template #header-extra>
        <n-button @click="handleBack">
          返回监控
        </n-button>
      </template>

      <!-- 回测配置 -->
      <n-card title="回测配置" size="small" class="mb-4">
        <n-form :model="backtestConfig" label-placement="left" label-width="100">
          <n-grid :cols="4" :x-gap="16">
            <n-grid-item>
              <n-form-item label="开始日期">
                <n-date-picker v-model:value="startDateTs" type="date" clearable />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="结束日期">
                <n-date-picker v-model:value="endDateTs" type="date" clearable />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="初始资金">
                <n-input-number v-model:value="backtestConfig.initial_capital" :min="10000" :step="10000" />
              </n-form-item>
            </n-grid-item>
            <n-grid-item>
              <n-form-item label="策略选择">
                <n-select v-model:value="selectedStrategyId" :options="strategyOptions" placeholder="选择策略" />
              </n-form-item>
            </n-grid-item>
          </n-grid>
          <n-space justify="end">
            <n-button type="primary" :loading="running" @click="handleRunBacktest">
              运行回测
            </n-button>
          </n-space>
        </n-form>
      </n-card>

      <!-- 回测结果 -->
      <n-spin :show="running">
        <n-card v-if="backtestResult" title="回测结果" size="small">
          <!-- 指标展示 -->
          <n-grid :cols="6" :x-gap="16" class="mb-4">
            <n-grid-item>
              <n-statistic label="总收益">
                <template #default>
                  <n-text :type="backtestResult.total_return >= 0 ? 'success' : 'error'">
                    {{ backtestResult.total_return?.toFixed(2) }}%
                  </n-text>
                </template>
              </n-statistic>
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="年化收益" :value="backtestResult.annual_return?.toFixed(2)">
                <template #suffix>%</template>
              </n-statistic>
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="最大回撤" :value="backtestResult.max_drawdown?.toFixed(2)">
                <template #suffix>%</template>
              </n-statistic>
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="胜率" :value="backtestResult.win_rate?.toFixed(2)">
                <template #suffix>%</template>
              </n-statistic>
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="夏普比率" :value="backtestResult.sharpe_ratio?.toFixed(2)" />
            </n-grid-item>
            <n-grid-item>
              <n-statistic label="交易次数" :value="backtestResult.trade_count" />
            </n-grid-item>
          </n-grid>

          <!-- 收益曲线 TODO: ECharts -->
          <n-card title="收益曲线" size="small">
            <n-empty description="收益曲线图表开发中（需ECharts）" />
          </n-card>

          <!-- 交易记录 -->
          <n-card title="交易记录" size="small" class="mt-4">
            <n-empty description="暂无交易记录" />
          </n-card>
        </n-card>

        <n-empty v-else description="请配置参数并运行回测" />
      </n-spin>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  getRotationStrategies,
  runBacktest
} from '@/api/etfRotation'
import type { RotationStrategyListItem, BacktestResult } from '@/types/etfRotation'

const message = useMessage()

// 状态
const running = ref(false)
const selectedStrategyId = ref<number | null>(null)
const strategies = ref<RotationStrategyListItem[]>([])
const startDateTs = ref<number>(Date.now() - 365 * 24 * 60 * 60 * 1000) // 一年前
const endDateTs = ref<number>(Date.now())
const backtestResult = ref<BacktestResult | null>(null)

// 配置
const backtestConfig = reactive({
  initial_capital: 100000
})

// 策略选项
const strategyOptions = computed(() =>
  strategies.value.map(s => ({ label: s.name, value: s.id }))
)

// 加载策略列表
async function loadStrategies() {
  try {
    strategies.value = await getRotationStrategies()
    if (strategies.value.length > 0) {
      selectedStrategyId.value = strategies.value[0].id
    }
  } catch (e) {
    message.error('加载策略失败')
  }
}

// 运行回测
async function handleRunBacktest() {
  if (!selectedStrategyId.value) {
    message.warning('请选择策略')
    return
  }

  running.value = true
  try {
    const startDate = new Date(startDateTs.value).toISOString().split('T')[0]
    const endDate = new Date(endDateTs.value).toISOString().split('T')[0]

    const result = await runBacktest(selectedStrategyId.value, {
      start_date: startDate,
      end_date: endDate,
      initial_capital: backtestConfig.initial_capital
    })

    message.info(result.message || '回测请求已提交')

    // TODO: 获取回测结果详情
    // backtestResult.value = await getBacktestResult(selectedStrategyId.value, result.backtest_id)

  } catch (e) {
    message.error('回测失败')
  } finally {
    running.value = false
  }
}

// 返回监控页
function handleBack() {
  window.location.href = '/policy/etf-rotation'
}

// 初始化
onMounted(() => {
  loadStrategies()
})
</script>

<style scoped>
.backtest-page {
  padding: 16px;
}
.mb-4 {
  margin-bottom: 16px;
}
.mt-4 {
  margin-top: 16px;
}
</style>