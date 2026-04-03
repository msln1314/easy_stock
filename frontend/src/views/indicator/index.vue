<template>
  <div class="indicator-config-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>指标库管理</h2>
      <div class="header-actions">
        <n-button type="primary" @click="showAddModal = true">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          添加指标
        </n-button>
        <n-button @click="initIndicators" :loading="initializing">
          初始化预置指标
        </n-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <n-select
        v-model:value="filterCategory"
        :options="categoryOptions"
        placeholder="选择分类"
        clearable
        style="width: 150px"
      />
      <n-input
        v-model:value="filterKeyword"
        placeholder="搜索指标名称/KEY"
        clearable
        style="width: 200px"
      />
    </div>

    <!-- 指标列表 -->
    <div class="indicator-list">
      <n-spin :show="loading">
        <div class="category-section" v-for="cat in groupedIndicators" :key="cat.category">
          <div class="category-header">
            <span class="category-name">{{ cat.categoryName }}</span>
            <span class="category-desc">{{ cat.categoryDesc }}</span>
            <n-tag size="small">{{ cat.indicators.length }} 个指标</n-tag>
          </div>

          <div class="indicator-cards">
            <div
              class="indicator-card"
              v-for="indicator in cat.indicators"
              :key="indicator.id"
              :class="{ disabled: !indicator.is_enabled }"
              @click="showIndicatorDetail(indicator)"
            >
              <div class="card-header">
                <span class="indicator-key">{{ indicator.indicator_key }}</span>
                <n-tag
                  :type="indicator.is_builtin ? 'info' : 'success'"
                  size="small"
                >
                  {{ indicator.is_builtin ? '内置' : '自定义' }}
                </n-tag>
              </div>
              <div class="indicator-name">{{ indicator.indicator_name }}</div>
              <div class="indicator-desc">{{ indicator.description }}</div>
              <div class="card-footer">
                <n-tag :type="getValueTypeTag(indicator.value_type)" size="small">
                  {{ getValueTypeLabel(indicator.value_type) }}
                </n-tag>
                <span class="params-count">
                  {{ indicator.params?.length || 0 }} 个参数
                </span>
              </div>
            </div>
          </div>
        </div>

        <n-empty v-if="!loading && filteredIndicators.length === 0" description="暂无指标数据" />
      </n-spin>
    </div>

    <!-- 指标详情弹窗 -->
    <n-modal v-model:show="showDetailModal" preset="card" :title="currentIndicator?.indicator_name" style="width: 700px">
      <template v-if="currentIndicator">
        <n-descriptions label-placement="left" :column="2">
          <n-descriptions-item label="指标KEY">
            <n-tag type="primary">{{ currentIndicator.indicator_key }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="分类">
            {{ currentIndicator.category_name }}
          </n-descriptions-item>
          <n-descriptions-item label="值类型">
            {{ getValueTypeLabel(currentIndicator.value_type) }}
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-switch
              :value="currentIndicator.is_enabled"
              @update:value="(val) => toggleIndicator(val)"
            />
          </n-descriptions-item>
        </n-descriptions>

        <n-divider>指标说明</n-divider>
        <p class="detail-desc">{{ currentIndicator.description }}</p>

        <n-divider>参数配置</n-divider>
        <n-data-table
          :columns="paramsColumns"
          :data="currentIndicator.params || []"
          size="small"
          v-if="currentIndicator.params?.length"
        />
        <n-empty v-else description="无参数" size="small" />

        <n-divider>输出字段</n-divider>
        <n-data-table
          :columns="outputColumns"
          :data="currentIndicator.output_fields || []"
          size="small"
          v-if="currentIndicator.output_fields?.length"
        />
        <n-empty v-else description="无输出定义" size="small" />

        <template v-if="currentIndicator.usage_guide">
          <n-divider>使用说明</n-divider>
          <p class="usage-guide">{{ currentIndicator.usage_guide }}</p>
        </template>

        <template v-if="currentIndicator.signal_interpretation">
          <n-divider>信号解读</n-divider>
          <div class="signal-list">
            <div
              class="signal-item"
              v-for="(desc, key) in currentIndicator.signal_interpretation"
              :key="key"
            >
              <n-tag size="small">{{ key }}</n-tag>
              <span>{{ desc }}</span>
            </div>
          </div>
        </template>
      </template>

      <template #footer>
        <div class="modal-footer">
          <n-button
            v-if="!currentIndicator?.is_builtin"
            type="error"
            @click="deleteCurrentIndicator"
          >
            删除
          </n-button>
          <n-button @click="showDetailModal = false">关闭</n-button>
        </div>
      </template>
    </n-modal>

    <!-- 添加指标弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="添加自定义指标" style="width: 600px">
      <n-form ref="addFormRef" :model="addForm" label-placement="left" label-width="100">
        <n-form-item label="指标KEY" required>
          <n-input v-model:value="addForm.indicator_key" placeholder="如：CUSTOM_MA" />
        </n-form-item>
        <n-form-item label="指标名称" required>
          <n-input v-model:value="addForm.indicator_name" placeholder="如：自定义均线" />
        </n-form-item>
        <n-form-item label="分类" required>
          <n-select v-model:value="addForm.category" :options="categoryOptions" />
        </n-form-item>
        <n-form-item label="值类型">
          <n-select
            v-model:value="addForm.value_type"
            :options="valueTypeOptions"
          />
        </n-form-item>
        <n-form-item label="描述">
          <n-input
            v-model:value="addForm.description"
            type="textarea"
            placeholder="指标说明"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-button @click="showAddModal = false">取消</n-button>
        <n-button type="primary" @click="addIndicator">确定</n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton, NIcon, NSelect, NInput, NSpin, NTag, NModal, NDescriptions,
  NDescriptionsItem, NDivider, NDataTable, NEmpty, NSwitch, NForm,
  NFormItem, useMessage
} from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import request from '@/utils/request'

const message = useMessage()

// 数据
const indicators = ref<any[]>([])
const loading = ref(false)
const initializing = ref(false)

// 筛选
const filterCategory = ref<string | null>(null)
const filterKeyword = ref('')

// 弹窗
const showDetailModal = ref(false)
const showAddModal = ref(false)
const currentIndicator = ref<any>(null)

// 添加表单
const addFormRef = ref()
const addForm = ref({
  indicator_key: '',
  indicator_name: '',
  category: 'trend',
  value_type: 'single',
  description: ''
})

// 分类选项
const categoryOptions = [
  { label: '趋势类', value: 'trend' },
  { label: '动量类', value: 'momentum' },
  { label: '震荡类', value: 'oscillator' },
  { label: '成交量类', value: 'volume' },
  { label: '波动率类', value: 'volatility' }
]

const categoryInfo: Record<string, { name: string; desc: string }> = {
  trend: { name: '趋势类', desc: '用于判断趋势方向' },
  momentum: { name: '动量类', desc: '用于判断动量强弱' },
  oscillator: { name: '震荡类', desc: '用于判断超买超卖' },
  volume: { name: '成交量类', desc: '用于分析成交量变化' },
  volatility: { name: '波动率类', desc: '用于测量波动程度' }
}

const valueTypeOptions = [
  { label: '单值', value: 'single' },
  { label: '多值', value: 'multi' },
  { label: '序列', value: 'series' }
]

// 筛选后的指标
const filteredIndicators = computed(() => {
  let result = indicators.value

  if (filterCategory.value) {
    result = result.filter(i => i.category === filterCategory.value)
  }

  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase()
    result = result.filter(i =>
      i.indicator_name.toLowerCase().includes(keyword) ||
      i.indicator_key.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 按分类分组
const groupedIndicators = computed(() => {
  const groups: Record<string, any[]> = {}

  for (const indicator of filteredIndicators.value) {
    if (!groups[indicator.category]) {
      groups[indicator.category] = []
    }
    groups[indicator.category].push(indicator)
  }

  return Object.entries(groups).map(([category, indicators]) => ({
    category,
    categoryName: categoryInfo[category]?.name || category,
    categoryDesc: categoryInfo[category]?.desc || '',
    indicators
  }))
})

// 参数表格列
const paramsColumns = [
  { title: '参数KEY', key: 'key' },
  { title: '参数名', key: 'name' },
  { title: '类型', key: 'type' },
  { title: '默认值', key: 'default' },
  { title: '范围', key: 'range', render: (row: any) => row.min && row.max ? `${row.min} ~ ${row.max}` : '-' }
]

// 输出字段表格列
const outputColumns = [
  { title: '字段KEY', key: 'key' },
  { title: '字段名', key: 'name' },
  { title: '类型', key: 'type' },
  { title: '说明', key: 'desc' }
]

// 获取值类型标签
function getValueTypeTag(type: string): 'default' | 'info' | 'success' | 'warning' | 'error' {
  const map: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
    single: 'info',
    multi: 'success',
    series: 'warning'
  }
  return map[type] || 'default'
}

function getValueTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    single: '单值',
    multi: '多值',
    series: '序列'
  }
  return labels[type] || type
}

// 显示指标详情
function showIndicatorDetail(indicator: any) {
  currentIndicator.value = indicator
  showDetailModal.value = true
}

// 切换指标状态
async function toggleIndicator(enabled: boolean) {
  if (!currentIndicator.value) return

  try {
    await request.put(`/api/indicators/${currentIndicator.value.id}`, {
      is_enabled: enabled
    })
    currentIndicator.value.is_enabled = enabled
    message.success(enabled ? '已启用' : '已禁用')
  } catch (error) {
    message.error('操作失败')
  }
}

// 删除指标
async function deleteCurrentIndicator() {
  if (!currentIndicator.value) return

  try {
    await request.delete(`/api/indicators/${currentIndicator.value.id}`)
    message.success('删除成功')
    showDetailModal.value = false
    loadIndicators()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '删除失败')
  }
}

// 初始化预置指标
async function initIndicators() {
  initializing.value = true
  try {
    const res = await request.post('/api/indicators/init')
    message.success(res.message || '初始化成功')
    loadIndicators()
  } catch (error) {
    message.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

// 添加指标
async function addIndicator() {
  try {
    await request.post('/api/indicators', addForm.value)
    message.success('添加成功')
    showAddModal.value = false
    addForm.value = {
      indicator_key: '',
      indicator_name: '',
      category: 'trend',
      value_type: 'single',
      description: ''
    }
    loadIndicators()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '添加失败')
  }
}

// 加载指标列表
async function loadIndicators() {
  loading.value = true
  try {
    const res = await request.get('/api/indicators')
    indicators.value = res.data || []
  } catch (error) {
    console.error('加载指标失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadIndicators()
})
</script>

<style scoped lang="scss">
.indicator-config-page {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
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

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.category-section {
  margin-bottom: 30px;

  .category-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);

    .category-name {
      font-size: 18px;
      font-weight: 500;
      color: #00aaff;
    }

    .category-desc {
      color: rgba(255, 255, 255, 0.6);
      font-size: 13px;
    }
  }
}

.indicator-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.indicator-card {
  background: rgba(20, 40, 80, 0.6);
  border: 1px solid rgba(100, 150, 255, 0.2);
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(100, 150, 255, 0.5);
    background: rgba(30, 50, 100, 0.6);
  }

  &.disabled {
    opacity: 0.5;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .indicator-key {
      font-family: monospace;
      color: #00ffcc;
      font-size: 13px;
    }
  }

  .indicator-name {
    font-size: 16px;
    font-weight: 500;
    color: #fff;
    margin-bottom: 8px;
  }

  .indicator-desc {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 10px;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .params-count {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.5);
    }
  }
}

.detail-desc,
.usage-guide {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  line-height: 1.6;
}

.signal-list {
  .signal-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(100, 150, 255, 0.1);

    &:last-child {
      border-bottom: none;
    }

    span {
      color: rgba(255, 255, 255, 0.8);
      font-size: 13px;
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>