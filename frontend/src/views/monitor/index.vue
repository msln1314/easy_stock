<template>
  <div class="monitor-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>监控股票池</h2>
        <n-space>
          <n-button type="primary" @click="showAddModal = true">
            <template #icon>
              <n-icon><AddOutline /></n-icon>
            </template>
            添加股票
          </n-button>
          <n-button type="info" @click="handleCheckAll" :loading="checking">
            <template #icon>
              <n-icon><RefreshOutline /></n-icon>
            </template>
            检测预警
          </n-button>
        </n-space>
      </div>
      <div class="header-right">
        <n-space align="center">
          <n-select
            v-model:value="filterType"
            :options="typeOptions"
            placeholder="监控类型"
            clearable
            size="small"
            style="width: 120px"
          />
          <n-select
            v-model:value="filterActive"
            :options="activeOptions"
            placeholder="启用状态"
            clearable
            size="small"
            style="width: 100px"
          />
        </n-space>
      </div>
    </div>

    <!-- 股票列表 -->
    <div class="stock-panel">
      <n-spin :show="loading">
        <n-data-table
          :columns="stockColumns"
          :data="filteredStocks"
          :row-key="(row: MonitorStock) => row.id"
          striped
          size="small"
        />
        <n-empty v-if="!loading && filteredStocks.length === 0" description="暂无监控股票" class="py-8" />
      </n-spin>
    </div>

    <!-- 添加股票弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="添加监控股票" style="width: 600px">
      <n-form ref="addFormRef" :model="addForm" label-placement="left" label-width="80">
        <n-form-item label="股票代码" required>
          <n-auto-complete
            v-model:value="addForm.stock_code"
            :options="stockSearchOptions"
            :loading="stockSearchLoading"
            placeholder="输入代码或名称搜索，如：000001 或 平安银行"
            @update:value="handleStockSearch"
            @select="handleStockSelect"
            clearable
          />
        </n-form-item>
        <n-form-item label="股票名称">
          <n-input v-model:value="addForm.stock_name" placeholder="如：平安银行" />
        </n-form-item>
        <n-form-item label="监控类型">
          <n-radio-group v-model:value="addForm.monitor_type">
            <n-radio-button value="hold">持仓监控</n-radio-button>
            <n-radio-button value="watch">关注监控</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="预警条件">
          <n-checkbox-group v-model:value="addForm.conditions">
            <n-space>
              <n-checkbox
                v-for="cond in conditions"
                :key="cond.condition_key"
                :value="cond.condition_key"
                :label="cond.condition_name"
              />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="addForm.remark" type="textarea" placeholder="备注信息" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleAddStock" :loading="adding">添加</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 编辑股票弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" title="编辑监控股票" style="width: 600px">
      <n-form ref="editFormRef" :model="editForm" label-placement="left" label-width="80">
        <n-form-item label="股票代码">
          <n-input :value="editForm.stock_code" disabled />
        </n-form-item>
        <n-form-item label="股票名称">
          <n-input v-model:value="editForm.stock_name" />
        </n-form-item>
        <n-form-item label="监控类型">
          <n-radio-group v-model:value="editForm.monitor_type">
            <n-radio-button value="hold">持仓监控</n-radio-button>
            <n-radio-button value="watch">关注监控</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="启用状态">
          <n-switch v-model:value="editForm.is_active" />
        </n-form-item>
        <n-form-item label="预警条件">
          <n-checkbox-group v-model:value="editForm.conditions">
            <n-space>
              <n-checkbox
                v-for="cond in conditions"
                :key="cond.condition_key"
                :value="cond.condition_key"
                :label="cond.condition_name"
              />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="editForm.remark" type="textarea" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleEditStock" :loading="editing">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton, NIcon, NSelect, NInput, NSpin, NTag, NModal, NDataTable, NEmpty,
  NForm, NFormItem, NCheckboxGroup, NCheckbox, NSpace, NSwitch, NRadioButton,
  NRadioGroup, NAutoComplete, useMessage
} from 'naive-ui'
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import {
  fetchMonitorStocks, addMonitorStock, updateMonitorStock, deleteMonitorStock,
  checkSingleStock, checkAllStocks, fetchAvailableConditions, searchStocks,
  MonitorStock, WarningConditionOption
} from '@/api/monitor'

const message = useMessage()

// 数据
const stocks = ref<MonitorStock[]>([])
const conditions = ref<WarningConditionOption[]>([])
const loading = ref(false)
const adding = ref(false)
const editing = ref(false)
const checking = ref(false)

// 筛选
const filterType = ref<string | null>(null)
const filterActive = ref<boolean | null>(null)

// 弹窗
const showAddModal = ref(false)
const showEditModal = ref(false)

// 表单
const addFormRef = ref()
const addForm = ref({
  stock_code: '',
  stock_name: '',
  monitor_type: 'hold',
  conditions: [] as string[],
  remark: ''
})

// 股票搜索
const stockSearchLoading = ref(false)
const stockSearchOptions = ref<{label: string, value: string}[]>([])

async function handleStockSearch(query: string) {
  if (!query || query.length < 1) {
    stockSearchOptions.value = []
    return
  }

  stockSearchLoading.value = true
  try {
    const results = await searchStocks(query)
    stockSearchOptions.value = results.map(s => ({
      label: `${s.stock_code} ${s.stock_name}`,
      value: s.stock_code
    }))
  } catch (e) {
    stockSearchOptions.value = []
  } finally {
    stockSearchLoading.value = false
  }
}

function handleStockSelect(value: string) {
  // 从选项中找到对应的股票名称
  const option = stockSearchOptions.value.find(o => o.value === value)
  if (option) {
    addForm.value.stock_code = value
    addForm.value.stock_name = option.label.split(' ').slice(1).join(' ')
  }
}

const editFormRef = ref()
const editForm = ref<MonitorStock & { conditions: string[] }>({
  id: 0,
  stock_code: '',
  stock_name: '',
  monitor_type: 'hold',
  conditions: [],
  is_active: true,
  remark: ''
})

// 选项
const typeOptions = [
  { label: '持仓监控', value: 'hold' },
  { label: '关注监控', value: 'watch' }
]

const activeOptions = [
  { label: '已启用', value: true },
  { label: '已禁用', value: false }
]

// 筛选后的列表
const filteredStocks = computed(() => {
  let result = stocks.value
  if (filterType.value) {
    result = result.filter(s => s.monitor_type === filterType.value)
  }
  if (filterActive.value !== null) {
    result = result.filter(s => s.is_active === filterActive.value)
  }
  return result
})

// 表格列
const stockColumns = [
  {
    title: '代码', key: 'stock_code', width: 100,
    render: (row: MonitorStock) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.stock_code })
  },
  { title: '名称', key: 'stock_name', width: 100 },
  {
    title: '类型', key: 'monitor_type', width: 90,
    render: (row: MonitorStock) => h(NTag, {
      type: row.monitor_type === 'hold' ? 'success' : 'warning', size: 'small'
    }, { default: () => row.monitor_type === 'hold' ? '持仓' : '关注' })
  },
  {
    title: '最新价', key: 'last_price', width: 90,
    render: (row: MonitorStock) => row.last_price ? row.last_price.toFixed(2) : '--'
  },
  {
    title: '涨跌幅', key: 'change_percent', width: 90,
    render: (row: MonitorStock) => {
      if (row.change_percent == null) return '--'
      const val = (row.change_percent * 100).toFixed(2)
      const color = row.change_percent >= 0 ? '#18a058' : '#d03050'
      return h('span', { style: { color } }, `${row.change_percent >= 0 ? '+' : ''}${val}%`)
    }
  },
  {
    title: '预警条件', key: 'conditions', width: 200,
    render: (row: MonitorStock) => {
      if (!row.conditions?.length) return '--'
      return h(NSpace, { size: 'small' }, {
        default: () => row.conditions.slice(0, 3).map(c =>
          h(NTag, { size: 'small', bordered: false }, { default: () => c })
        )
      })
    }
  },
  {
    title: '状态', key: 'is_active', width: 70,
    render: (row: MonitorStock) => h(NTag, {
      type: row.is_active ? 'success' : 'default', size: 'small'
    }, { default: () => row.is_active ? '启用' : '禁用' })
  },
  {
    title: '上次检查', key: 'last_check_time', width: 140,
    render: (row: MonitorStock) => row.last_check_time
      ? dayjs(row.last_check_time).format('MM-DD HH:mm')
      : '--'
  },
  {
    title: '操作', key: 'actions', width: 180,
    render: (row: MonitorStock) => h(NSpace, {}, {
      default: () => [
        h(NButton, { size: 'tiny', type: 'info', onClick: () => handleCheck(row) }, { default: () => '检测' }),
        h(NButton, { size: 'tiny', onClick: () => openEditModal(row) }, { default: () => '编辑' }),
        h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDelete(row) }, { default: () => '删除' })
      ]
    })
  }
]

// 加载数据
async function loadStocks() {
  loading.value = true
  try {
    stocks.value = await fetchMonitorStocks()
  } catch (error) {
    console.error('加载监控股票失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadConditions() {
  try {
    conditions.value = await fetchAvailableConditions()
  } catch (error) {
    console.error('加载预警条件失败:', error)
  }
}

// 添加股票
async function handleAddStock() {
  if (!addForm.value.stock_code) {
    message.warning('请输入股票代码')
    return
  }

  adding.value = true
  try {
    await addMonitorStock(addForm.value)
    message.success('添加成功')
    showAddModal.value = false
    addForm.value = {
      stock_code: '',
      stock_name: '',
      monitor_type: 'hold',
      conditions: [],
      remark: ''
    }
    loadStocks()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

// 编辑股票
function openEditModal(stock: MonitorStock) {
  editForm.value = {
    ...stock,
    conditions: stock.conditions || []
  }
  showEditModal.value = true
}

async function handleEditStock() {
  editing.value = true
  try {
    await updateMonitorStock(editForm.value.id, {
      stock_name: editForm.value.stock_name,
      monitor_type: editForm.value.monitor_type,
      conditions: editForm.value.conditions,
      is_active: editForm.value.is_active,
      remark: editForm.value.remark
    })
    message.success('保存成功')
    showEditModal.value = false
    loadStocks()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '保存失败')
  } finally {
    editing.value = false
  }
}

// 删除股票
async function handleDelete(stock: MonitorStock) {
  try {
    await deleteMonitorStock(stock.id)
    message.success('删除成功')
    loadStocks()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '删除失败')
  }
}

// 检测单只股票
async function handleCheck(stock: MonitorStock) {
  try {
    const result = await checkSingleStock(stock.id)
    if (result.triggered_count > 0) {
      message.warning(`${stock.stock_name} 触发 ${result.triggered_count} 条预警`)
    } else {
      message.success(`${stock.stock_name} 暂无预警`)
    }
    loadStocks()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '检测失败')
  }
}

// 检测所有股票
async function handleCheckAll() {
  checking.value = true
  try {
    const result = await checkAllStocks()
    message.success(result.message)
    loadStocks()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '检测失败')
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  loadStocks()
  loadConditions()
})
</script>

<style scoped lang="scss">
.monitor-page {
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

  .header-right {
    display: flex;
    align-items: center;
  }
}

.stock-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  flex: 1;
}

.py-8 {
  padding-top: 32px;
  padding-bottom: 32px;
}
</style>