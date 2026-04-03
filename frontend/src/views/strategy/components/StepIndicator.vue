<template>
  <div class="step-indicator">
    <!-- 已添加的指标列表 -->
    <div v-if="wizard.indicators.length > 0" class="indicator-list mb-4">
      <div
        v-for="(indicator, index) in wizard.indicators"
        :key="index"
        class="indicator-item flex-between p-3 bg-gray-50 rounded mb-2"
      >
        <div class="indicator-info">
          <span class="font-medium">{{ getIndicatorLabel(indicator.indicator_type) }}</span>
          <span class="text-sm text-gray-500 ml-2">{{ formatParameters(indicator.parameters) }}</span>
        </div>
        <n-button size="small" type="error" text @click="wizard.removeIndicator(index)">
          <template #icon>
            <n-icon><CloseOutline /></n-icon>
          </template>
        </n-button>
      </div>
    </div>

    <!-- 添加指标表单 -->
    <n-card title="添加技术指标" size="small">
      <n-form :model="newIndicator" label-placement="left" label-width="80">
        <n-form-item label="指标类型">
          <n-select
            v-model:value="newIndicator.indicator_type"
            :options="INDICATOR_TYPES"
            placeholder="选择指标类型"
            @update:value="handleTypeChange"
          />
        </n-form-item>

        <!-- MA参数 -->
        <template v-if="newIndicator.indicator_type === 'MA'">
          <n-form-item label="周期">
            <n-input-number v-model:value="newIndicator.parameters.period" :min="1" :max="500" />
          </n-form-item>
          <n-form-item label="类型">
            <n-radio-group v-model:value="newIndicator.parameters.type">
              <n-radio-button value="SMA" label="简单均线" />
              <n-radio-button value="EMA" label="指数均线" />
            </n-radio-group>
          </n-form-item>
        </template>

        <!-- MACD参数 -->
        <template v-if="newIndicator.indicator_type === 'MACD'">
          <n-form-item label="快线周期">
            <n-input-number v-model:value="newIndicator.parameters.fast_period" :min="1" />
          </n-form-item>
          <n-form-item label="慢线周期">
            <n-input-number v-model:value="newIndicator.parameters.slow_period" :min="1" />
          </n-form-item>
          <n-form-item label="信号线周期">
            <n-input-number v-model:value="newIndicator.parameters.signal_period" :min="1" />
          </n-form-item>
        </template>

        <!-- RSI参数 -->
        <template v-if="newIndicator.indicator_type === 'RSI'">
          <n-form-item label="周期">
            <n-input-number v-model:value="newIndicator.parameters.period" :min="1" />
          </n-form-item>
        </template>

        <!-- KDJ参数 -->
        <template v-if="newIndicator.indicator_type === 'KDJ'">
          <n-form-item label="N周期">
            <n-input-number v-model:value="newIndicator.parameters.n" :min="1" />
          </n-form-item>
          <n-form-item label="M1周期">
            <n-input-number v-model:value="newIndicator.parameters.m1" :min="1" />
          </n-form-item>
          <n-form-item label="M2周期">
            <n-input-number v-model:value="newIndicator.parameters.m2" :min="1" />
          </n-form-item>
        </template>

        <!-- BOLL参数 -->
        <template v-if="newIndicator.indicator_type === 'BOLL'">
          <n-form-item label="周期">
            <n-input-number v-model:value="newIndicator.parameters.period" :min="1" />
          </n-form-item>
          <n-form-item label="标准差倍数">
            <n-input-number v-model:value="newIndicator.parameters.std_dev" :min="0.1" :step="0.1" />
          </n-form-item>
        </template>

        <n-form-item>
          <n-button type="primary" @click="handleAddIndicator">
            添加指标
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  NCard, NForm, NFormItem, NSelect, NInputNumber, NRadioGroup, NRadioButton, NButton, NIcon
} from 'naive-ui'
import { CloseOutline } from '@vicons/ionicons5'
import { useWizardStore } from '@/stores/wizard'
import { INDICATOR_TYPES } from '@/types/strategy'
import type { Indicator } from '@/types/strategy'

const wizard = useWizardStore()

const newIndicator = ref<Indicator>({
  indicator_type: 'MA',
  parameters: {
    period: 20,
    type: 'EMA'
  }
})

const defaultParameters: Record<string, any> = {
  MA: { period: 20, type: 'EMA' },
  MACD: { fast_period: 12, slow_period: 26, signal_period: 9 },
  RSI: { period: 14 },
  KDJ: { n: 9, m1: 3, m2: 3 },
  BOLL: { period: 20, std_dev: 2 }
}

function handleTypeChange(value: string) {
  newIndicator.value.parameters = { ...defaultParameters[value] }
}

function handleAddIndicator() {
  wizard.addIndicator({
    indicator_type: newIndicator.value.indicator_type,
    parameters: { ...newIndicator.value.parameters }
  })
}

function getIndicatorLabel(type: string): string {
  const item = INDICATOR_TYPES.find(i => i.value === type)
  return item?.label || type
}

function formatParameters(params: Record<string, any>): string {
  return Object.entries(params)
    .map(([key, value]) => `${key}=${value}`)
    .join(', ')
}
</script>

<style scoped lang="scss">
.indicator-item {
  border: 1px solid #e5e7eb;
}
</style>