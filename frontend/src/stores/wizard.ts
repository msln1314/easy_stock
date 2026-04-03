/**
 * 向导表单状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Indicator, Signal, RiskConfig, CreateStrategyRequest } from '@/types/strategy'

export const useWizardStore = defineStore('wizard', () => {
  // 当前步骤
  const currentStep = ref(1)

  // 基础信息 (Step1)
  const basicInfo = ref({
    name: '',
    description: '',
    execute_mode: 'simulate',
    status: 'paused'
  })

  // 技术指标 (Step2)
  const indicators = ref<Indicator[]>([])

  // 买卖信号 (Step3)
  const signals = ref<Signal[]>([])

  // 止盈止损 (Step4)
  const risk = ref<RiskConfig>({
    stop_profit_type: 'fixed_percent',
    stop_profit_value: 10,
    stop_loss_type: 'fixed_percent',
    stop_loss_value: 5,
    max_position: 80
  })

  // 是否编辑模式
  const isEdit = ref(false)
  const editId = ref<number | null>(null)

  // 重置表单
  function reset() {
    currentStep.value = 1
    basicInfo.value = {
      name: '',
      description: '',
      execute_mode: 'simulate',
      status: 'paused'
    }
    indicators.value = []
    signals.value = []
    risk.value = {
      stop_profit_type: 'fixed_percent',
      stop_profit_value: 10,
      stop_loss_type: 'fixed_percent',
      stop_loss_value: 5,
      max_position: 80
    }
    isEdit.value = false
    editId.value = null
  }

  // 下一步
  function nextStep() {
    if (currentStep.value < 5) {
      currentStep.value++
    }
  }

  // 上一步
  function prevStep() {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  // 设置步骤
  function setStep(step: number) {
    currentStep.value = step
  }

  // 添加指标
  function addIndicator(indicator: Indicator) {
    indicators.value.push(indicator)
  }

  // 删除指标
  function removeIndicator(index: number) {
    indicators.value.splice(index, 1)
  }

  // 添加信号
  function addSignal(signal: Signal) {
    signals.value.push(signal)
  }

  // 删除信号
  function removeSignal(index: number) {
    signals.value.splice(index, 1)
  }

  // 获取提交数据
  function getSubmitData(): CreateStrategyRequest {
    return {
      name: basicInfo.value.name,
      description: basicInfo.value.description,
      execute_mode: basicInfo.value.execute_mode,
      status: basicInfo.value.status,
      indicators: indicators.value,
      signals: signals.value,
      risk: risk.value
    }
  }

  return {
    currentStep,
    basicInfo,
    indicators,
    signals,
    risk,
    isEdit,
    editId,
    reset,
    nextStep,
    prevStep,
    setStep,
    addIndicator,
    removeIndicator,
    addSignal,
    removeSignal,
    getSubmitData
  }
})