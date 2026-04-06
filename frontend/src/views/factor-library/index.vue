<template>
  <div class="factor-library-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>因子库管理</h2>
      <div class="header-actions">
        <n-button type="primary" @click="syncFromQMT" :loading="syncing">
          <template #icon>
            <n-icon><CloudDownloadOutline /></n-icon>
          </template>
          从QMT同步
        </n-button>
        <n-button @click="initFactors" :loading="initializing">
          初始化预置因子
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
        placeholder="搜索因子名称/ID"
        clearable
        style="width: 200px"
      />
      <n-tag type="info" size="medium">
        共 {{ filteredFactors.length }} 个因子
      </n-tag>
    </div>

    <!-- 因子列表 -->
    <div class="factor-list">
      <n-spin :show="loading">
        <div class="category-section" v-for="cat in groupedFactors" :key="cat.category">
          <div class="category-header">
            <span class="category-name">{{ cat.categoryName }}</span>
            <span class="category-desc">{{ cat.categoryDesc }}</span>
            <n-tag size="small">{{ cat.factors.length }} 个</n-tag>
          </div>

          <div class="factor-cards">
            <div
              class="factor-card"
              v-for="factor in cat.factors"
              :key="factor.factor_id"
              :class="{ disabled: !factor.is_active }"
            >
              <div class="card-header">
                <span class="factor-id">{{ factor.factor_id }}</span>
                <n-switch
                  size="small"
                  :value="factor.is_active"
                  @update:value="toggleFactorStatus(factor, $event)"
                />
              </div>
              <div class="factor-name">{{ factor.factor_name }}</div>
              <div class="factor-desc">{{ factor.description }}</div>
              <div class="card-footer">
                <n-tag :type="getCategoryTag(factor.category)" size="small">
                  {{ getCategoryLabel(factor.category) }}
                </n-tag>
                <span class="factor-unit" v-if="factor.unit">{{ factor.unit }}</span>
              </div>
            </div>
          </div>
        </div>

        <n-empty v-if="!loading && filteredFactors.length === 0" description="暂无因子数据，请点击「从QMT同步」或「初始化预置因子」" />
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NButton, NIcon, NSelect, NInput, NSpin, NTag, NEmpty, NSwitch, useMessage } from 'naive-ui'
import { CloudDownloadOutline } from '@vicons/ionicons5'
import request from '@/utils/request'

const message = useMessage()

// 数据
const factors = ref<any[]>([])
const loading = ref(false)
const syncing = ref(false)
const initializing = ref(false)

// 筛选
const filterCategory = ref<string | null>(null)
const filterKeyword = ref('')

// 分类选项
const categoryOptions = [
  { label: '趋势因子', value: 'trend' },
  { label: '动量因子', value: 'momentum' },
  { label: '波动因子', value: 'volatility' },
  { label: '成交量因子', value: 'volume' },
  { label: '价值因子', value: 'value' },
  { label: '成长因子', value: 'growth' },
  { label: '质量因子', value: 'quality' },
  { label: '情绪因子', value: 'sentiment' },
  { label: '自定义因子', value: 'custom' }
]

const categoryInfo: Record<string, { name: string; desc: string }> = {
  trend: { name: '趋势因子', desc: '均线、趋势类指标' },
  momentum: { name: '动量因子', desc: 'RSI、KDJ、动量等' },
  volatility: { name: '波动因子', desc: 'ATR、波动率等' },
  volume: { name: '成交量因子', desc: '量比、换手率等' },
  value: { name: '价值因子', desc: 'PE、PB、PS等' },
  growth: { name: '成长因子', desc: '营收增长、利润增长等' },
  quality: { name: '质量因子', desc: 'ROE、ROA、毛利率等' },
  sentiment: { name: '情绪因子', desc: '成交额、振幅等' },
  custom: { name: '自定义因子', desc: '用户自定义因子' }
}

// 筛选后的因子
const filteredFactors = computed(() => {
  let result = factors.value

  if (filterCategory.value) {
    result = result.filter(f => f.category === filterCategory.value)
  }

  if (filterKeyword.value) {
    const keyword = filterKeyword.value.toLowerCase()
    result = result.filter(f =>
      f.factor_name.toLowerCase().includes(keyword) ||
      f.factor_id.toLowerCase().includes(keyword)
    )
  }

  return result
})

// 按分类分组
const groupedFactors = computed(() => {
  const groups: Record<string, any[]> = {}

  for (const factor of filteredFactors.value) {
    if (!groups[factor.category]) {
      groups[factor.category] = []
    }
    groups[factor.category].push(factor)
  }

  return Object.entries(groups).map(([category, factors]) => ({
    category,
    categoryName: categoryInfo[category]?.name || category,
    categoryDesc: categoryInfo[category]?.desc || '',
    factors
  }))
})

// 获取分类标签
function getCategoryTag(category: string): 'default' | 'info' | 'success' | 'warning' | 'error' {
  const map: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
    trend: 'info',
    momentum: 'success',
    volatility: 'warning',
    volume: 'error',
    value: 'info',
    growth: 'success',
    quality: 'warning',
    sentiment: 'default',
    custom: 'default'
  }
  return map[category] || 'default'
}

function getCategoryLabel(category: string): string {
  return categoryInfo[category]?.name || category
}

// 切换因子状态
async function toggleFactorStatus(factor: any, active: boolean) {
  try {
    await request.put(`/factor-screen/factors/${factor.factor_id}`, {
      is_active: active
    })
    factor.is_active = active
    message.success(active ? '已启用' : '已禁用')
  } catch (error) {
    message.error('操作失败')
  }
}

// 从QMT同步
async function syncFromQMT() {
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

// 初始化预置因子
async function initFactors() {
  initializing.value = true
  try {
    const res: any = await request.post('/factor-screen/init')
    message.success(res.message || '初始化成功')
    loadFactors()
  } catch (error) {
    message.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

// 加载因子列表
async function loadFactors() {
  loading.value = true
  try {
    const res: any = await request.get('/factor-screen/factors')
    factors.value = res || []
  } catch (error) {
    console.error('加载因子失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadFactors()
})
</script>

<style scoped lang="scss">
.factor-library-page {
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
  align-items: center;
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

.factor-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 15px;
}

.factor-card {
  background: rgba(20, 40, 80, 0.6);
  border: 1px solid rgba(100, 150, 255, 0.2);
  border-radius: 8px;
  padding: 15px;
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

    .factor-id {
      font-family: monospace;
      color: #00ffcc;
      font-size: 13px;
    }
  }

  .factor-name {
    font-size: 16px;
    font-weight: 500;
    color: #fff;
    margin-bottom: 8px;
  }

  .factor-desc {
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

    .factor-unit {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.5);
    }
  }
}
</style>