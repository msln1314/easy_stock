<template>
  <div class="strategy-config-editor">
    <!-- 指标选择 -->
    <n-card title="选择指标" size="small" style="margin-bottom: 16px;">
      <n-space wrap>
        <n-tag
          v-for="ind in availableIndicators"
          :key="ind.indicator_key"
          :type="selectedIndicators.includes(ind.indicator_key) ? 'primary' : 'default'"
          style="cursor: pointer; margin-bottom: 8px;"
          @click="toggleIndicator(ind.indicator_key)"
        >
          {{ ind.indicator_name }}
        </n-tag>
      </n-space>
    </n-card>

    <!-- 已选指标参数配置 -->
    <n-card v-if="selectedIndicatorDetails.length > 0" title="指标参数" size="small" style="margin-bottom: 16px;">
      <n-space vertical>
        <n-card
          v-for="ind in selectedIndicatorDetails"
          :key="ind.indicator_key"
          size="small"
          style="background: var(--n-color-modal);"
        >
          <template #header>
            <n-space align="center">
              <span>{{ ind.indicator_name }}</span>
              <n-button size="tiny" type="error" @click="removeIndicator(ind.indicator_key)">移除</n-button>
            </n-space>
          </template>

          <!-- 参数配置 -->
          <n-space v-if="ind.params && ind.params.length > 0">
            <n-form-item
              v-for="param in ind.params"
              :key="param.key"
              :label="param.name"
              size="small"
            >
              <n-input-number
                v-if="param.type === 'int' || param.type === 'float'"
                v-model:value="indicatorParams[ind.indicator_key][param.key]"
                :min="param.min"
                :max="param.max"
                size="small"
                style="width: 120px;"
              />
              <n-select
                v-else-if="param.type === 'select'"
                v-model:value="indicatorParams[ind.indicator_key][param.key]"
                :options="(param.options || []).map(o => ({ label: o, value: o }))"
                size="small"
                style="width: 120px;"
              />
              <n-input
                v-else
                v-model:value="indicatorParams[ind.indicator_key][param.key]"
                size="small"
                style="width: 120px;"
              />
            </n-form-item>
          </n-space>

          <!-- 输出字段选择 -->
          <n-space v-if="ind.output_fields && ind.output_fields.length > 1">
            <span>输出:</span>
            <n-select
              v-model:value="indicatorOutputs[ind.indicator_key]"
              :options="ind.output_fields.map(f => ({ label: f.name, value: f.key }))"
              size="small"
              style="width: 150px;"
            />
          </n-space>
        </n-card>
      </n-space>
    </n-card>

    <!-- 条件配置 -->
    <n-card title="筛选条件" size="small" style="margin-bottom: 16px;">
      <template #header-extra>
        <n-button size="small" type="primary" @click="addCondition">添加条件</n-button>
      </template>

      <n-empty v-if="conditions.length === 0" description="请添加筛选条件" />

      <n-space vertical v-else>
        <n-card
          v-for="(cond, index) in conditions"
          :key="cond.id"
          size="small"
          style="background: var(--n-color-modal);"
        >
          <template #header>
            <n-space align="center">
              <span>条件 {{ index + 1 }}</span>
              <n-button size="tiny" type="error" quaternary @click="removeCondition(cond.id)">删除</n-button>
            </n-space>
          </template>

          <n-space align="center" wrap>
            <!-- 条件类型 -->
            <n-select
              v-model:value="cond.type"
              :options="conditionTypeOptions"
              size="small"
              style="width: 100px;"
              @update:value="onConditionTypeChange(cond)"
            />

            <!-- 指标类型 -->
            <template v-if="cond.type === 'indicator'">
              <n-select
                v-model:value="cond.indicator_key"
                :options="selectedIndicatorDetails.map(i => ({ label: i.indicator_name, value: i.indicator_key }))"
                size="small"
                style="width: 120px;"
                placeholder="选择指标"
                @update:value="onConditionIndicatorChange(cond)"
              />

              <!-- 输出字段 -->
              <n-select
                v-if="cond.indicator_key && getIndicatorOutputFields(cond.indicator_key).length > 1"
                v-model:value="cond.output_field"
                :options="getIndicatorOutputFields(cond.indicator_key || '').map(f => ({ label: f.name, value: f.key }))"
                size="small"
                style="width: 100px;"
              />
            </template>

            <!-- 行情类型 -->
            <template v-if="cond.type === 'quote'">
              <n-select
                v-model:value="cond.field"
                :options="quoteFieldOptions"
                size="small"
                style="width: 120px;"
                placeholder="选择字段"
              />
            </template>

            <!-- 操作符 -->
            <n-select
              v-model:value="cond.operator"
              :options="operatorOptions"
              size="small"
              style="width: 80px;"
            />

            <!-- 比较值 -->
            <n-select
              v-model:value="cond.value_type"
              :options="valueTypeOptions"
              size="small"
              style="width: 100px;"
            />

            <!-- 数值输入 -->
            <n-input-number
              v-if="cond.value_type === 'number'"
              v-model:value="cond.value"
              size="small"
              style="width: 120px;"
            />

            <!-- 指标比较 -->
            <template v-if="cond.value_type === 'indicator'">
              <n-select
                v-model:value="cond.value_indicator_key"
                :options="selectedIndicatorDetails.map(i => ({ label: i.indicator_name, value: i.indicator_key }))"
                size="small"
                style="width: 120px;"
                placeholder="选择指标"
              />
            </template>

            <!-- 行情字段比较 -->
            <n-select
              v-if="cond.value_type === 'quote_field'"
              v-model:value="cond.value_field"
              :options="quoteFieldOptions"
              size="small"
              style="width: 120px;"
            />
          </n-space>
        </n-card>
      </n-space>
    </n-card>

    <!-- 组合逻辑 -->
    <n-card title="条件组合" size="small">
      <n-radio-group v-model:value="logic">
        <n-radio value="AND">全部满足 (AND)</n-radio>
        <n-radio value="OR">任一满足 (OR)</n-radio>
      </n-radio-group>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  fetchIndicators,
  type IndicatorItem,
  type StrategyCondition,
  type StrategyConfig
} from '@/api/stockPick'

const message = useMessage()

// Props
const props = defineProps<{
  modelValue?: StrategyConfig
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: StrategyConfig): void
}>()

// 指标库
const availableIndicators = ref<IndicatorItem[]>([])
const selectedIndicators = ref<string[]>([])
const indicatorParams = ref<Record<string, Record<string, any>>>({})
const indicatorOutputs = ref<Record<string, string>>({})

// 条件
const conditions = ref<StrategyCondition[]>([])
const logic = ref<'AND' | 'OR'>('AND')

// 选项
const conditionTypeOptions = [
  { label: '指标', value: 'indicator' },
  { label: '行情', value: 'quote' },
]

const operatorOptions = [
  { label: '>', value: '>' },
  { label: '<', value: '<' },
  { label: '>=', value: '>=' },
  { label: '<=', value: '<=' },
  { label: '=', value: '==' },
  { label: '!=', value: '!=' },
]

const valueTypeOptions = [
  { label: '数值', value: 'number' },
  { label: '指标', value: 'indicator' },
  { label: '行情', value: 'quote_field' },
]

const quoteFieldOptions = [
  { label: '当前价', value: 'lastPrice' },
  { label: '涨跌幅%', value: 'changePercent' },
  { label: '成交量', value: 'volume' },
  { label: '成交额', value: 'amount' },
  { label: '换手率%', value: 'turnoverRate' },
  { label: '量比', value: 'volumeRatio' },
]

// 计算已选指标详情
const selectedIndicatorDetails = computed(() => {
  return availableIndicators.value.filter(ind => selectedIndicators.value.includes(ind.indicator_key))
})

// 获取指标输出字段
function getIndicatorOutputFields(indicatorKey: string) {
  const ind = availableIndicators.value.find(i => i.indicator_key === indicatorKey)
  return ind?.output_fields || [{ key: 'values', name: '值' }]
}

// 加载指标库
async function loadIndicators() {
  try {
    availableIndicators.value = await fetchIndicators()
  } catch (e: any) {
    message.error(e.message || '加载指标库失败')
  }
}

// 切换指标选择
function toggleIndicator(key: string) {
  const index = selectedIndicators.value.indexOf(key)
  if (index >= 0) {
    selectedIndicators.value.splice(index, 1)
    delete indicatorParams.value[key]
    delete indicatorOutputs.value[key]
  } else {
    selectedIndicators.value.push(key)
    // 初始化参数
    const ind = availableIndicators.value.find(i => i.indicator_key === key)
    if (ind?.params) {
      indicatorParams.value[key] = {}
      for (const p of ind.params) {
        if (p.default !== undefined) {
          indicatorParams.value[key][p.key] = p.default
        }
      }
    }
    // 初始化输出字段
    if (ind?.default_output) {
      indicatorOutputs.value[key] = ind.default_output
    } else if (ind?.output_fields && ind.output_fields.length > 0) {
      indicatorOutputs.value[key] = ind.output_fields[0].key
    }
  }
}

// 移除指标
function removeIndicator(key: string) {
  const index = selectedIndicators.value.indexOf(key)
  if (index >= 0) {
    selectedIndicators.value.splice(index, 1)
    delete indicatorParams.value[key]
    delete indicatorOutputs.value[key]
  }
}

// 添加条件
function addCondition() {
  const cond: StrategyCondition = {
    id: `cond_${Date.now()}`,
    type: 'indicator',
    indicator_key: selectedIndicatorDetails.value[0]?.indicator_key || '',
    output_field: 'values',
    operator: '>',
    value_type: 'number',
    value: 0,
  }
  conditions.value.push(cond)
}

// 移除条件
function removeCondition(id: string) {
  const index = conditions.value.findIndex(c => c.id === id)
  if (index >= 0) {
    conditions.value.splice(index, 1)
  }
}

// 条件类型改变
function onConditionTypeChange(cond: StrategyCondition) {
  if (cond.type === 'indicator') {
    cond.indicator_key = selectedIndicatorDetails.value[0]?.indicator_key || ''
    cond.output_field = 'values'
  } else if (cond.type === 'quote') {
    cond.field = 'lastPrice'
  }
}

// 条件指标改变
function onConditionIndicatorChange(cond: StrategyCondition) {
  const fields = getIndicatorOutputFields(cond.indicator_key || '')
  if (fields.length > 0) {
    cond.output_field = fields[0].key
  }
}

// 输出配置
function outputConfig(): StrategyConfig {
  return {
    indicators: selectedIndicatorDetails.value.map(ind => ({
      indicator_key: ind.indicator_key,
      params: indicatorParams.value[ind.indicator_key] || {},
      output_field: indicatorOutputs.value[ind.indicator_key] || 'values',
    })),
    conditions: conditions.value,
    logic: logic.value,
  }
}

// 监听变化，输出配置
watch(
  [selectedIndicators, indicatorParams, indicatorOutputs, conditions, logic],
  () => {
    emit('update:modelValue', outputConfig())
  },
  { deep: true }
)

// 初始化
onMounted(() => {
  loadIndicators()

  // 加载已有配置
  if (props.modelValue) {
    const config = props.modelValue
    logic.value = config.logic || 'AND'
    conditions.value = config.conditions || []

    // 恢复已选指标
    if (config.indicators) {
      for (const ind of config.indicators) {
        selectedIndicators.value.push(ind.indicator_key)
        if (ind.params) {
          indicatorParams.value[ind.indicator_key] = ind.params
        }
        if (ind.output_field) {
          indicatorOutputs.value[ind.indicator_key] = ind.output_field
        }
      }
    }
  }
})

// 暴露方法
defineExpose({
  getConfig: outputConfig
})
</script>

<style scoped>
.strategy-config-editor {
  padding: 8px;
}
</style>