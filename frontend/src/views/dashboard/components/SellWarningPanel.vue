<template>
  <div class="sell-warning-panel">
    <!-- 预警条件配置按钮 -->
    <div class="config-btn">
      <n-button size="small" type="primary" @click="showConfigModal = true">
        <template #icon>
          <n-icon><SettingsOutline /></n-icon>
        </template>
        配置预警条件
      </n-button>
    </div>

    <!-- 预警股票列表 -->
    <div class="warning-list scroll-content">
      <div class="warning-item" v-for="stock in warningStocks" :key="stock.id">
        <div class="stock-info">
          <span class="stock-code">{{ stock.stock_code }}</span>
          <span class="stock-name">{{ stock.stock_name }}</span>
        </div>
        <div class="price-info">
          <span class="current-price" :class="stock.change_percent >= 0 ? 'rise' : 'fall'">
            {{ formatPrice(stock.price) }}
          </span>
          <span class="change-percent" :class="stock.change_percent >= 0 ? 'rise' : 'fall'">
            {{ formatChange(stock.change_percent) }}
          </span>
        </div>
        <div class="warning-condition">
          <n-tag :type="getWarningType(stock.warning_level)" size="small">
            {{ stock.condition_name }}
          </n-tag>
        </div>
        <div class="warning-time">
          {{ formatTime(stock.trigger_time) }}
        </div>
        <div class="warning-actions">
          <n-button text size="small" @click="handleStock(stock, 'WATCH')">关注</n-button>
          <n-button text size="small" @click="handleStock(stock, 'SELL')">卖出</n-button>
          <n-button text size="small" @click="handleStock(stock, 'IGNORE')">忽略</n-button>
        </div>
      </div>
      <div class="empty-tip" v-if="warningStocks.length === 0">
        暂无预警股票
      </div>
    </div>

    <!-- 预警条件配置弹窗 -->
    <n-modal v-model:show="showConfigModal" preset="card" title="预警条件配置" style="width: 700px">
      <div class="config-content">
        <n-spin :show="loadingConditions">
          <div class="condition-groups">
            <!-- 按周期分组显示 -->
            <div class="condition-group" v-for="(conditions, period) in groupedConditions" :key="period">
              <div class="group-title">{{ getPeriodLabel(period) }}</div>
              <div class="condition-list">
                <div class="condition-item" v-for="cond in conditions" :key="cond.id">
                  <n-checkbox
                    :checked="cond.is_enabled"
                    @update:checked="(val) => toggleCondition(cond, val)"
                  >
                    <span class="condition-name">{{ cond.condition_name }}</span>
                    <n-tag
                      :type="getPriorityType(cond.priority)"
                      size="small"
                      :bordered="false"
                    >
                      {{ getPriorityLabel(cond.priority) }}
                    </n-tag>
                  </n-checkbox>
                  <div class="condition-desc">{{ cond.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </n-spin>
      </div>
      <template #footer>
        <div class="modal-footer">
          <n-button @click="showConfigModal = false">关闭</n-button>
          <n-button type="primary" @click="initConditions" :loading="initializing">
            初始化预置条件
          </n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NButton, NIcon, NModal, NCheckbox, NTag, NSpin, useMessage } from 'naive-ui'
import { SettingsOutline } from '@vicons/ionicons5'
import {
  fetchWarningStocks,
  fetchWarningConditions,
  updateWarningCondition,
  handleWarningStock,
  initWarningConditions,
  type WarningStock,
  type WarningCondition
} from '@/api/warning'

const message = useMessage()

// 预警股票数据
const warningStocks = ref<WarningStock[]>([])

// 预警条件数据
const conditions = ref<WarningCondition[]>([])
const loadingConditions = ref(false)
const initializing = ref(false)

// 配置弹窗
const showConfigModal = ref(false)

// 按周期分组的预警条件
const groupedConditions = computed(() => {
  const groups: Record<string, WarningCondition[]> = {}
  for (const cond of conditions.value) {
    if (!groups[cond.period]) {
      groups[cond.period] = []
    }
    groups[cond.period].push(cond)
  }
  return groups
})

// 获取预警级别对应的标签类型
function getWarningType(level: string): 'error' | 'warning' | 'info' {
  if (level === 'critical') return 'error'
  if (level === 'warning') return 'warning'
  return 'info'
}

// 获取优先级对应的标签类型
function getPriorityType(priority: string): 'error' | 'warning' | 'info' | 'success' {
  if (priority === 'critical') return 'error'
  if (priority === 'warning') return 'warning'
  if (priority === 'info') return 'info'
  return 'success'
}

// 获取优先级标签文本
function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    critical: '严重',
    warning: '警告',
    info: '提示'
  }
  return labels[priority] || priority
}

// 获取周期标签
function getPeriodLabel(period: string): string {
  const labels: Record<string, string> = {
    '30min': '30分钟',
    '60min': '60分钟',
    'daily': '日线',
    'weekly': '周线'
  }
  return labels[period] || period
}

// 格式化时间
function formatTime(time: string): string {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 格式化价格
function formatPrice(price: number | null | undefined): string {
  if (price == null) return '--'
  return price.toFixed(2)
}

// 格式化涨跌幅
function formatChange(change: number | null | undefined): string {
  if (change == null) return '--'
  const sign = change >= 0 ? '+' : ''
  return `${sign}${(change * 100).toFixed(2)}%`
}

// 切换预警条件启用状态
async function toggleCondition(condition: WarningCondition, enabled: boolean) {
  try {
    await updateWarningCondition(condition.id, { is_enabled: enabled })
    condition.is_enabled = enabled
    message.success(enabled ? '已启用' : '已禁用')
  } catch (error) {
    message.error('操作失败')
  }
}

// 处理预警股票
async function handleStock(stock: WarningStock, action: 'IGNORE' | 'SELL' | 'WATCH') {
  try {
    await handleWarningStock(stock.id, action)
    // 从列表中移除或更新状态
    const index = warningStocks.value.findIndex(s => s.id === stock.id)
    if (index !== -1) {
      warningStocks.value.splice(index, 1)
    }
    message.success('处理成功')
  } catch (error) {
    message.error('处理失败')
  }
}

// 加载预警股票
async function loadWarningStocks() {
  try {
    const data = await fetchWarningStocks({ handled: false, limit: 50 })
    warningStocks.value = data
  } catch (error) {
    console.error('加载预警股票失败:', error)
  }
}

// 加载预警条件
async function loadConditions() {
  loadingConditions.value = true
  try {
    const data = await fetchWarningConditions()
    conditions.value = data
  } catch (error) {
    console.error('加载预警条件失败:', error)
  } finally {
    loadingConditions.value = false
  }
}

// 初始化预置条件
async function initConditions() {
  initializing.value = true
  try {
    await initWarningConditions()
    message.success('初始化成功')
    await loadConditions()
  } catch (error) {
    message.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

onMounted(() => {
  loadWarningStocks()
  loadConditions()
})
</script>

<style scoped lang="scss">
.sell-warning-panel {
  height: 100%;
  display: flex;
  flex-direction: column;

  .config-btn {
    padding: 5px 10px;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);
  }

  .warning-list {
    flex: 1;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(100, 150, 255, 0.3);
      border-radius: 2px;
    }
  }

  .warning-item {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(100, 150, 255, 0.1);
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;

    .stock-info {
      display: flex;
      gap: 6px;
      min-width: 100px;

      .stock-code {
        color: #00aaff;
      }

      .stock-name {
        color: rgba(255, 255, 255, 0.8);
      }
    }

    .price-info {
      display: flex;
      gap: 6px;
      min-width: 90px;

      .current-price {
        font-weight: 500;
      }

      .change-percent {
        font-size: 11px;
      }
    }

    .warning-condition {
      flex: 1;
    }

    .warning-time {
      color: rgba(255, 255, 255, 0.5);
      font-size: 11px;
      min-width: 40px;
    }

    .warning-actions {
      display: flex;
      gap: 4px;
    }
  }

  .empty-tip {
    padding: 20px;
    text-align: center;
    color: rgba(255, 255, 255, 0.5);
  }

  .rise { color: #00ff88; }
  .fall { color: #ff4466; }
}

.config-content {
  max-height: 500px;
  overflow-y: auto;

  .condition-groups {
    .condition-group {
      margin-bottom: 20px;

      .group-title {
        font-size: 14px;
        font-weight: 500;
        color: #00aaff;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid rgba(100, 150, 255, 0.2);
      }

      .condition-list {
        .condition-item {
          padding: 8px 0;
          border-bottom: 1px solid rgba(100, 150, 255, 0.1);

          .condition-name {
            margin-right: 8px;
          }

          .condition-desc {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 4px;
            padding-left: 24px;
          }
        }
      }
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: space-between;
}
</style>