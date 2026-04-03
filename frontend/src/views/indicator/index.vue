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
    <IndicatorDetailModal
      v-model:show="showDetailModal"
      :indicator="currentIndicator"
      @updated="loadIndicators"
    />

    <!-- 添加指标弹窗 -->
    <IndicatorAddModal
      v-model:show="showAddModal"
      @success="loadIndicators"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NButton, NIcon, NSelect, NInput, NSpin, NTag, NEmpty, useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import request from '@/utils/request'
import IndicatorDetailModal from './components/IndicatorDetailModal.vue'
import IndicatorAddModal from './components/IndicatorAddModal.vue'

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

// 初始化预置指标
async function initIndicators() {
  initializing.value = true
  try {
    const res: any = await request.post('/indicators/init')
    message.success(res.message || '初始化成功')
    loadIndicators()
  } catch (error) {
    message.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

// 加载指标列表
async function loadIndicators() {
  loading.value = true
  try {
    const res: any = await request.get('/indicators')
    indicators.value = res || []
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
</style>