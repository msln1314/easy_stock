<template>
  <div class="role-page">
    <n-card title="角色管理">
      <div class="toolbar">
        <n-space>
          <n-select
            v-model:value="filter.status"
            :options="statusOptions"
            placeholder="选择状态"
            clearable
            style="width: 120px"
            @update:value="loadRoles"
          />
          <n-input
            v-model:value="filter.keyword"
            placeholder="搜索角色名称"
            clearable
            style="width: 200px"
            @keyup.enter="loadRoles"
          />
          <n-button type="primary" @click="openModal()">
            新增角色
          </n-button>
        </n-space>
      </div>
      <n-data-table
        :columns="columns"
        :data="roleList"
        :loading="loading"
        :pagination="pagination"
        :row-key="getRowKey"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="modalVisible" preset="dialog" title="编辑角色" style="width: 500px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="80">
        <n-form-item label="角色名称" path="name">
          <n-input v-model:value="form.name" placeholder="请输入角色名称" />
        </n-form-item>
        <n-form-item label="角色编码" path="code">
          <n-input v-model:value="form.code" placeholder="请输入角色编码" :disabled="!!form.id" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="form.description" type="textarea" placeholder="请输入描述" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-radio-group v-model:value="form.status">
            <n-radio-button value="active">启用</n-radio-button>
            <n-radio-button value="inactive">禁用</n-radio-button>
          </n-radio-group>
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" :loading="submitLoading" @click="submit">确定</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 分配权限弹窗 -->
    <n-modal v-model:show="permModalVisible" preset="dialog" title="分配菜单权限" style="width: 600px">
      <n-tree
        v-model:checked-keys="checkedMenuIds"
        :data="menuTreeData"
        checkable
        cascade
        selectable
        block-line
        key-field="id"
        label-field="name"
        children-field="children"
      />
      <template #action>
        <n-space justify="end">
          <n-button @click="permModalVisible = false">取消</n-button>
          <n-button type="primary" :loading="permSubmitLoading" @click="submitPermissions">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { NButton, NTag, NSpace, useMessage, type DataTableColumns, type FormInst, type FormRules } from 'naive-ui'
import type { RoleListResponse, RoleCreate, RoleUpdate } from '@/types/role'
import type { MenuListResponse, MenuTreeResponse } from '@/types/menu'
import * as roleApi from '@/api/role'
import * as menuApi from '@/api/menu'

const message = useMessage()

const loading = ref(false)
const roleList = ref<RoleListResponse[]>([])
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  onChange: (page: number) => {
    pagination.page = page
    loadRoles()
  }
})
const filter = reactive({ status: null as string | null, keyword: '' })

const modalVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInst | null>(null)
const form = reactive<{
  id?: number
  name: string
  code: string
  description?: string
  status: string
}>({
  name: '',
  code: '',
  description: '',
  status: 'active'
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入角色名称' }],
  code: [{ required: true, message: '请输入角色编码' }]
}

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' }
]

function getRowKey(row: RoleListResponse) {
  return row.id
}

const columns: DataTableColumns<RoleListResponse> = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '角色名称', key: 'name', width: 150 },
  { title: '角色编码', key: 'code', width: 150 },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '状态', key: 'status', width: 80, render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'error' }, () => row.status === 'active' ? '启用' : '禁用') },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 200, render: (row) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', onClick: () => openModal(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'info', onClick: () => openPermModal(row.id) }, () => '分配权限'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row.id) }, () => '删除')
    ])
  }
]

// 权限分配相关
const permModalVisible = ref(false)
const permSubmitLoading = ref(false)
const currentRoleId = ref<number | null>(null)
const checkedMenuIds = ref<number[]>([])
const menuTreeData = ref<MenuTreeResponse[]>([])

async function loadRoles() {
  loading.value = true
  try {
    const res = await roleApi.getRoles({
      status: filter.status || undefined,
      keyword: filter.keyword || undefined,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    roleList.value = res.items
    pagination.itemCount = res.total
  } catch (e: any) {
    message.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function loadMenuTree() {
  try {
    const res: MenuListResponse[] = await menuApi.getAllMenus()
    // 构建树形结构
    const map: Record<number, MenuTreeResponse> = {}
    const roots: MenuTreeResponse[] = []
    for (const m of res) {
      map[m.id] = {
        id: m.id,
        parent_id: m.parent_id,
        name: m.name,
        path: m.path,
        icon: m.icon,
        sort: m.sort,
        visible: m.visible,
        status: m.status,
        menu_type: m.menu_type,
        permission: m.permission,
        children: [],
        created_at: m.created_at,
        updated_at: ''
      }
    }
    for (const m of res) {
      const node = map[m.id]
      if (m.parent_id && map[m.parent_id]) {
        map[m.parent_id].children.push(node)
      } else {
        roots.push(node)
      }
    }
    menuTreeData.value = roots
  } catch (e: any) {
    message.error(e.message || '加载菜单失败')
  }
}

function openModal(row?: RoleListResponse) {
  if (row) {
    form.id = row.id
    form.name = row.name
    form.code = row.code
    form.description = row.description || ''
    form.status = row.status
  } else {
    form.id = undefined
    form.name = ''
    form.code = ''
    form.description = ''
    form.status = 'active'
  }
  modalVisible.value = true
}

async function openPermModal(roleId: number) {
  currentRoleId.value = roleId
  // 加载角色当前权限
  try {
    const role = await roleApi.getRole(roleId)
    checkedMenuIds.value = role.menu_ids || []
  } catch (e: any) {
    message.error(e.message || '加载角色权限失败')
    return
  }
  await loadMenuTree()
  permModalVisible.value = true
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitLoading.value = true
  try {
    const data: RoleCreate | RoleUpdate = {
      name: form.name,
      code: form.code,
      description: form.description,
      status: form.status
    }

    if (form.id) {
      await roleApi.updateRole(form.id, data)
      message.success('更新成功')
    } else {
      await roleApi.createRole(data as RoleCreate)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadRoles()
  } catch (e: any) {
    message.error(e.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function submitPermissions() {
  if (!currentRoleId.value) return

  permSubmitLoading.value = true
  try {
    await roleApi.assignMenus(currentRoleId.value, { menu_ids: checkedMenuIds.value })
    message.success('权限分配成功')
    permModalVisible.value = false
  } catch (e: any) {
    message.error(e.message || '权限分配失败')
  } finally {
    permSubmitLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await roleApi.deleteRole(id)
    message.success('删除成功')
    loadRoles()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped lang="scss">
.role-page {
  padding: 16px;

  .toolbar {
    margin-bottom: 16px;
  }
}
</style>