<template>
  <div class="step-basic">
    <n-form ref="formRef" :model="wizard.basicInfo" label-placement="left" label-width="100">
      <n-form-item label="策略名称" path="name" :rule="{ required: true, message: '请输入策略名称' }">
        <n-input
          v-model:value="wizard.basicInfo.name"
          placeholder="请输入策略名称"
          maxlength="100"
          show-count
        />
      </n-form-item>

      <n-form-item label="策略描述" path="description">
        <n-input
          v-model:value="wizard.basicInfo.description"
          type="textarea"
          placeholder="请输入策略描述（可选）"
          maxlength="500"
          show-count
          :autosize="{ minRows: 3, maxRows: 5 }"
        />
      </n-form-item>

      <n-form-item label="执行模式" path="execute_mode">
        <n-radio-group v-model:value="wizard.basicInfo.execute_mode">
          <n-space>
            <n-radio-button
              v-for="mode in EXECUTE_MODE_OPTIONS"
              :key="mode.value"
              :value="mode.value"
              :label="mode.label"
            />
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-form-item label="初始状态" path="status">
        <n-radio-group v-model:value="wizard.basicInfo.status">
          <n-space>
            <n-radio-button
              v-for="status in STATUS_OPTIONS"
              :key="status.value"
              :value="status.value"
              :label="status.label"
            />
          </n-space>
        </n-radio-group>
      </n-form-item>
    </n-form>

    <!-- 执行模式说明 -->
    <n-alert type="info" class="mt-4">
      <template #header>执行模式说明</template>
      <ul class="mode-desc-list">
        <li><strong>自动交易</strong>：系统自动执行买卖操作，需要对接券商API</li>
        <li><strong>信号提醒</strong>：推送通知给用户，由用户手动决策执行</li>
        <li><strong>模拟运行</strong>：虚拟环境测试，不执行真实交易</li>
      </ul>
    </n-alert>
  </div>
</template>

<script setup lang="ts">
import { NForm, NFormItem, NInput, NRadioGroup, NRadioButton, NSpace, NAlert } from 'naive-ui'
import { useWizardStore } from '@/stores/wizard'
import { EXECUTE_MODE_OPTIONS, STATUS_OPTIONS } from '@/types/strategy'

const wizard = useWizardStore()
</script>

<style scoped lang="scss">
.mode-desc-list {
  padding-left: 16px;
  margin: 0;

  li {
    margin-bottom: 4px;
  }
}
</style>