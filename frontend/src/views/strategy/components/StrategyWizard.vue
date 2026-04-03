<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="创建策略"
    style="width: 800px"
    :mask-closable="false"
    @close="handleClose"
  >
    <!-- 步骤条 -->
    <n-steps :current="wizard.currentStep" class="mb-6">
      <n-step title="基础信息" description="设置策略名称和执行模式" />
      <n-step title="技术指标" description="配置分析指标" />
      <n-step title="买卖信号" description="定义交易规则" />
      <n-step title="止盈止损" description="设置风险控制" />
      <n-step title="回测验证" description="验证策略效果" />
    </n-steps>

    <!-- 步骤内容 -->
    <div class="step-content">
      <StepBasic v-if="wizard.currentStep === 1" />
      <StepIndicator v-if="wizard.currentStep === 2" />
      <StepSignal v-if="wizard.currentStep === 3" />
      <StepRisk v-if="wizard.currentStep === 4" />
      <StepBacktest v-if="wizard.currentStep === 5" />
    </div>

    <!-- 底部操作按钮 -->
    <div class="step-actions flex-between mt-6">
      <n-button v-if="wizard.currentStep > 1" @click="wizard.prevStep">
        上一步
      </n-button>
      <span v-else></span>
      <div class="flex gap-2">
        <n-button @click="handleClose">取消</n-button>
        <n-button v-if="wizard.currentStep < 5" type="primary" @click="handleNext">
          下一步
        </n-button>
        <n-button v-else type="primary" :loading="submitting" @click="handleSubmit">
          提交创建
        </n-button>
      </div>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NSteps, NStep, NButton, useMessage } from 'naive-ui'
import { useWizardStore } from '@/stores/wizard'
import { createStrategy } from '@/api/strategy'
import StepBasic from './StepBasic.vue'
import StepIndicator from './StepIndicator.vue'
import StepSignal from './StepSignal.vue'
import StepRisk from './StepRisk.vue'
import StepBacktest from './StepBacktest.vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  success: []
}>()

const wizard = useWizardStore()
const message = useMessage()
const submitting = ref(false)

const showModal = ref(props.show)

watch(() => props.show, (val) => {
  showModal.value = val
  if (val) {
    wizard.reset()
  }
})

watch(showModal, (val) => {
  emit('update:show', val)
})

function handleClose() {
  showModal.value = false
  wizard.reset()
}

function handleNext() {
  // 步骤验证
  if (wizard.currentStep === 1) {
    if (!wizard.basicInfo.name) {
      message.warning('请输入策略名称')
      return
    }
  }
  wizard.nextStep()
}

async function handleSubmit() {
  submitting.value = true
  try {
    const data = wizard.getSubmitData()
    await createStrategy(data)
    emit('success')
    handleClose()
  } catch (error) {
    message.error('创建失败，请检查表单数据')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped lang="scss">
.step-content {
  min-height: 300px;
}

.step-actions {
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}
</style>