<template>
  <div class="dict-page">
    <n-card title="字典管理">
      <n-tabs v-model:value="activeTab" type="line">
        <n-tab-pane name="types" tab="字典类型">
          <div class="toolbar">
            <n-space>
              <n-select
                v-model:value="typeFilter.category"
                :options="categoryOptions"
                placeholder="选择类别"
                clearable
                style="width: 150px"
                @update:value="loadTypes"
              />
              <n-select
                v-model:value="typeFilter.status"
                :options="statusOptions"
                placeholder="选择状态"
                clearable
                style="width: 120px"
                @update:value="loadTypes"
              />
              <n-input
                v-model:value="typeFilter.keyword"
                placeholder="搜索类型名称/编码"
                clearable
                style="width: 200px"
                @keyup.enter="loadTypes"
              />
              <n-button type="primary" @click="openTypeModal()">
                新增类型
              </n-button>
            </n-space>
          </div>
          <n-data-table
            :columns="typeColumns"
            :data="typeList"
            :loading="typeLoading"
            :pagination="typePagination"
            :row-key="(row: DictType) => row.id"
          />
        </n-tab-pane>
        <n-tab-pane name="items" tab="字典项">
          <div class="toolbar">
            <n-space>
              <n-select
                v-model:value="itemFilter.type_id"
                :options="typeOptions"
                placeholder="选择字典类型"
                clearable
                style="width: 200px"
                @update:value="loadItems"
              />
              <n-select
                v-model:value="itemFilter.status"
                :options="statusOptions"
                placeholder="选择状态"
                clearable
                style="width: 120px"
                @update:value="loadItems"
              />
              <n-input
                v-model:value="itemFilter.keyword"
                placeholder="搜索项名称/编码"
                clearable
                style="width: 200px"
                @keyup.enter="loadItems"
              />
              <n-button type="primary" :disabled="!itemFilter.type_id" @click="openItemModal()">
                新增字典项
              </n-button>
            </n-space>
          </div>
          <n-data-table
            :columns="itemColumns"
            :data="itemList"
            :loading="itemLoading"
            :pagination="itemPagination"
            :row-key="(row: DictItem) => row.id"
          />
        </n-tab-pane>
      </n-tabs>
    </n-card>

    <!-- 字典类型编辑弹窗 -->
    <n-modal v-model:show="typeModalVisible" preset="dialog" title="编辑字典类型" style="width: 500px">
      <n-form ref="typeFormRef" :model="typeForm" :rules="typeRules" label-placement="left" label-width="80">
        <n-form-item label="类型编码" path="code">
          <n-input v-model:value="typeForm.code" placeholder="请输入类型编码" :disabled="!!typeForm.id" />
        </n-form-item>
        <n-form-item label="类型名称" path="name">
          <n-input v-model:value="typeForm.name" placeholder="请输入类型名称" />
        </n-form-item>
        <n-form-item label="类别" path="category">
          <n-select v-model:value="typeForm.category" :options="categoryOptions" />
        </n-form-item>
        <n-form-item label="访问类型" path="access_type">
          <n-select v-model:value="typeForm.access_type" :options="accessTypeOptions" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="typeForm.description" type="textarea" placeholder="请输入描述" />
        </n-form-item>
        <n-form-item label="排序" path="sort">
          <n-input-number v-model:value="typeForm.sort" :min="0" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-select v-model:value="typeForm.status" :options="statusOptions" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="typeModalVisible = false">取消</n-button>
          <n-button type="primary" :loading="typeSubmitLoading" @click="submitType">确定</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 字典项编辑弹窗 -->
    <n-modal v-model:show="itemModalVisible" preset="dialog" title="编辑字典项" style="width: 500px">
      <n-form ref="itemFormRef" :model="itemForm" :rules="itemRules" label-placement="left" label-width="80">
        <n-form-item label="项编码" path="code">
          <n-input v-model:value="itemForm.code" placeholder="请输入项编码" :disabled="!!itemForm.id" />
        </n-form-item>
        <n-form-item label="项名称" path="name">
          <n-input v-model:value="itemForm.name" placeholder="请输入项名称" />
        </n-form-item>
        <n-form-item label="项值" path="value">
          <n-input v-model:value="itemForm.value" placeholder="请输入项值" />
        </n-form-item>
        <n-form-item label="数据类型" path="data_type">
          <n-select v-model:value="itemForm.data_type" :options="dataTypeOptions" />
        </n-form-item>
        <n-form-item label="父级项" path="parent_id">
          <n-select v-model:value="itemForm.parent_id" :options="parentItemOptions" clearable placeholder="选择父级项" />
        </n-form-item>
        <n-form-item label="排序" path="sort">
          <n-input-number v-model:value="itemForm.sort" :min="0" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-select v-model:value="itemForm.status" :options="statusOptions" />
        </n-form-item>
        <n-form-item label="备注" path="remark">
          <n-input v-model:value="itemForm.remark" type="textarea" placeholder="请输入备注" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="itemModalVisible = false">取消</n-button>
          <n-button type="primary" :loading="itemSubmitLoading" @click="submitItem">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, h, onMounted } from 'vue'
import { NButton, NTag, NSpace, useMessage, type DataTableColumns, type FormInst, type FormRules } from 'naive-ui'
import type { DictType, DictItem, DictTypeCreateParams, DictItemCreateParams } from '@/types/dict'
import * as dictApi from '@/api/dict'

const message = useMessage()

// Tab状态
const activeTab = ref('types')

// ==================== 字典类型管理 ====================
const typeLoading = ref(false)
const typeList = ref<DictType[]>([])
const typePagination = reactive({ page: 1, pageSize: 10, itemCount: 0, onChange: (page: number) => { typePagination.page = page; loadTypes() } })
const typeFilter = reactive({ category: null as string | null, status: null as string | null, keyword: '' })
const typeModalVisible = ref(false)
const typeSubmitLoading = ref(false)
const typeFormRef = ref<FormInst | null>(null)
const typeForm = reactive<DictTypeCreateParams & { id?: number }>({
  code: '',
  name: '',
  category: 'system',
  access_type: 'public',
  description: '',
  sort: 0,
  status: 'active'
})

const typeRules: FormRules = {
  code: [{ required: true, message: '请输入类型编码' }],
  name: [{ required: true, message: '请输入类型名称' }]
}

const categoryOptions = [
  { label: '系统预置', value: 'system' },
  { label: '用户自定义', value: 'custom' },
  { label: '系统配置', value: 'config' }
]

const accessTypeOptions = [
  { label: '公开', value: 'public' },
  { label: '私有', value: 'private' }
]

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'disabled' }
]

const dataTypeOptions = [
  { label: '明文', value: 'plain' },
  { label: '加密', value: 'encrypted' }
]

const typeColumns: DataTableColumns<DictType> = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '类型编码', key: 'code', width: 150 },
  { title: '类型名称', key: 'name', width: 150 },
  { title: '类别', key: 'category', width: 100, render: (row) => h(NTag, { type: 'info' }, () => categoryOptions.find(o => o.value === row.category)?.label || row.category) },
  { title: '访问类型', key: 'access_type', width: 100, render: (row) => h(NTag, { type: row.access_type === 'private' ? 'warning' : 'default' }, () => accessTypeOptions.find(o => o.value === row.access_type)?.label || row.access_type) },
  { title: '排序', key: 'sort', width: 80 },
  { title: '状态', key: 'status', width: 80, render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'error' }, () => row.status === 'active' ? '启用' : '禁用') },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  {
    title: '操作', key: 'actions', width: 150, render: (row) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', onClick: () => openTypeModal(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDeleteType(row.id) }, () => '删除')
    ])
  }
]

async function loadTypes() {
  typeLoading.value = true
  try {
    const res = await dictApi.getDictTypes({
      category: typeFilter.category || undefined,
      status: typeFilter.status || undefined,
      keyword: typeFilter.keyword || undefined,
      page: typePagination.page,
      page_size: typePagination.pageSize
    })
    typeList.value = res.items
    typePagination.itemCount = res.total
  } finally {
    typeLoading.value = false
  }
}

function openTypeModal(row?: DictType) {
  if (row) {
    typeForm.id = row.id
    typeForm.code = row.code
    typeForm.name = row.name
    typeForm.category = row.category
    typeForm.access_type = row.access_type
    typeForm.description = row.description || ''
    typeForm.sort = row.sort
    typeForm.status = row.status
  } else {
    typeForm.id = undefined
    typeForm.code = ''
    typeForm.name = ''
    typeForm.category = 'system'
    typeForm.access_type = 'public'
    typeForm.description = ''
    typeForm.sort = 0
    typeForm.status = 'active'
  }
  typeModalVisible.value = true
}

async function submitType() {
  try {
    await typeFormRef.value?.validate()
  } catch {
    return
  }

  typeSubmitLoading.value = true
  try {
    if (typeForm.id) {
      await dictApi.updateDictType(typeForm.id, typeForm)
      message.success('更新成功')
    } else {
      await dictApi.createDictType(typeForm)
      message.success('创建成功')
    }
    typeModalVisible.value = false
    loadTypes()
  } catch (e: any) {
    message.error(e.message || '操作失败')
  } finally {
    typeSubmitLoading.value = false
  }
}

async function handleDeleteType(id: number) {
  try {
    await dictApi.deleteDictType(id)
    message.success('删除成功')
    loadTypes()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

// ==================== 字典项管理 ====================
const itemLoading = ref(false)
const itemList = ref<DictItem[]>([])
const itemPagination = reactive({ page: 1, pageSize: 10, itemCount: 0, onChange: (page: number) => { itemPagination.page = page; loadItems() } })
const itemFilter = reactive({ type_id: null as number | null, status: null as string | null, keyword: '' })
const itemModalVisible = ref(false)
const itemSubmitLoading = ref(false)
const itemFormRef = ref<FormInst | null>(null)
const itemForm = reactive<DictItemCreateParams & { id?: number }>({
  type_id: 0,
  code: '',
  name: '',
  value: '',
  data_type: 'plain',
  parent_id: undefined,
  sort: 0,
  status: 'active',
  remark: ''
})

const itemRules: FormRules = {
  code: [{ required: true, message: '请输入项编码' }],
  name: [{ required: true, message: '请输入项名称' }]
}

const typeOptions = computed(() =>
  typeList.value.map(t => ({ label: `${t.name} (${t.code})`, value: t.id }))
)

const parentItemOptions = computed(() =>
  itemList.value.filter(i => i.id !== itemForm.id).map(i => ({ label: i.name, value: i.id }))
)

const itemColumns: DataTableColumns<DictItem> = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '项编码', key: 'code', width: 150 },
  { title: '项名称', key: 'name', width: 150 },
  { title: '项值', key: 'value', width: 150, ellipsis: { tooltip: true } },
  { title: '数据类型', key: 'data_type', width: 100, render: (row) => h(NTag, { type: row.data_type === 'encrypted' ? 'warning' : 'default' }, () => row.data_type === 'encrypted' ? '加密' : '明文') },
  { title: '排序', key: 'sort', width: 80 },
  { title: '状态', key: 'status', width: 80, render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'error' }, () => row.status === 'active' ? '启用' : '禁用') },
  { title: '备注', key: 'remark', ellipsis: { tooltip: true } },
  {
    title: '操作', key: 'actions', width: 150, render: (row) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', onClick: () => openItemModal(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDeleteItem(row.id) }, () => '删除')
    ])
  }
]

async function loadItems() {
  if (!itemFilter.type_id) {
    itemList.value = []
    return
  }
  itemLoading.value = true
  try {
    const res = await dictApi.getDictItems({
      type_id: itemFilter.type_id || undefined,
      status: itemFilter.status || undefined,
      keyword: itemFilter.keyword || undefined,
      page: itemPagination.page,
      page_size: itemPagination.pageSize
    })
    itemList.value = res.items
    itemPagination.itemCount = res.total
  } finally {
    itemLoading.value = false
  }
}

function openItemModal(row?: DictItem) {
  if (!itemFilter.type_id) {
    message.warning('请先选择字典类型')
    return
  }
  if (row) {
    itemForm.id = row.id
    itemForm.type_id = row.type_id
    itemForm.code = row.code
    itemForm.name = row.name
    itemForm.value = row.value || ''
    itemForm.data_type = row.data_type
    itemForm.parent_id = row.parent_id
    itemForm.sort = row.sort
    itemForm.status = row.status
    itemForm.remark = row.remark || ''
  } else {
    itemForm.id = undefined
    itemForm.type_id = itemFilter.type_id
    itemForm.code = ''
    itemForm.name = ''
    itemForm.value = ''
    itemForm.data_type = 'plain'
    itemForm.parent_id = undefined
    itemForm.sort = 0
    itemForm.status = 'active'
    itemForm.remark = ''
  }
  itemModalVisible.value = true
}

async function submitItem() {
  try {
    await itemFormRef.value?.validate()
  } catch {
    return
  }

  itemSubmitLoading.value = true
  try {
    if (itemForm.id) {
      await dictApi.updateDictItem(itemForm.id, itemForm)
      message.success('更新成功')
    } else {
      await dictApi.createDictItem(itemForm)
      message.success('创建成功')
    }
    itemModalVisible.value = false
    loadItems()
  } catch (e: any) {
    message.error(e.message || '操作失败')
  } finally {
    itemSubmitLoading.value = false
  }
}

async function handleDeleteItem(id: number) {
  try {
    await dictApi.deleteDictItem(id)
    message.success('删除成功')
    loadItems()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

// 初始化
onMounted(() => {
  loadTypes()
})
</script>

<style scoped lang="scss">
.dict-page {
  padding: 16px;

  .toolbar {
    margin-bottom: 16px;
  }
}
</style>