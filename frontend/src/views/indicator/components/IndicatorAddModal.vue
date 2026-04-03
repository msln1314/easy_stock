<template>
  <n-modal v-model:show="visible" preset="card" title="添加自定义指标" style="width: 600px">
    <n-form ref="formRef" :model="form" label-placement="left" label-width="100">
      <n-form-item label="指标KEY" required>
        <n-input v-model:value="form.indicator_key" placeholder="如：CUSTOM_MA" />
      </n-form-item>
      <n-form-item label="指标名称" required>
        <n-input v-model:value="form.indicator_name" placeholder="如：自定义均线" />
      </n-form-item>
      <n-form-item label="分类" required>
        <n-select v-model:value="form.category" :options="categoryOptions" />
      </n-form-item>
      <n-form-item label="值类型">
        <n-select
          v-model:value="form.value_type"
          :options="valueTypeOptions"
        />
      </n-form-item>
      <n-form-item label="描述">
        <n-input
          v-model:value="form.description"
          type="textarea"
          placeholder="指标说明"
        />
      </n-form-item>
    </n-form>

    <template #footer>
      <n-button @click="handleCancel">取消</n-button>
      <n-button type="primary" @click="handleSubmit" :loading="submitting">确定</n-button>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { NModal, NForm, NFormItem, NInput, NSelect, NButton, useMessage } from 'naive-ui'
import request from '@/utils/request'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  success: []
}>()

const message = useMessage()
const formRef = ref()
const submitting = ref(false)

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

const form = ref({
  indicator_key: '',
  indicator_name: '',
  category: 'trend',
  value_type: 'single',
  description: ''
})

const categoryOptions = [
  { label: '趋势类', value: 'trend' },
  { label: '动量类', value: 'momentum' },
  { label: '震荡类', value: 'oscillator' },
  { label: '成交量类', value: 'volume' },
  { label: '波动率类', value: 'volatility' }
]

const valueTypeOptions = [
  { label: '单值', value: 'single' },
  { label: '多值', value: 'multi' },
  { label: '序列', value: 'series' }
]

function resetForm() {
  form.value = {
    indicator_key: '',
    indicator_name: '',
    category: 'trend',
    value_type: 'single',
    description: ''
  }
}

function handleCancel() {
  resetForm()
  emit('update:show', false)
}

async function handleSubmit() {
  if (!form.value.indicator_key || !form.value.indicator_name) {
    message.warning('请填写必填项')
    return
  }

  submitting.value = true
  try {
    await request.post('/indicators', form.value)
    message.success('添加成功')
    resetForm()
    emit('update:show', false)
    emit('success')
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}
</script>