<template>
  <div class="red-line-page">
    <n-card title="交易红线管理">
      <template #header-extra>
        <n-space>
          <n-switch
            v-model:value="switchEnabled"
            :loading="switchLoading"
            @update:value="handleSwitchChange"
          >
            <template #checked>已开启</template>
            <template #unchecked>已关闭</template>
          </n-switch>
          <n-button type="primary" @click="handleInit" :loading="initLoading">
            初始化预置规则
          </n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="redLines"
        :loading="loading"
        :row-key="(row: RedLine) => row.rule_key"
        striped
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NSwitch, NTag, NSpace, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  getRedLines,
  getRedLineSwitch,
  setRedLineSwitch,
  batchUpdateRedLineStatus,
  initPresetRedLines,
  type RedLine
} from '@/api/redLine'

const message = useMessage()
const loading = ref(false)
const switchLoading = ref(false)
const initLoading = ref(false)
const switchEnabled = ref(true)
const redLines = ref<RedLine[]>([])

const severityMap: Record<string, { type: 'error' | 'warning' | 'info'; label: string }> = {
  critical: { type: 'error', label: '严重' },
  warning: { type: 'warning', label: '警告' },
  info: { type: 'info', label: '提示' }
}

const columns: DataTableColumns<RedLine> = [
  {
    title: '规则KEY',
    key: 'rule_key',
    width: 150
  },
  {
    title: '规则名称',
    key: 'rule_name',
    width: 150
  },
  {
    title: '规则类型',
    key: 'rule_type',
    width: 100
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: { tooltip: true }
  },
  {
    title: '严重级别',
    key: 'severity',
    width: 100,
    render: (row) => {
      const config = severityMap[row.severity] || severityMap.info
      return h(NTag, { type: config.type, size: 'small' }, { default: () => config.label })
    }
  },
  {
    title: '状态',
    key: 'is_enabled',
    width: 80,
    render: (row) => h(NSwitch, {
      value: row.is_enabled,
      onUpdateValue: (val: boolean) => handleToggleRule(row.rule_key, val)
    })
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(NButton, {
      size: 'small',
      onClick: () => handleViewDetail(row)
    }, { default: () => '查看' })
  }
]

async function loadData() {
  loading.value = true
  try {
    const [rulesRes, switchRes] = await Promise.all([
      getRedLines(),
      getRedLineSwitch()
    ])
    redLines.value = rulesRes.rules
    switchEnabled.value = switchRes.enabled
  } catch (e: any) {
    message.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function handleSwitchChange(val: boolean) {
  switchLoading.value = true
  try {
    await setRedLineSwitch(val)
    message.success(val ? '红线已开启' : '红线已关闭')
  } catch (e: any) {
    message.error(e.message || '操作失败')
    switchEnabled.value = !val
  } finally {
    switchLoading.value = false
  }
}

async function handleToggleRule(ruleKey: string, enabled: boolean) {
  try {
    await batchUpdateRedLineStatus([ruleKey], enabled)
    const rule = redLines.value.find(r => r.rule_key === ruleKey)
    if (rule) rule.is_enabled = enabled
    message.success(enabled ? '已启用' : '已禁用')
  } catch (e: any) {
    message.error(e.message || '操作失败')
  }
}

async function handleInit() {
  initLoading.value = true
  try {
    const res = await initPresetRedLines()
    message.success(`初始化完成，新增 ${res.synced} 条，共 ${res.total} 条`)
    await loadData()
  } catch (e: any) {
    message.error(e.message || '初始化失败')
  } finally {
    initLoading.value = false
  }
}

function handleViewDetail(row: RedLine) {
  message.info(`查看规则: ${row.rule_name}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.red-line-page {
  padding: 16px;
}
</style>