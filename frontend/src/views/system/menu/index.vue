<template>
  <div class="menu-page">
    <n-card title="菜单管理">
      <div class="toolbar">
        <n-space>
          <n-button type="primary" @click="openModal()">
            新增菜单
          </n-button>
          <n-button v-if="hasChanges" type="warning" @click="saveSort">
            保存排序
          </n-button>
        </n-space>
        <span class="tip">提示：拖动行可调整排序</span>
      </div>
      <n-data-table
        ref="tableRef"
        :columns="columns"
        :data="menuList"
        :loading="loading"
        :row-key="getRowKey"
        indent="20"
        default-expand-all
        :row-props="rowProps"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="modalVisible" preset="dialog" title="编辑菜单" style="width: 600px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="100">
        <n-form-item label="上级菜单" path="parent_id">
          <n-tree-select
            v-model:value="form.parent_id"
            :options="parentMenuOptions"
            clearable
            placeholder="选择上级菜单（不选则为顶级）"
          />
        </n-form-item>
        <n-form-item label="菜单类型" path="menu_type">
          <n-radio-group v-model:value="form.menu_type">
            <n-radio-button value="directory">目录</n-radio-button>
            <n-radio-button value="menu">菜单</n-radio-button>
            <n-radio-button value="button">按钮</n-radio-button>
            <n-radio-button value="link">外链</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="菜单名称" path="name">
          <n-input v-model:value="form.name" placeholder="请输入菜单名称" />
        </n-form-item>
        <n-form-item v-if="form.menu_type !== 'button'" label="路由路径" path="path">
          <n-input v-model:value="form.path" placeholder="请输入路由路径" />
        </n-form-item>
        <n-form-item v-if="form.menu_type === 'menu'" label="组件路径" path="component">
          <n-input v-model:value="form.component" placeholder="请输入组件路径" />
        </n-form-item>
        <n-form-item v-if="form.menu_type !== 'button'" label="图标" path="icon">
          <n-input v-model:value="form.icon" placeholder="请输入图标名称" />
        </n-form-item>
        <!-- 外部链接配置 -->
        <n-form-item v-if="form.menu_type === 'link'" label="外部链接" path="external_url">
          <n-input v-model:value="form.external_url" placeholder="请输入外部链接URL" />
        </n-form-item>
        <n-form-item v-if="form.menu_type === 'link'" label="打开方式" path="link_target">
          <n-radio-group v-model:value="form.link_target">
            <n-radio-button value="_blank">新窗口</n-radio-button>
            <n-radio-button value="_self">当前窗口</n-radio-button>
            <n-radio-button value="_iframe">iframe嵌入</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="排序" path="sort">
          <n-input-number v-model:value="form.sort" :min="0" />
        </n-form-item>
        <n-form-item v-if="form.menu_type !== 'button'" label="是否显示" path="visible">
          <n-switch v-model:value="form.visible" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-radio-group v-model:value="form.status">
            <n-radio-button value="active">启用</n-radio-button>
            <n-radio-button value="inactive">禁用</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="权限标识" path="permission">
          <n-input v-model:value="form.permission" placeholder="请输入权限标识，如 menu:view" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" :loading="submitLoading" @click="submit">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted, computed } from 'vue'
import { NButton, NTag, NSpace, useMessage, type DataTableColumns, type FormInst, type FormRules } from 'naive-ui'
import type { MenuTreeResponse, MenuCreate, MenuUpdate, MenuType } from '@/types/menu'
import * as menuApi from '@/api/menu'

const message = useMessage()

const loading = ref(false)
const menuList = ref<MenuTreeResponse[]>([])
const modalVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInst | null>(null)
const tableRef = ref<any>(null)
const hasChanges = ref(false)

// 拖拽相关
const dragRow = ref<MenuTreeResponse | null>(null)

const form = reactive<{
  id?: number
  parent_id?: number
  name: string
  path: string
  component?: string
  icon?: string
  sort: number
  visible: boolean
  status: string
  menu_type: MenuType
  permission?: string
  is_external?: boolean
  external_url?: string
  link_target?: string
}>({
  parent_id: undefined,
  name: '',
  path: '',
  component: '',
  icon: '',
  sort: 0,
  visible: true,
  status: 'active',
  menu_type: 'menu',
  permission: '',
  is_external: false,
  external_url: '',
  link_target: '_blank'
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入菜单名称' }],
  path: [{ required: true, message: '请输入路由路径' }],
  menu_type: [{ required: true, message: '请选择菜单类型' }]
}

const menuTypeOptions: Record<string, { label: string; type: 'default' | 'info' | 'success' | 'warning' }> = {
  directory: { label: '目录', type: 'default' },
  menu: { label: '菜单', type: 'info' },
  button: { label: '按钮', type: 'success' },
  link: { label: '外链', type: 'warning' }
}

const columns: DataTableColumns<MenuTreeResponse> = [
  { title: '菜单名称', key: 'name' },
  { title: '类型', key: 'menu_type', width: 80, render: (row) => h(NTag, { type: menuTypeOptions[row.menu_type]?.type || 'default', size: 'small' }, () => menuTypeOptions[row.menu_type]?.label || row.menu_type) },
  { title: '路径', key: 'path', width: 150 },
  { title: '图标', key: 'icon', width: 80 },
  { title: '排序', key: 'sort', width: 60 },
  { title: '可见', key: 'visible', width: 60, render: (row) => h(NTag, { type: row.visible ? 'success' : 'error', size: 'small' }, () => row.visible ? '是' : '否') },
  { title: '状态', key: 'status', width: 80, render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'error', size: 'small' }, () => row.status === 'active' ? '启用' : '禁用') },
  { title: '权限标识', key: 'permission', width: 150 },
  {
    title: '操作', key: 'actions', width: 150, render: (row) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', onClick: () => openModal(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row.id) }, () => '删除')
    ])
  }
]

const parentMenuOptions = computed(() => {
  function buildOptions(list: MenuTreeResponse[]): any[] {
    return list.map(m => ({
      label: m.name,
      key: m.id,
      children: m.children && m.children.length > 0 ? buildOptions(m.children) : undefined
    }))
  }
  return buildOptions(menuList.value)
})

function getRowKey(row: MenuTreeResponse) {
  return row.id
}

// 拖拽功能
function rowProps(row: MenuTreeResponse) {
  return {
    style: 'cursor: move;',
    draggable: true,
    onDragstart: (e: DragEvent) => {
      dragRow.value = row
      if (e.dataTransfer) {
        e.dataTransfer.effectAllowed = 'move'
      }
    },
    onDragover: (e: DragEvent) => {
      e.preventDefault()
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = 'move'
      }
    },
    onDrop: (e: DragEvent) => {
      e.preventDefault()
      if (dragRow.value && dragRow.value.id !== row.id) {
        // 同级菜单排序
        handleDragSort(dragRow.value, row)
      }
      dragRow.value = null
    },
    onDragend: () => {
      dragRow.value = null
    }
  }
}

function handleDragSort(source: MenuTreeResponse, target: MenuTreeResponse) {
  // 只允许同级拖拽排序
  if (source.parent_id !== target.parent_id) {
    message.warning('只支持同级菜单排序')
    return
  }

  // 找到父级菜单列表
  let siblingList: MenuTreeResponse[]
  if (source.parent_id) {
    const parent = findMenuById(menuList.value, source.parent_id)
    siblingList = parent?.children || []
  } else {
    siblingList = menuList.value
  }

  // 找到两个菜单的索引
  const sourceIndex = siblingList.findIndex(m => m.id === source.id)
  const targetIndex = siblingList.findIndex(m => m.id === target.id)

  if (sourceIndex === -1 || targetIndex === -1) return

  // 交换位置
  const newSort = [...siblingList]
  const [removed] = newSort.splice(sourceIndex, 1)
  newSort.splice(targetIndex, 0, removed)

  // 更新排序值
  newSort.forEach((item, index) => {
    item.sort = index
  })

  // 更新原始列表
  if (source.parent_id) {
    const parent = findMenuById(menuList.value, source.parent_id)
    if (parent) {
      parent.children = newSort
    }
  } else {
    menuList.value = newSort
  }

  hasChanges.value = true
  message.info('排序已修改，请点击保存')
}

function findMenuById(list: MenuTreeResponse[], id: number): MenuTreeResponse | null {
  for (const item of list) {
    if (item.id === id) return item
    if (item.children) {
      const found = findMenuById(item.children, id)
      if (found) return found
    }
  }
  return null
}

async function saveSort() {
  // 收集所有菜单的排序
  const sortData: Record<number, number> = {}

  function collectSort(list: MenuTreeResponse[]) {
    for (const item of list) {
      sortData[item.id] = item.sort
      if (item.children) {
        collectSort(item.children)
      }
    }
  }

  collectSort(menuList.value)

  try {
    // 批量更新排序
    for (const [id, sort] of Object.entries(sortData)) {
      await menuApi.updateMenu(Number(id), { sort })
    }
    message.success('排序保存成功')
    hasChanges.value = false
    loadMenus()
  } catch (e) {
    const err = e as Error
    message.error(err.message || '保存失败')
  }
}

async function loadMenus() {
  loading.value = true
  try {
    const res = await menuApi.getMenuTree()
    menuList.value = res
  } catch (e) {
    const err = e as Error
    message.error(err.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function openModal(row?: MenuTreeResponse) {
  if (row) {
    form.id = row.id
    form.parent_id = row.parent_id
    form.name = row.name
    form.path = row.path
    form.component = row.component || ''
    form.icon = row.icon || ''
    form.sort = row.sort
    form.visible = row.visible
    form.status = row.status
    form.menu_type = row.menu_type
    form.permission = row.permission || ''
    form.is_external = row.is_external
    form.external_url = row.external_url || ''
    form.link_target = row.link_target || '_blank'
  } else {
    form.id = undefined
    form.parent_id = undefined
    form.name = ''
    form.path = ''
    form.component = ''
    form.icon = ''
    form.sort = 0
    form.visible = true
    form.status = 'active'
    form.menu_type = 'menu'
    form.permission = ''
    form.is_external = false
    form.external_url = ''
    form.link_target = '_blank'
  }
  modalVisible.value = true
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitLoading.value = true
  try {
    const data: MenuCreate | MenuUpdate = {
      parent_id: form.parent_id,
      name: form.name,
      path: form.path,
      component: form.component,
      icon: form.icon,
      sort: form.sort,
      visible: form.visible,
      status: form.status,
      menu_type: form.menu_type,
      permission: form.permission,
      is_external: form.menu_type === 'link',
      external_url: form.external_url,
      link_target: form.link_target
    }

    if (form.id) {
      await menuApi.updateMenu(form.id, data)
      message.success('更新成功')
    } else {
      await menuApi.createMenu(data as MenuCreate)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadMenus()
  } catch (e) {
    const err = e as Error
    message.error(err.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await menuApi.deleteMenu(id)
    message.success('删除成功')
    loadMenus()
  } catch (e) {
    const err = e as Error
    message.error(err.message || '删除失败')
  }
}

onMounted(() => {
  loadMenus()
})
</script>

<style scoped lang="scss">
.menu-page {
  padding: 16px;

  .toolbar {
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .tip {
      font-size: 12px;
      color: #999;
    }
  }
}
</style>