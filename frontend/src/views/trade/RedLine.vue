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

    <!-- 编辑规则弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" title="编辑规则配置" style="width: 700px;">
      <template v-if="editingRule">
        <n-descriptions label-placement="left" :column="1" bordered size="small" style="margin-bottom: 16px;">
          <n-descriptions-item label="规则KEY">{{ editingRule.rule_key }}</n-descriptions-item>
          <n-descriptions-item label="规则名称">{{ editingRule.rule_name }}</n-descriptions-item>
          <n-descriptions-item label="规则类型">{{ editingRule.rule_type }}</n-descriptions-item>
          <n-descriptions-item label="描述">{{ editingRule.description }}</n-descriptions-item>
        </n-descriptions>

        <n-divider>规则配置</n-divider>

        <!-- 仓位限制配置 -->
        <template v-if="editingRule.rule_type === 'position_limit'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="单只股票仓位上限">
              <n-input-number v-model:value="editForm.max_single_position_pct" :min="0" :max="100" :precision="2" style="width: 200px">
                <template #suffix>%</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="总仓位上限">
              <n-input-number v-model:value="editForm.max_total_position_pct" :min="0" :max="100" :precision="2" style="width: 200px">
                <template #suffix>%</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </template>

        <!-- 金额限制配置 -->
        <template v-else-if="editingRule.rule_type === 'amount_limit'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="单笔金额上限">
              <n-input-number v-model:value="editForm.max_single_amount" :min="0" :precision="0" style="width: 200px">
                <template #suffix>元</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="日累计买入上限">
              <n-input-number v-model:value="editForm.max_daily_buy_amount" :min="0" :precision="0" style="width: 200px">
                <template #suffix>元</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </template>

        <!-- 价格限制配置 -->
        <template v-else-if="editingRule.rule_type === 'price_limit'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="最低价格">
              <n-input-number v-model:value="editForm.min_price" :min="0" :precision="2" style="width: 200px">
                <template #suffix>元</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="最低价格原因">
              <n-input v-model:value="editForm.min_price_reason" placeholder="如: 低价股风险大" style="width: 300px" />
            </n-form-item>
            <n-form-item label="最高价格">
              <n-input-number v-model:value="editForm.max_price" :min="0" :precision="2" style="width: 200px">
                <template #suffix>元</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="最高价格原因">
              <n-input v-model:value="editForm.max_price_reason" placeholder="如: 高价股波动大" style="width: 300px" />
            </n-form-item>
            <n-form-item label="避免涨停买入">
              <n-switch v-model:value="editForm.avoid_limit_up" />
            </n-form-item>
            <n-form-item label="涨停阈值" v-if="editForm.avoid_limit_up">
              <n-input-number v-model:value="editForm.limit_up_threshold_pct" :min="0" :max="20" :precision="1" style="width: 200px">
                <template #suffix>%</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </template>

        <!-- 时间限制配置 -->
        <template v-else-if="editingRule.rule_type === 'time_limit'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="开盘后回避分钟">
              <n-input-number v-model:value="editForm.avoid_first_minutes" :min="0" :max="60" style="width: 200px">
                <template #suffix>分钟</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="收盘前回避分钟">
              <n-input-number v-model:value="editForm.avoid_last_minutes" :min="0" :max="60" style="width: 200px">
                <template #suffix>分钟</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="允许的交易时段">
              <n-checkbox-group v-model:value="editForm.allowed_sessions">
                <n-space>
                  <n-checkbox value="morning" label="上午盘" />
                  <n-checkbox value="afternoon" label="下午盘" />
                </n-space>
              </n-checkbox-group>
            </n-form-item>
          </n-form>
        </template>

        <!-- 频率限制配置 -->
        <template v-else-if="editingRule.rule_type === 'frequency_limit'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="每日买入次数上限">
              <n-input-number v-model:value="editForm.max_buy_per_day" :min="1" :max="100" style="width: 200px">
                <template #suffix>次</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </template>

        <!-- 股票黑名单配置 -->
        <template v-else-if="editingRule.rule_type === 'stock_blacklist'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="新股限制天数">
              <n-input-number v-model:value="editForm.ipo_days" :min="0" :max="365" style="width: 200px">
                <template #suffix>天</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="新股限制原因">
              <n-input v-model:value="editForm.new_stock_reason" placeholder="如: 新股波动大" style="width: 300px" />
            </n-form-item>
          </n-form>
        </template>

        <!-- 风控指标配置 -->
        <template v-else-if="editingRule.rule_type === 'risk_control'">
          <n-form :model="editForm" label-placement="left" label-width="150">
            <n-form-item label="亏损股票加仓限制">
              <n-input-number v-model:value="editForm.max_loss_pct_before_add" :min="-50" :max="0" :precision="2" style="width: 200px">
                <template #suffix>%</template>
              </n-input-number>
              <n-text depth="3" style="margin-left: 8px;">亏损超过此比例禁止加仓</n-text>
            </n-form-item>
          </n-form>
        </template>

        <!-- 其他类型 -->
        <template v-else>
          <n-alert type="info" title="自定义配置">
            <n-input
              v-model:value="editFormRaw"
              type="textarea"
              :rows="6"
              placeholder="请输入JSON格式配置"
            />
          </n-alert>
        </template>

        <n-divider>其他设置</n-divider>
        <n-form :model="editForm" label-placement="left" label-width="150">
          <n-form-item label="严重级别">
            <n-radio-group v-model:value="editingRule.severity">
              <n-radio value="critical">必须通过</n-radio>
              <n-radio value="warning">警告</n-radio>
              <n-radio value="info">提示</n-radio>
            </n-radio-group>
          </n-form-item>
          <n-form-item label="是否启用">
            <n-switch v-model:value="editingRule.is_enabled" />
          </n-form-item>
        </n-form>
      </template>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleSaveEdit" :loading="editLoading">保存</n-button>
        </n-space>
      </template>
    </n-modal>

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
  updateRedLine,
  type RedLine,
  type AuditTestResult
} from '@/api/redLine'

const message = useMessage()
const loading = ref(false)
const switchLoading = ref(false)
const initLoading = ref(false)
const testLoading = ref(false)
const editLoading = ref(false)
const switchEnabled = ref(true)
const redLines = ref<RedLine[]>([])

// 编辑相关
const showEditModal = ref(false)
const editingRule = ref<RedLine | null>(null)
const editForm = ref<Record<string, any>>({})
const editFormRaw = ref('')

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
    width: 120,
    render: (row) => h('div', { style: { display: 'flex', gap: '8px' } }, [
      h(NButton, {
        size: 'small',
        onClick: () => handleEditRule(row)
      }, { default: () => '设置' }),
      h(NButton, {
        size: 'small',
        tertiary: true,
        onClick: () => handleViewConfig(row)
      }, { default: () => '查看' })
    ])
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

function handleEditRule(row: RedLine) {
  editingRule.value = { ...row }
  editForm.value = { ...row.rule_config }
  editFormRaw.value = JSON.stringify(row.rule_config, null, 2)
  showEditModal.value = true
}

function handleViewConfig(row: RedLine) {
  message.info(`规则配置: ${JSON.stringify(row.rule_config, null, 2)}`)
}

async function handleSaveEdit() {
  if (!editingRule.value) return

  editLoading.value = true
  try {
    // 构建更新数据
    const updateData: any = {
      severity: editingRule.value.severity,
      is_enabled: editingRule.value.is_enabled
    }

    // 根据规则类型构建配置
    const ruleType = editingRule.value.rule_type
    if (['position_limit', 'amount_limit', 'price_limit', 'time_limit', 'frequency_limit', 'stock_blacklist', 'risk_control'].includes(ruleType)) {
      updateData.rule_config = { ...editForm.value }
    } else {
      // 其他类型尝试解析JSON
      try {
        updateData.rule_config = JSON.parse(editFormRaw.value)
      } catch {
        message.error('JSON格式错误')
        return
      }
    }

    await updateRedLine(editingRule.value.rule_key, updateData)
    message.success('保存成功')
    showEditModal.value = false
    await loadData()
  } catch (e: any) {
    message.error(e.message || '保存失败')
  } finally {
    editLoading.value = false
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

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.red-line-page {
  padding: 16px;
}
</style>