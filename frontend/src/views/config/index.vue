<template>
  <div class="config-page">
    <n-card title="系统配置">
      <n-tabs v-model:value="activeCategory" type="line" @update:value="loadConfigs">
        <n-tab-pane name="basic" tab="基础配置" />
        <n-tab-pane name="security" tab="安全认证配置" />
        <n-tab-pane name="notification" tab="通知渠道配置" />
        <n-tab-pane name="ai" tab="AI服务配置" />
      </n-tabs>

      <div class="toolbar">
        <n-space>
          <n-input
            v-model:value="keyword"
            placeholder="搜索配置键/描述"
            clearable
            style="width: 200px"
            @keyup.enter="loadConfigs"
          />
          <n-button type="primary" @click="openModal()">
            新增配置
          </n-button>
        </n-space>
      </div>

      <n-data-table
        :columns="columns"
        :data="configList"
        :loading="loading"
        :row-key="(row: SysConfig) => row.id"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="modalVisible" preset="dialog" title="编辑配置" style="width: 500px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="80">
        <n-form-item label="配置键" path="key">
          <n-input v-model:value="form.key" placeholder="请输入配置键" :disabled="!!form.id" />
        </n-form-item>
        <n-form-item label="配置值" path="value">
          <n-input v-model:value="form.value" type="textarea" placeholder="请输入配置值" :rows="3" />
        </n-form-item>
        <n-form-item label="类别" path="category">
          <n-select v-model:value="form.category" :options="categoryOptions" />
        </n-form-item>
        <n-form-item label="数据类型" path="data_type">
          <n-select v-model:value="form.data_type" :options="dataTypeOptions" />
        </n-form-item>
        <n-form-item label="访问类型" path="access_type">
          <n-select v-model:value="form.access_type" :options="accessTypeOptions" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="form.description" type="textarea" placeholder="请输入描述" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" :loading="submitLoading" @click="submit">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { NButton, NTag, NSpace, useMessage, type DataTableColumns, type FormInst, type FormRules } from 'naive-ui'
import type { SysConfig, SysConfigCreateParams } from '@/types/config'
import * as configApi from '@/api/config'
import { useAuthStore } from '@/stores/auth'

const message = useMessage()
const authStore = useAuthStore()

const activeCategory = ref<'basic' | 'security' | 'notification' | 'ai'>('basic')
const loading = ref(false)
const configList = ref<SysConfig[]>([])
const keyword = ref('')
const modalVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInst | null>(null)
const form = reactive<SysConfigCreateParams & { id?: number }>({
  key: '',
  value: '',
  category: 'basic',
  data_type: 'plain',
  access_type: 'public',
  description: ''
})

const rules: FormRules = {
  key: [{ required: true, message: '请输入配置键' }],
  value: [{ required: true, message: '请输入配置值' }]
}

const categoryOptions = [
  { label: '基础配置', value: 'basic' },
  { label: '安全认证', value: 'security' },
  { label: '通知渠道', value: 'notification' },
  { label: 'AI服务', value: 'ai' }
]

const dataTypeOptions = [
  { label: '明文', value: 'plain' },
  { label: '加密', value: 'encrypted' }
]

const accessTypeOptions = [
  { label: '公开', value: 'public' },
  { label: '私有', value: 'private' }
]

const columns: DataTableColumns<SysConfig> = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '配置键', key: 'key', width: 200 },
  {
    title: '配置值',
    key: 'value',
    width: 200,
    ellipsis: { tooltip: true },
    render: (row) => {
      if (!row.value) return '-'
      if (row.data_type === 'encrypted') return '******'
      return row.value
    }
  },
  {
    title: '数据类型',
    key: 'data_type',
    width: 100,
    render: (row) => h(NTag, { type: row.data_type === 'encrypted' ? 'warning' : 'default' }, () => row.data_type === 'encrypted' ? '加密' : '明文')
  },
  {
    title: '访问类型',
    key: 'access_type',
    width: 100,
    render: (row) => h(NTag, { type: row.access_type === 'private' ? 'warning' : 'default' }, () => row.access_type === 'private' ? '私有' : '公开')
  },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row) => {
      return h(NSpace, {}, () => [
        h(NButton, { size: 'small', onClick: () => openModal(row) }, () => '编辑'),
        h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row.key) }, () => '删除')
      ])
    }
  }
]

async function loadConfigs() {
  loading.value = true
  try {
    const res = await configApi.getConfigsByCategory(activeCategory.value)
    configList.value = res
  } finally {
    loading.value = false
  }
}

function openModal(row?: SysConfig) {
  if (row) {
    form.id = row.id
    form.key = row.key
    form.value = row.decrypted_value || row.value || ''
    form.category = row.category
    form.data_type = row.data_type
    form.access_type = row.access_type
    form.description = row.description || ''
  } else {
    form.id = undefined
    form.key = ''
    form.value = ''
    form.category = activeCategory.value
    form.data_type = 'plain'
    form.access_type = 'public'
    form.description = ''
  }
  modalVisible.value = true
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitLoading.value = true
  try {
    if (form.id) {
      await configApi.updateConfig(form.key, form)
      message.success('更新成功')
    } else {
      await configApi.createConfig(form)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadConfigs()
  } catch (e: any) {
    message.error(e.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(key: string) {
  try {
    await configApi.deleteConfig(key)
    message.success('删除成功')
    loadConfigs()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped lang="scss">
.config-page {
  padding: 16px;

  .toolbar {
    margin: 16px 0;
  }
}
</style>