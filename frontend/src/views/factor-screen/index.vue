<template>
  <div class="factor-screen-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>因子筛选</h2>
      <div class="header-actions">
        <n-button @click="syncFactors" :loading="syncing">
          <template #icon>
            <n-icon><SyncOutline /></n-icon>
          </template>
          从QMT同步因子
        </n-button>
      </div>
    </div>

    <div class="page-content">
      <!-- 左侧：因子选择 -->
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title">选择因子</span>
          <n-input
            v-model:value="searchKeyword"
            placeholder="搜索因子"
            clearable
            size="small"
            style="width: 150px"
          />
        </div>

        <!-- 分类筛选 -->
        <div class="category-filter">
          <n-tag
            v-for="cat in categories"
            :key="cat.key"
            :type="selectedCategory === cat.key ? 'primary' : 'default'"
            :bordered="false"
            round
            size="small"
            class="category-tag"
            @click="selectedCategory = cat.key"
          >
            {{ cat.name }}
          </n-tag>
        </div>

        <!-- 因子列表 -->
        <div class="factor-list">
          <n-spin :show="loadingFactors">
            <div
              v-for="factor in filteredFactors"
              :key="factor.factor_id"
              class="factor-item"
              :class="{ selected: isFactorSelected(factor.factor_id) }"
              @click="toggleFactor(factor)"
            >
              <div class="factor-info">
                <span class="factor-name">{{ factor.factor_name }}</span>
                <span class="factor-id">{{ factor.factor_id }}</span>
              </div>
              <n-tag size="small" :type="getCategoryType(factor.category)">
                {{ getCategoryName(factor.category) }}
              </n-tag>
            </div>
          </n-spin>
        </div>
      </div>

      <!-- 右侧：筛选条件和结果 -->
      <div class="right-panel">
        <!-- 已选因子条件 -->
        <div class="conditions-section">
          <div class="section-header">
            <span class="section-title">筛选条件</span>
            <span class="selected-count">已选 {{ selectedFactors.length }} 个因子</span>
          </div>

          <div class="conditions-list" v-if="selectedFactors.length > 0">
            <div
              v-for="(cond, index) in selectedFactors"
              :key="cond.factor_id"
              class="condition-item"
            >
              <div class="condition-factor">
                <span class="factor-name">{{ cond.factor_name }}</span>
                <n-button text size="tiny" @click="removeFactor(index)">
                  <n-icon><CloseOutline /></n-icon>
                </n-button>
              </div>
              <div class="condition-config">
                <n-select
                  v-model:value="cond.op"
                  :options="opOptions"
                  size="small"
                  style="width: 80px"
                />
                <n-input-number
                  v-model:value="cond.value"
                  size="small"
                  placeholder="值"
                  style="width: 120px"
                />
                <span class="unit">{{ cond.unit || '' }}</span>
              </div>
            </div>
          </div>

          <n-empty v-else description="请从左侧选择因子" size="small" />

          <!-- 执行筛选按钮 -->
          <div class="action-bar" v-if="selectedFactors.length > 0">
            <n-input-number
              v-model:value="resultLimit"
              size="small"
              :min="10"
              :max="500"
              style="width: 100px"
            >
              <template #prefix>返回</template>
              <template #suffix>条</template>
            </n-input-number>
            <n-button type="primary" @click="executeScreen" :loading="screening">
              开始选股
            </n-button>
          </div>
        </div>

        <!-- 选股结果 -->
        <div class="result-section" v-if="screenResult.length > 0">
          <div class="section-header">
            <span class="section-title">选股结果</span>
            <span class="result-count">共 {{ screenResult.length }} 只股票</span>
          </div>

          <n-data-table
            :columns="resultColumns"
            :data="screenResult"
            :max-height="400"
            striped
            size="small"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { NButton, NIcon, NInput, NTag, NSpin, NEmpty, NSelect, NInputNumber, NDataTable, useMessage } from 'naive-ui'
import { SyncOutline, CloseOutline } from '@vicons/ionicons5'
import request from '@/utils/request'

const message = useMessage()

// 因子数据
const factors = ref<any[]>([])
const categories = ref<any[]>([])
const loadingFactors = ref(false)
const syncing = ref(false)
const screening = ref(false)

// 筛选状态
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedFactors = ref<any[]>([])
const resultLimit = ref(50)
const screenResult = ref<any[]>([])

// 操作符选项
const opOptions = [
  { label: '大于', value: 'gt' },
  { label: '小于', value: 'lt' },
  { label: '≥', value: 'ge' },
  { label: '≤', value: 'le' },
  { label: '等于', value: 'eq' }
]

// 结果表格列
const resultColumns = [
  { title: '代码', key: 'stock_code', width: 80 },
  { title: '名称', key: 'stock_name', width: 100 },
  { title: '综合得分', key: 'score', width: 100, sortable: true },
  { title: '因子值', key: 'factor_values', width: 200, render: (row: any) => {
    const values = Object.entries(row.factor_values || {})
      .slice(0, 3)
      .map(([k, v]) => `${k}: ${(v as number).toFixed(2)}`)
      .join(', ')
    return values
  }}
]

// 筛选后的因子列表
const filteredFactors = computed(() => {
  let result = factors.value

  if (selectedCategory.value && selectedCategory.value !== 'all') {
    result = result.filter(f => f.category === selectedCategory.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(f =>
      f.factor_name.toLowerCase().includes(keyword) ||
      f.factor_id.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 获取分类名称
function getCategoryName(category: string): string {
  const cat = categories.value.find(c => c.key === category)
  return cat?.name || category
}

// 获取分类标签类型
function getCategoryType(category: string): 'default' | 'primary' | 'info' | 'success' | 'warning' | 'error' {
  const typeMap: Record<string, 'default' | 'primary' | 'info' | 'success' | 'warning' | 'error'> = {
    trend: 'info',
    momentum: 'success',
    volatility: 'warning',
    volume: 'error',
    value: 'primary',
    growth: 'success',
    quality: 'info',
    sentiment: 'warning',
    custom: 'default'
  }
  return typeMap[category] || 'default'
}

// 判断因子是否已选
function isFactorSelected(factorId: string): boolean {
  return selectedFactors.value.some(f => f.factor_id === factorId)
}

// 切换因子选择
function toggleFactor(factor: any) {
  const index = selectedFactors.value.findIndex(f => f.factor_id === factor.factor_id)
  if (index >= 0) {
    selectedFactors.value.splice(index, 1)
  } else {
    selectedFactors.value.push({
      factor_id: factor.factor_id,
      factor_name: factor.factor_name,
      category: factor.category,
      unit: factor.unit,
      op: 'gt',
      value: 0
    })
  }
}

// 移除因子
function removeFactor(index: number) {
  selectedFactors.value.splice(index, 1)
}

// 同步因子
async function syncFactors() {
  syncing.value = true
  try {
    const res: any = await request.post('/factor-screen/sync')
    message.success(res.message || '同步成功')
    loadFactors()
  } catch (error) {
    message.error('同步失败')
  } finally {
    syncing.value = false
  }
}

// 加载因子列表
async function loadFactors() {
  loadingFactors.value = true
  try {
    const res: any = await request.get('/factor-screen/factors')
    factors.value = res || []
  } catch (error) {
    console.error('加载因子失败:', error)
  } finally {
    loadingFactors.value = false
  }
}

// 加载分类
async function loadCategories() {
  try {
    const res: any = await request.get('/factor-screen/categories')
    categories.value = [
      { key: 'all', name: '全部' },
      ...(res || [])
    ]
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

// 执行选股
async function executeScreen() {
  if (selectedFactors.value.length === 0) {
    message.warning('请至少选择一个因子')
    return
  }

  screening.value = true
  try {
    const conditions = selectedFactors.value.map(f => ({
      factor_id: f.factor_id,
      op: f.op,
      value: f.value
    }))

    const res: any = await request.post('/factor-screen/screen', {
      factors: conditions,
      limit: resultLimit.value
    })

    screenResult.value = res?.stocks || []
    message.success(`筛选完成，共 ${screenResult.value.length} 只股票`)
  } catch (error) {
    message.error('选股失败')
  } finally {
    screening.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadFactors()
})
</script>

<style scoped lang="scss">
.factor-screen-page {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    margin: 0;
    color: #fff;
  }
}

.page-content {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
}

.left-panel {
  width: 320px;
  background: rgba(20, 40, 80, 0.6);
  border: 1px solid rgba(100, 150, 255, 0.2);
  border-radius: 8px;
  display: flex;
  flex-direction: column;

  .panel-header {
    padding: 12px 15px;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;

    .panel-title {
      font-size: 14px;
      font-weight: 500;
      color: #00aaff;
    }
  }

  .category-filter {
    padding: 10px 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);

    .category-tag {
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        opacity: 0.8;
      }
    }
  }

  .factor-list {
    flex: 1;
    overflow-y: auto;
    padding: 10px;

    &::-webkit-scrollbar {
      width: 4px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(100, 150, 255, 0.3);
      border-radius: 2px;
    }
  }

  .factor-item {
    padding: 10px 12px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    &:hover {
      background: rgba(100, 150, 255, 0.15);
    }

    &.selected {
      background: rgba(0, 170, 255, 0.3);
      border: 1px solid rgba(0, 170, 255, 0.5);
    }

    .factor-info {
      display: flex;
      flex-direction: column;
      gap: 2px;

      .factor-name {
        font-size: 13px;
        color: #fff;
      }

      .factor-id {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.5);
        font-family: monospace;
      }
    }
  }
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.conditions-section,
.result-section {
  background: rgba(20, 40, 80, 0.6);
  border: 1px solid rgba(100, 150, 255, 0.2);
  border-radius: 8px;
  padding: 15px;

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    .section-title {
      font-size: 14px;
      font-weight: 500;
      color: #00aaff;
    }

    .selected-count,
    .result-count {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
    }
  }
}

.conditions-section {
  .conditions-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 15px;
  }

  .condition-item {
    background: rgba(0, 100, 200, 0.2);
    border: 1px solid rgba(100, 150, 255, 0.3);
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 200px;

    .condition-factor {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .factor-name {
        font-size: 13px;
        color: #00ffcc;
      }
    }

    .condition-config {
      display: flex;
      align-items: center;
      gap: 8px;

      .unit {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.5);
      }
    }
  }

  .action-bar {
    display: flex;
    align-items: center;
    gap: 15px;
    padding-top: 10px;
    border-top: 1px solid rgba(100, 150, 255, 0.2);
  }
}

.result-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .n-data-table {
    flex: 1;
  }
}

// 表格样式
:deep(.n-data-table) {
  background: transparent;

  .n-data-table-th {
    background: rgba(0, 100, 200, 0.3);
    color: #00aaff;
    font-size: 12px;
  }

  .n-data-table-td {
    background: transparent;
    color: #fff;
    font-size: 12px;
  }
}
</style>