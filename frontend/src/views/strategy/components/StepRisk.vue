<template>
  <div class="step-risk">
    <n-form :model="wizard.risk" label-placement="left" label-width="100">
      <!-- 止盈设置 -->
      <n-divider>止盈设置</n-divider>

      <n-form-item label="止盈类型">
        <n-radio-group v-model:value="wizard.risk.stop_profit_type">
          <n-space>
            <n-radio-button
              v-for="type in STOP_PROFIT_TYPE_OPTIONS"
              :key="type.value"
              :value="type.value"
              :label="type.label"
            />
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-form-item v-if="wizard.risk.stop_profit_type === 'fixed_percent'" label="止盈值">
        <n-input-number
          v-model:value="wizard.risk.stop_profit_value"
          :min="0"
          :max="100"
          placeholder="止盈百分比"
        >
          <template #suffix>%</template>
        </n-input-number>
      </n-form-item>

      <!-- 止损设置 -->
      <n-divider>止损设置</n-divider>

      <n-form-item label="止损类型">
        <n-radio-group v-model:value="wizard.risk.stop_loss_type">
          <n-space>
            <n-radio-button
              v-for="type in STOP_LOSS_TYPE_OPTIONS"
              :key="type.value"
              :value="type.value"
              :label="type.label"
            />
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-form-item v-if="wizard.risk.stop_loss_type === 'fixed_percent'" label="止损值">
        <n-input-number
          v-model:value="wizard.risk.stop_loss_value"
          :min="0"
          :max="100"
          placeholder="止损百分比"
        >
          <template #suffix>%</template>
        </n-input-number>
      </n-form-item>

      <!-- 仓位控制 -->
      <n-divider>仓位控制</n-divider>

      <n-form-item label="最大仓位">
        <n-input-number
          v-model:value="wizard.risk.max_position"
          :min="0"
          :max="100"
          placeholder="最大仓位比例"
        >
          <template #suffix>%</template>
        </n-input-number>
      </n-form-item>
    </n-form>

    <!-- 风控说明 -->
    <n-alert type="warning" class="mt-4">
      <template #header>风险提示</template>
      合理设置止盈止损可以有效控制风险，建议止损值不超过本金的10%，止盈值根据策略预期收益设定。
    </n-alert>
  </div>
</template>

<script setup lang="ts">
import {
  NForm, NFormItem, NInputNumber, NRadioGroup, NRadioButton, NSpace, NDivider, NAlert
} from 'naive-ui'
import { useWizardStore } from '@/stores/wizard'
import { STOP_PROFIT_TYPE_OPTIONS, STOP_LOSS_TYPE_OPTIONS } from '@/types/strategy'

const wizard = useWizardStore()
</script>

<style scoped lang="scss">
.n-divider {
  margin: 16px 0;
}
</style>