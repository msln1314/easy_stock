<template>
  <div class="dict-page">
    <n-card title="字典管理" class="dict-card">
      <div class="dict-layout">
        <!-- 左侧：字典类型列表 -->
        <div class="dict-type-panel">
          <div class="panel-header">
            <span class="panel-title">字典类型</span>
            <n-button size="small" type="primary" @click="openTypeModal()">
              新增
            </n-button>
          </div>
          <div class="panel-toolbar">
            <n-input
              v-model:value="typeFilter.keyword"
              placeholder="搜索类型"
              clearable
              size="small"
              @keyup.enter="loadTypes"
            >
              <template #prefix>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
              </template>
            </n-input>
          </div>
          <div class="type-list">
            <n-spin :show="typeLoading">
              <div
                v-for="item in typeList"
                :key="item.id"
                :class="['type-item', { active: selectedTypeId === item.id }]"
                @click="selectType(item)"
              >
                <div class="type-info">
                  <span class="type-name">{{ item.name }}</span>
                  <span class="type-code">{{ item.code }}</span>
                </div>
                <div class="type-tags">
                  <n-tag size="small" :type="item.access_type === 'private' ? 'warning' : 'default'">
                    {{ item.access_type === 'private' ? '私有' : '公开' }}
                  </n-tag>
                  <n-tag size="small" :type="item.status === 'active' ? 'success' : 'error'">
                    {{ item.status === 'active' ? '启用' : '禁用' }}
                  </n-tag>
                </div>
              </div>
              <n-empty v-if="!typeLoading && typeList.length === 0" description="暂无字典类型" />
            </n-spin>
          </div>
        </div>

        <!-- 右侧：字典项列表 -->
        <div class="dict-item-panel">
          <template v-if="selectedType">
            <div class="panel-header">
              <div class="panel-title-row">
                <span class="panel-title">{{ selectedType.name }}</span>
                <n-tag size="small" type="info">{{ selectedType.code }}</n-tag>
              </div>
              <n-space>
                <n-button size="small" @click="openTypeModal(selectedType)">编辑类型</n-button>
                <n-button size="small" type="primary" @click="openItemModal()">新增项</n-button>
              </n-space>
            </div>
            <div class="panel-toolbar">
              <n-input
                v-model:value="itemFilter.keyword"
                placeholder="搜索字典项"
                clearable
                size="small"
                style="width: 200px"
                @keyup.enter="loadItems"
              />
              <n-select
                v-model:value="itemFilter.status"
                :options="statusOptions"
                placeholder="状态"
                clearable
                size="small"
                style="width: 100px"
                @update:value="loadItems"
              />
            </div>
            <n-data-table
              :columns="itemColumns"
              :data="itemList"
              :loading="itemLoading"
              :pagination="itemPagination"
              :row-key="(row) => row.id"
              size="small"
            />
          </template>
          <n-empty v-else description="请选择左侧字典类型" class="empty-placeholder" />
        </div>
      </div>
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
          <n-radio-group v-model:value="typeForm.access_type">
            <n-radio-button value="public">公开</n-radio-button>
            <n-radio-button value="private">私有</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="typeForm.description" type="textarea" placeholder="请输入描述" />
        </n-form-item>
        <n-form-item label="排序" path="sort">
          <n-input-number v-model:value="typeForm.sort" :min="0" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-radio-group v-model:value="typeForm.status">
            <n-radio-button value="active">启用</n-radio-button>
            <n-radio-button value="disabled">禁用</n-radio-button>
          </n-radio-group>
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
        <n-form-item label="项名称" path="name">
          <n-input v-model:value="itemForm.name" placeholder="请输入项名称" />
        </n-form-item>
        <n-form-item label="项值" path="value">
          <n-input v-model:value="itemForm.value" placeholder="请输入项值" />
        </n-form-item>
        <n-form-item label="访问类型" path="access_type">
          <n-radio-group v-model:value="itemForm.access_type">
            <n-radio-button value="public">公开</n-radio-button>
            <n-radio-button value="private">私有</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="排序" path="sort">
          <n-input-number v-model:value="itemForm.sort" :min="0" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-radio-group v-model:value="itemForm.status">
            <n-radio-button value="active">启用</n-radio-button>
            <n-radio-button value="disabled">禁用</n-radio-button>
          </n-radio-group>
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

// ==================== 字典类型管理 ====================
const typeLoading = ref(false)
const typeList = ref<DictType[]>([])
const typeFilter = reactive({ keyword: '' })
const selectedTypeId = ref<number | null>(null)
const selectedType = computed(() => typeList.value.find(t => t.id === selectedTypeId.value))

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

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'disabled' }
]

async function loadTypes() {
  typeLoading.value = true
  try {
    const res = await dictApi.getDictTypes({
      keyword: typeFilter.keyword || undefined,
      page: 1,
      page_size: 100
    })
    typeList.value = res.items
    // 如果没有选中且列表有数据，自动选中第一个
    if (!selectedTypeId.value && typeList.value.length > 0) {
      selectedTypeId.value = typeList.value[0].id
      loadItems()
    }
  } finally {
    typeLoading.value = false
  }
}

function selectType(item: DictType) {
  selectedTypeId.value = item.id
  loadItems()
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
  } catch (e) {
    const err = e as Error
    message.error(err.message || '操作失败')
  } finally {
    typeSubmitLoading.value = false
  }
}

// ==================== 字典项管理 ====================
const itemLoading = ref(false)
const itemList = ref<DictItem[]>([])
const itemPagination = reactive({ page: 1, pageSize: 10, itemCount: 0, onChange: (page: number) => { itemPagination.page = page; loadItems() } })
const itemFilter = reactive({ status: null as string | null, keyword: '' })
const itemModalVisible = ref(false)
const itemSubmitLoading = ref(false)
const itemFormRef = ref<FormInst | null>(null)
const itemForm = reactive<DictItemCreateParams & { id?: number }>({
  type_id: 0,
  code: '',
  name: '',
  value: '',
  data_type: 'plain',
  access_type: 'public',
  parent_id: undefined,
  sort: 0,
  status: 'active',
  remark: ''
})

const itemRules: FormRules = {
  code: [{ required: true, message: '请输入项编码' }],
  name: [{ required: true, message: '请输入项名称' }]
}

const itemColumns: DataTableColumns<DictItem> = [
  { title: '编码', key: 'code', width: 120 },
  { title: '名称', key: 'name', width: 150 },
  { title: '值', key: 'value', ellipsis: { tooltip: true } },
  {
    title: '访问',
    key: 'access_type',
    width: 80,
    render: (row) => h(NTag, {
      size: 'small',
      type: row.access_type === 'private' ? 'warning' : 'default'
    }, () => row.access_type === 'private' ? '私有' : '公开')
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    render: (row) => h(NTag, {
      size: 'small',
      type: row.status === 'active' ? 'success' : 'error'
    }, () => row.status === 'active' ? '启用' : '禁用')
  },
  { title: '排序', key: 'sort', width: 60 },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) => h(NSpace, { size: 'small' }, () => [
      h(NButton, { size: 'tiny', onClick: () => openItemModal(row) }, () => '编辑'),
      h(NButton, { size: 'tiny', type: 'error', onClick: () => handleDeleteItem(row.id) }, () => '删除')
    ])
  }
]

async function loadItems() {
  if (!selectedTypeId.value) {
    itemList.value = []
    return
  }
  itemLoading.value = true
  try {
    const res = await dictApi.getDictItems({
      type_id: selectedTypeId.value,
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
  if (!selectedTypeId.value) {
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
    itemForm.access_type = row.access_type
    itemForm.sort = row.sort
    itemForm.status = row.status
    itemForm.remark = row.remark || ''
  } else {
    itemForm.id = undefined
    itemForm.type_id = selectedTypeId.value
    itemForm.code = ''
    itemForm.name = ''
    itemForm.value = ''
    itemForm.data_type = 'plain'
    itemForm.access_type = 'public'
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
  } catch (e) {
    const err = e as Error
    message.error(err.message || '操作失败')
  } finally {
    itemSubmitLoading.value = false
  }
}

async function handleDeleteItem(id: number) {
  try {
    await dictApi.deleteDictItem(id)
    message.success('删除成功')
    loadItems()
  } catch (e) {
    const err = e as Error
    message.error(err.message || '删除失败')
  }
}

// 初始化
onMounted(() => {
  loadTypes()
})
</script>

<style scoped lang="scss">
.dict-page {
  height: 100%;
  padding: 16px;
  box-sizing: border-box;
}

.dict-card {
  height: 100%;

  :deep(.n-card__content) {
    height: 100%;
    padding: 0;
  }
}

.dict-layout {
  display: flex;
  height: 100%;
  gap: 0;
}

.dict-type-panel {
  width: 280px;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.dict-item-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e8e8e8;
  background: #fff;
}

.panel-title {
  font-weight: 600;
  font-size: 14px;
}

.panel-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-toolbar {
  padding: 8px 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  gap: 8px;
}

.type-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.type-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s;
  background: #fff;
  border: 1px solid transparent;

  &:hover {
    background: #f0f7ff;
  }

  &.active {
    background: #e6f4ff;
    border-color: #1890ff;
  }
}

.type-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.type-name {
  font-weight: 500;
  font-size: 13px;
}

.type-code {
  font-size: 12px;
  color: #999;
}

.type-tags {
  display: flex;
  gap: 4px;
}

.empty-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.n-data-table) {
  flex: 1;
}
</style>