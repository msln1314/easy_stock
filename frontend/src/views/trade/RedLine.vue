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
          <n-button @click="showTestModal = true">
            测试校验
          </n-button>
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

    <!-- 测试校验弹窗 -->
    <n-modal v-model:show="showTestModal" preset="card" title="测试红线校验" style="width: 600px;">
      <n-form :model="testForm" label-placement="left" label-width="80">
        <n-form-item label="股票代码" required>
          <n-input v-model:value="testForm.stock_code" placeholder="如: 000001" />
        </n-form-item>
        <n-form-item label="委托价格" required>
          <n-input-number v-model:value="testForm.price" :precision="2" :min="0" style="width: 100%" />
        </n-form-item>
        <n-form-item label="委托数量" required>
          <n-input-number v-model:value="testForm.quantity" :min="100" :step="100" style="width: 100%" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showTestModal = false">取消</n-button>
          <n-button type="primary" @click="handleTest" :loading="testLoading">开始测试</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 测试结果弹窗 -->
    <n-modal v-model:show="showResultModal" preset="card" title="校验结果" style="width: 700px;">
      <template v-if="testResult">
        <n-alert :type="testResult.passed ? 'success' : 'error'" :title="testResult.passed ? '校验通过' : '校验未通过'" style="margin-bottom: 16px;">
          <template v-if="!testResult.passed">
            拒绝原因: {{ testResult.reject_reason }}
          </template>
          <template v-else-if="testResult.warning_rules && testResult.warning_rules.length > 0">
            有 {{ testResult.warning_rules.length }} 条警告
          </template>
        </n-alert>

        <n-descriptions label-placement="left" :column="2" bordered size="small">
          <n-descriptions-item label="股票代码">{{ testResult.stock_code }}</n-descriptions-item>
          <n-descriptions-item label="股票名称">{{ testResult.stock_name }}</n-descriptions-item>
          <n-descriptions-item label="委托价格">{{ testResult.price }}</n-descriptions-item>
          <n-descriptions-item label="委托数量">{{ testResult.quantity }}</n-descriptions-item>
          <n-descriptions-item label="委托金额" :span="2">{{ testResult.amount ? testResult.amount.toFixed(2) : '-' }}</n-descriptions-item>
        </n-descriptions>

        <n-divider>未通过规则</n-divider>
        <n-empty v-if="!testResult.failed_rules || testResult.failed_rules.length === 0" description="无" size="small" />
        <n-list v-else bordered size="small">
          <n-list-item v-for="rule in testResult.failed_rules" :key="rule.rule_key">
            <n-thing :title="rule.rule_name">
              <template #description>
                <n-text type="error">{{ rule.reason }}</n-text>
                <n-text v-if="rule.value !== undefined" depth="3" style="margin-left: 8px;">
                  (当前: {{ rule.value }}, 限制: {{ rule.limit }})
                </n-text>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>

        <n-divider>警告规则</n-divider>
        <n-empty v-if="!testResult.warning_rules || testResult.warning_rules.length === 0" description="无" size="small" />
        <n-list v-else bordered size="small">
          <n-list-item v-for="rule in testResult.warning_rules" :key="rule.rule_key">
            <n-thing :title="rule.rule_name">
              <template #description>
                <n-text type="warning">{{ rule.reason }}</n-text>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
      </template>

      <template #footer>
        <n-button @click="showResultModal = false">关闭</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { NButton, NSwitch, NTag, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  getRedLines,
  getRedLineSwitch,
  setRedLineSwitch,
  batchUpdateRedLineStatus,
  initPresetRedLines,
  testRedLineAudit,
  type RedLine,
  type AuditTestResult
} from '@/api/redLine'

const message = useMessage()
const loading = ref(false)
const switchLoading = ref(false)
const initLoading = ref(false)
const testLoading = ref(false)
const switchEnabled = ref(true)
const redLines = ref<RedLine[]>([])

// 测试相关
const showTestModal = ref(false)
const showResultModal = ref(false)
const testForm = ref({
  stock_code: '000001',
  price: 10.5,
  quantity: 1000
})
const testResult = ref<AuditTestResult | null>(null)

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

async function handleTest() {
  if (!testForm.value.stock_code || !testForm.value.price || !testForm.value.quantity) {
    message.warning('请填写完整信息')
    return
  }

  testLoading.value = true
  try {
    testResult.value = await testRedLineAudit({
      stock_code: testForm.value.stock_code,
      price: testForm.value.price,
      quantity: testForm.value.quantity
    })
    showTestModal.value = false
    showResultModal.value = true
  } catch (e: any) {
    message.error(e.message || '测试失败')
  } finally {
    testLoading.value = false
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