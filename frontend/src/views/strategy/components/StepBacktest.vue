<template>
  <div class="step-backtest">
    <n-alert type="info" class="mb-4">
      <template #header>回测验证</template>
      回测功能将在 Phase 2 版本中完整实现，当前版本仅保存策略配置，暂不支持实际回测。
    </n-alert>

    <!-- 回测参数设置 -->
    <n-form label-placement="left" label-width="100">
      <n-form-item label="回测区间">
        <n-date-picker
          v-model:value="backtestRange"
          type="daterange"
          :default-value="[Date.now() - 90 * 24 * 60 * 60 * 1000, Date.now()]"
          clearable
        />
      </n-form-item>

      <n-form-item label="初始资金">
        <n-input-number
          v-model:value="initialCapital"
          :min="1000"
          :step="1000"
          placeholder="初始资金"
        >
          <template #prefix>¥</template>
        </n-input-number>
      </n-form-item>
    </n-form>

    <!-- 预留回测按钮 -->
    <n-button type="primary" disabled class="mt-4">
      运行回测 (Phase 2)
    </n-button>

    <!-- 策略摘要 -->
    <n-card title="策略摘要" size="small" class="mt-4">
      <n-descriptions label-placement="left" :column="2">
        <n-descriptions-item label="策略名称">
          {{ wizard.basicInfo.name || '未设置' }}
        </n-descriptions-item>
        <n-descriptions-item label="执行模式">
          {{ getModeLabel(wizard.basicInfo.execute_mode) }}
        </n-descriptions-item>
        <n-descriptions-item label="技术指标">
          {{ wizard.indicators.length }} 个
        </n-descriptions-item>
        <n-descriptions-item label="交易信号">
          {{ wizard.signals.length }} 条
        </n-descriptions-item>
        <n-descriptions-item label="止盈设置">
          {{ wizard.risk.stop_profit_value ? `${wizard.risk.stop_profit_value}%` : '未设置' }}
        </n-descriptions-item>
        <n-descriptions-item label="止损设置">
          {{ wizard.risk.stop_loss_value ? `${wizard.risk.stop_loss_value}%` : '未设置' }}
        </n-descriptions-item>
      </n-descriptions>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  NForm, NFormItem, NDatePicker, NInputNumber, NButton, NCard, NDescriptions, NDescriptionsItem, NAlert
} from 'naive-ui'
import { useWizardStore } from '@/stores/wizard'
import { EXECUTE_MODE_OPTIONS } from '@/types/strategy'

const wizard = useWizardStore()

const backtestRange = ref<[number, number] | null>(null)
const initialCapital = ref(100000)

function getModeLabel(value: string): string {
  const item = EXECUTE_MODE_OPTIONS.find(m => m.value === value)
  return item?.label || value
}
</script>