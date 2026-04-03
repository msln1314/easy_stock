<template>
  <div class="step-signal">
    <!-- 已添加的信号列表 -->
    <div v-if="wizard.signals.length > 0" class="signal-list mb-4">
      <div
        v-for="(signal, index) in wizard.signals"
        :key="index"
        class="signal-item flex-between p-3 bg-gray-50 rounded mb-2"
      >
        <div class="signal-info">
          <n-tag :type="signal.signal_type === 'buy' ? 'success' : 'error'" size="small">
            {{ signal.signal_type === 'buy' ? '买入' : '卖出' }}
          </n-tag>
          <span class="font-medium ml-2">{{ getConditionLabel(signal.condition_type) }}</span>
          <span class="text-sm text-gray-500 ml-2">{{ formatCondition(signal.condition_config) }}</span>
        </div>
        <n-button size="small" type="error" text @click="wizard.removeSignal(index)">
          <template #icon>
            <n-icon><CloseOutline /></n-icon>
          </template>
        </n-button>
      </div>
    </div>

    <!-- 添加信号表单 -->
    <n-card title="添加交易信号" size="small">
      <n-form :model="newSignal" label-placement="left" label-width="80">
        <n-form-item label="信号类型">
          <n-radio-group v-model:value="newSignal.signal_type">
            <n-radio-button value="buy" label="买入" />
            <n-radio-button value="sell" label="卖出" />
          </n-radio-group>
        </n-form-item>

        <n-form-item label="条件类型">
          <n-select
            v-model:value="newSignal.condition_type"
            :options="conditionTypes"
            placeholder="选择条件类型"
          />
        </n-form-item>

        <!-- 指标交叉条件 -->
        <template v-if="newSignal.condition_type === 'indicator_cross'">
          <n-form-item label="指标1">
            <n-input v-model:value="newSignal.condition_config.indicator1" placeholder="如: MA5" />
          </n-form-item>
          <n-form-item label="指标2">
            <n-input v-model:value="newSignal.condition_config.indicator2" placeholder="如: MA20" />
          </n-form-item>
          <n-form-item label="交叉方向">
            <n-radio-group v-model:value="newSignal.condition_config.direction">
              <n-radio-button value="up" label="向上交叉" />
              <n-radio-button value="down" label="向下交叉" />
            </n-radio-group>
          </n-form-item>
        </template>

        <!-- 阈值触发条件 -->
        <template v-if="newSignal.condition_type === 'threshold'">
          <n-form-item label="指标">
            <n-input v-model:value="newSignal.condition_config.indicator" placeholder="如: RSI" />
          </n-form-item>
          <n-form-item label="阈值">
            <n-input-number v-model:value="newSignal.condition_config.threshold" />
          </n-form-item>
          <n-form-item label="触发条件">
            <n-radio-group v-model:value="newSignal.condition_config.operator">
              <n-radio-button value="above" label="大于" />
              <n-radio-button value="below" label="小于" />
            </n-radio-group>
          </n-form-item>
        </template>

        <n-form-item label="优先级">
          <n-input-number v-model:value="newSignal.priority" :min="0" :max="100" />
        </n-form-item>

        <n-form-item>
          <n-button type="primary" @click="handleAddSignal">
            添加信号
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  NCard, NForm, NFormItem, NSelect, NInput, NInputNumber, NRadioGroup, NRadioButton, NButton, NTag, NIcon
} from 'naive-ui'
import { CloseOutline } from '@vicons/ionicons5'
import { useWizardStore } from '@/stores/wizard'
import type { Signal } from '@/types/strategy'

const wizard = useWizardStore()

const conditionTypes = [
  { label: '指标交叉', value: 'indicator_cross' },
  { label: '阈值触发', value: 'threshold' },
  { label: '自定义', value: 'custom' }
]

const newSignal = ref<Signal>({
  signal_type: 'buy',
  condition_type: 'indicator_cross',
  condition_config: {
    indicator1: '',
    indicator2: '',
    direction: 'up'
  },
  priority: 0
})

function handleAddSignal() {
  wizard.addSignal({
    signal_type: newSignal.value.signal_type,
    condition_type: newSignal.value.condition_type,
    condition_config: { ...newSignal.value.condition_config },
    priority: newSignal.value.priority
  })
}

function getConditionLabel(type: string): string {
  const item = conditionTypes.find(c => c.value === type)
  return item?.label || type
}

function formatCondition(config: Record<string, any>): string {
  return Object.entries(config)
    .filter(([_, value]) => value !== '' && value !== undefined)
    .map(([key, value]) => `${key}=${value}`)
    .join(', ')
}
</script>

<style scoped lang="scss">
.signal-item {
  border: 1px solid #e5e7eb;
}
</style>