<template>
  <div class="strategy-config-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>卖出策略配置</h2>
        <n-space>
          <n-button type="primary" @click="showAddModal = true">
            <template #icon>
              <n-icon><AddOutline /></n-icon>
            </template>
            新建策略
          </n-button>
          <n-button @click="loadStrategies" :loading="loading">
            <template #icon>
              <n-icon><RefreshOutline /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </div>
    </div>

    <!-- 策略列表 -->
    <div class="strategy-panel">
      <n-spin :show="loading">
        <div class="strategy-grid">
          <div class="strategy-card" v-for="strategy in strategies" :key="strategy.id">
            <div class="card-header">
              <div class="strategy-name">{{ strategy.name }}</div>
              <n-switch v-model:value="strategy.is_enabled" @update:value="(val) => toggleStrategy(strategy, val)" />
            </div>
            <div class="card-body">
              <div class="strategy-desc">{{ strategy.description || '暂无描述' }}</div>
              <div class="strategy-conditions">
                <div class="condition-label">触发条件：</div>
                <div class="condition-tags">
                  <n-tag v-for="cond in strategy.conditions" :key="cond" size="small" type="info" style="margin-right: 4px;">
                    {{ getConditionName(cond) }}
                  </n-tag>
                  <span v-if="!strategy.conditions?.length" class="no-data">全部条件</span>
                </div>
              </div>
              <div class="strategy-meta">
                <span>优先级: </span>
                <n-tag :type="getPriorityType(strategy.priority)" size="small">
                  {{ getPriorityLabel(strategy.priority) }}
                </n-tag>
                <span style="margin-left: 12px;">动作: </span>
                <n-tag type="warning" size="small">{{ strategy.action }}</n-tag>
              </div>
            </div>
            <div class="card-footer">
              <n-space>
                <n-button size="small" @click="editStrategy(strategy)">编辑</n-button>
                <n-button size="small" type="error" @click="deleteStrategy(strategy)">删除</n-button>
              </n-space>
            </div>
          </div>
        </div>
        <n-empty v-if="!loading && strategies.length === 0" description="暂无卖出策略" class="py-8" />
      </n-spin>
    </div>

    <!-- 新建/编辑策略弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" :title="editingStrategy ? '编辑策略' : '新建策略'" style="width: 600px">
      <n-form ref="formRef" :model="strategyForm" label-placement="left" label-width="100">
        <n-form-item label="策略名称" required>
          <n-input v-model:value="strategyForm.name" placeholder="请输入策略名称" />
        </n-form-item>
        <n-form-item label="策略描述">
          <n-input v-model:value="strategyForm.description" type="textarea" placeholder="请输入策略描述" :rows="3" />
        </n-form-item>
        <n-form-item label="优先级">
          <n-radio-group v-model:value="strategyForm.priority">
            <n-radio-button value="critical">严重</n-radio-button>
            <n-radio-button value="warning">警告</n-radio-button>
            <n-radio-button value="info">提示</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="触发条件">
          <n-checkbox-group v-model:value="strategyForm.conditions">
            <n-space>
              <n-checkbox
                v-for="cond in conditions"
                :key="cond.condition_key"
                :value="cond.condition_key"
                :label="cond.condition_name"
              />
            </n-space>
          </n-checkbox-group>
          <div class="form-tip">不选择则表示触发任意条件时执行</div>
        </n-form-item>
        <n-form-item label="执行动作">
          <n-radio-group v-model:value="strategyForm.action">
            <n-radio-button value="SELL">卖出</n-radio-button>
            <n-radio-button value="WATCH">关注</n-radio-button>
            <n-radio-button value="IGNORE">忽略</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="启用状态">
          <n-switch v-model:value="strategyForm.is_enabled" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="saveStrategy" :loading="saving">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NButton, NIcon, NSpin, NTag, NModal, NEmpty, NSpace, NSwitch,
  NForm, NFormItem, NInput, NCheckboxGroup, NCheckbox, NRadioButton, NRadioGroup, useMessage
} from 'naive-ui'
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { fetchWarningConditions, type WarningCondition } from '@/api/warning'

const message = useMessage()

// 策略类型
interface SellStrategy {
  id?: number
  name: string
  description: string
  priority: 'critical' | 'warning' | 'info'
  conditions: string[]
  action: 'SELL' | 'WATCH' | 'IGNORE'
  is_enabled: boolean
}

// 数据
const strategies = ref<SellStrategy[]>([])
const conditions = ref<WarningCondition[]>([])
const loading = ref(false)
const saving = ref(false)

// 弹窗
const showAddModal = ref(false)
const editingStrategy = ref<SellStrategy | null>(null)

// 表单
const formRef = ref()
const strategyForm = ref<SellStrategy>({
  name: '',
  description: '',
  priority: 'warning',
  conditions: [],
  action: 'SELL',
  is_enabled: true
})

// 模拟数据 - 实际项目中应该从API获取
const mockStrategies: SellStrategy[] = [
  {
    id: 1,
    name: '严重预警自动卖出',
    description: '当触发严重级别预警时，自动标记为卖出',
    priority: 'critical',
    conditions: [],
    action: 'SELL',
    is_enabled: true
  },
  {
    id: 2,
    name: 'MA死叉关注',
    description: 'MA死叉时标记为关注，需要人工确认',
    priority: 'warning',
    conditions: ['MA_DEAD_CROSS_DAILY', 'MA_DEAD_CROSS_60'],
    action: 'WATCH',
    is_enabled: true
  },
  {
    id: 3,
    name: 'RSI超买忽略',
    description: 'RSI超买信号仅作为参考，自动忽略',
    priority: 'info',
    conditions: ['RSI_OVERBOUGHT'],
    action: 'IGNORE',
    is_enabled: false
  }
]

// 辅助函数
function getPriorityType(priority: string): 'error' | 'warning' | 'info' {
  if (priority === 'critical') return 'error'
  if (priority === 'warning') return 'warning'
  return 'info'
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '提示'
  }
  return labels[priority] || priority
}

function getConditionName(key: string): string {
  const cond = conditions.value.find(c => c.condition_key === key)
  return cond?.condition_name || key
}

// 加载策略
async function loadStrategies() {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    strategies.value = mockStrategies
  } catch (error) {
    console.error('加载策略失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载预警条件
async function loadConditions() {
  try {
    conditions.value = await fetchWarningConditions()
  } catch (error) {
    console.error('加载预警条件失败:', error)
  }
}

// 切换策略启用状态
async function toggleStrategy(strategy: SellStrategy, enabled: boolean) {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))
    message.success(enabled ? '已启用' : '已禁用')
  } catch (error) {
    message.error('操作失败')
    strategy.is_enabled = !enabled // 回滚
  }
}

// 编辑策略
function editStrategy(strategy: SellStrategy) {
  editingStrategy.value = strategy
  strategyForm.value = { ...strategy }
  showAddModal.value = true
}

// 删除策略
async function deleteStrategy(strategy: SellStrategy) {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 300))
    const index = strategies.value.findIndex(s => s.id === strategy.id)
    if (index !== -1) {
      strategies.value.splice(index, 1)
    }
    message.success('删除成功')
  } catch (error) {
    message.error('删除失败')
  }
}

// 保存策略
async function saveStrategy() {
  if (!strategyForm.value.name) {
    message.warning('请输入策略名称')
    return
  }

  saving.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))

    if (editingStrategy.value) {
      // 更新
      Object.assign(editingStrategy.value, strategyForm.value)
      message.success('更新成功')
    } else {
      // 新建
      strategies.value.push({
        ...strategyForm.value,
        id: Date.now()
      })
      message.success('创建成功')
    }

    showAddModal.value = false
    editingStrategy.value = null
    strategyForm.value = {
      name: '',
      description: '',
      priority: 'warning',
      conditions: [],
      action: 'SELL',
      is_enabled: true
    }
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadStrategies()
  loadConditions()
})
</script>

<style scoped lang="scss">
.strategy-config-page {
  padding: 16px;
  height: calc(100vh - 50px - 32px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }
}

.strategy-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  flex: 1;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.strategy-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #eee;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;

    .strategy-name {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .card-body {
    .strategy-desc {
      font-size: 13px;
      color: #666;
      margin-bottom: 12px;
    }

    .strategy-conditions {
      margin-bottom: 12px;

      .condition-label {
        font-size: 13px;
        color: #999;
        margin-bottom: 6px;
      }

      .condition-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
      }

      .no-data {
        font-size: 12px;
        color: #999;
      }
    }

    .strategy-meta {
      font-size: 13px;
      color: #666;
    }
  }

  .card-footer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #eee;
  }
}

.py-8 {
  padding-top: 32px;
  padding-bottom: 32px;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>