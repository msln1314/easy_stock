<template>
  <div class="etf-pool-page">
    <n-card title="ETF池配置">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="handleAdd">
            添加ETF
          </n-button>
          <n-button @click="handleBack">
            返回监控
          </n-button>
        </n-space>
      </template>

      <!-- 筛选 -->
      <n-space class="mb-4">
        <n-input v-model:value="searchKeyword" placeholder="搜索ETF名称/代码" clearable style="width: 200px" />
        <n-select v-model:value="filterSector" :options="sectorOptions" placeholder="行业筛选" clearable style="width: 150px" />
        <n-switch v-model:value="filterActive" @update:value="handleFilterChange">
          <template #checked>仅启用</template>
          <template #unchecked>全部</template>
        </n-switch>
      </n-space>

      <!-- ETF列表 -->
      <n-data-table
        :columns="columns"
        :data="filteredEtfs"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
      />

      <!-- 添加ETF对话框 -->
      <n-modal v-model:show="showAddModal" preset="card" title="添加ETF" style="width: 400px">
        <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="80">
          <n-form-item label="ETF名称" path="name">
            <n-input v-model:value="formData.name" placeholder="如: 科技ETF" />
          </n-form-item>
          <n-form-item label="ETF代码" path="code">
            <n-input v-model:value="formData.code" placeholder="如: 515000" />
          </n-form-item>
          <n-form-item label="行业板块" path="sector">
            <n-select v-model:value="formData.sector" :options="sectorOptions" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showAddModal = false">取消</n-button>
            <n-button type="primary" @click="handleSubmit">添加</n-button>
          </n-space>
        </template>
      </n-modal>

      <!-- 编辑ETF对话框 -->
      <n-modal v-model:show="showEditModal" preset="card" title="编辑ETF" style="width: 400px">
        <n-form ref="editFormRef" :model="editData" label-placement="left" label-width="80">
          <n-form-item label="ETF名称">
            <n-input v-model:value="editData.name" />
          </n-form-item>
          <n-form-item label="行业板块">
            <n-select v-model:value="editData.sector" :options="sectorOptions" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showEditModal = false">取消</n-button>
            <n-button type="primary" @click="handleEditSubmit">保存</n-button>
          </n-space>
        </template>
      </n-modal>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, h } from 'vue'
import { NTag, NButton, NSpace, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  getEtfPoolList,
  addEtf,
  updateEtf,
  deleteEtf,
  toggleEtfStatus
} from '@/api/etfPool'
import type { EtfPool, EtfPoolCreate, EtfPoolUpdate } from '@/types/etfRotation'

const message = useMessage()

// 状态
const loading = ref(false)
const etfs = ref<EtfPool[]>([])
const searchKeyword = ref('')
const filterSector = ref<string | null>(null)
const filterActive = ref(true)

// 对话框
const showAddModal = ref(false)
const showEditModal = ref(false)
const formRef = ref()
const editFormRef = ref()
const formData = reactive<EtfPoolCreate>({
  name: '',
  code: '',
  sector: '',
  is_active: true
})
const editData = reactive<EtfPoolUpdate>({
  name: '',
  sector: ''
})
const editId = ref<number>(0)

// 表单规则
const formRules = {
  name: { required: true, message: '请输入ETF名称' },
  code: { required: true, message: '请输入ETF代码' },
  sector: { required: true, message: '请选择行业板块' }
}

// 行业选项
const sectorOptions = [
  { label: '科技', value: '科技' },
  { label: '消费', value: '消费' },
  { label: '医药', value: '医药' },
  { label: '金融', value: '金融' },
  { label: '军工', value: '军工' },
  { label: '新能源', value: '新能源' },
  { label: '半导体', value: '半导体' },
  { label: '有色金属', value: '有色金属' },
  { label: '基建', value: '基建' },
  { label: '其他', value: '其他' }
]

// 过滤后的ETF列表
const filteredEtfs = computed(() => {
  return etfs.value.filter(etf => {
    if (filterActive.value && !etf.is_active) return false
    if (filterSector.value && etf.sector !== filterSector.value) return false
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      if (!etf.name.toLowerCase().includes(keyword) &&
          !etf.code.toLowerCase().includes(keyword)) return false
    }
    return true
  })
})

// 表格列
const columns: DataTableColumns<EtfPool> = [
  { title: 'ETF名称', key: 'name' },
  { title: '代码', key: 'code' },
  { title: '行业', key: 'sector' },
  {
    title: '状态',
    key: 'is_active',
    render(row) {
      return h(NTag, {
        type: row.is_active ? 'success' : 'default',
        size: 'small'
      }, { default: () => row.is_active ? '启用' : '禁用' })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => handleToggle(row)
          }, { default: () => row.is_active ? '禁用' : '启用' }),
          h(NButton, {
            size: 'small',
            onClick: () => handleEdit(row)
          }, { default: () => '编辑' }),
          h(NButton, {
            size: 'small',
            type: 'error',
            onClick: () => handleDelete(row)
          }, { default: () => '删除' })
        ]
      })
    }
  }
]

// 加载ETF池列表
async function loadEtfs() {
  loading.value = true
  try {
    etfs.value = await getEtfPoolList({ is_active: false })
  } catch (e) {
    message.error('加载ETF池失败')
  } finally {
    loading.value = false
  }
}

// 添加ETF
function handleAdd() {
  formData.name = ''
  formData.code = ''
  formData.sector = ''
  showAddModal.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    await addEtf(formData)
    message.success('添加成功')
    showAddModal.value = false
    await loadEtfs()
  } catch (e) {
    // 验证失败或API错误
  }
}

// 编辑ETF
function handleEdit(etf: EtfPool) {
  editId.value = etf.id
  editData.name = etf.name
  editData.sector = etf.sector
  showEditModal.value = true
}

async function handleEditSubmit() {
  try {
    await updateEtf(editId.value, editData)
    message.success('保存成功')
    showEditModal.value = false
    await loadEtfs()
  } catch (e) {
    message.error('保存失败')
  }
}

// 切换启用状态
async function handleToggle(etf: EtfPool) {
  try {
    await toggleEtfStatus(etf.id)
    message.success(etf.is_active ? '已禁用' : '已启用')
    await loadEtfs()
  } catch (e) {
    message.error('操作失败')
  }
}

// 删除ETF
async function handleDelete(etf: EtfPool) {
  try {
    await deleteEtf(etf.id)
    message.success('删除成功')
    await loadEtfs()
  } catch (e) {
    message.error('删除失败')
  }
}

// 篮选变化
function handleFilterChange() {
  loadEtfs()
}

// 返回监控页
function handleBack() {
  window.location.href = '/policy/etf-rotation'
}

// 初始化
onMounted(() => {
  loadEtfs()
})
</script>

<style scoped>
.etf-pool-page {
  padding: 16px;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>