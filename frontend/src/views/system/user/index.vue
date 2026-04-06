<template>
  <div class="user-page">
    <n-card title="用户管理">
      <div class="toolbar">
        <n-space>
          <n-select
            v-model:value="filter.role"
            :options="roleOptions"
            placeholder="选择角色"
            clearable
            style="width: 120px"
            @update:value="loadUsers"
          />
          <n-select
            v-model:value="filter.status"
            :options="statusOptions"
            placeholder="选择状态"
            clearable
            style="width: 120px"
            @update:value="loadUsers"
          />
          <n-input
            v-model:value="filter.keyword"
            placeholder="搜索用户名"
            clearable
            style="width: 200px"
            @keyup.enter="loadUsers"
          />
          <n-button type="primary" @click="openModal()">
            新增用户
          </n-button>
        </n-space>
      </div>
      <n-data-table
        :columns="columns"
        :data="userList"
        :loading="loading"
        :pagination="pagination"
        :row-key="getRowKey"
      />
    </n-card>

    <!-- 编辑弹窗 -->
    <n-modal v-model:show="modalVisible" preset="dialog" title="编辑用户" style="width: 500px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="80">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="form.username" placeholder="请输入用户名" :disabled="!!form.id" />
        </n-form-item>
        <n-form-item v-if="!form.id" label="密码" path="password">
          <n-input v-model:value="form.password" type="password" placeholder="请输入密码" />
        </n-form-item>
        <n-form-item label="邮箱" path="email">
          <n-input v-model:value="form.email" placeholder="请输入邮箱" />
        </n-form-item>
        <n-form-item label="昵称" path="nickname">
          <n-input v-model:value="form.nickname" placeholder="请输入昵称" />
        </n-form-item>
        <n-form-item label="角色" path="role">
          <n-select v-model:value="form.role" :options="roleOptions" />
        </n-form-item>
        <n-form-item label="状态" path="status">
          <n-radio-group v-model:value="form.status">
            <n-radio-button value="active">启用</n-radio-button>
            <n-radio-button value="disabled">禁用</n-radio-button>
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

    <!-- 重置密码弹窗 -->
    <n-modal v-model:show="pwdModalVisible" preset="dialog" title="重置密码" style="width: 400px">
      <n-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-placement="left" label-width="80">
        <n-form-item label="新密码" path="new_password">
          <n-input v-model:value="pwdForm.new_password" type="password" placeholder="请输入新密码" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space justify="end">
          <n-button @click="pwdModalVisible = false">取消</n-button>
          <n-button type="primary" :loading="pwdSubmitLoading" @click="submitPassword">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { NButton, NTag, NSpace, useMessage, type DataTableColumns, type FormInst, type FormRules } from 'naive-ui'
import type { UserListResponse, UserCreate, UserUpdate } from '@/types/user'
import * as userApi from '@/api/user'

const message = useMessage()

const loading = ref(false)
const userList = ref<UserListResponse[]>([])
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  onChange: (page: number) => {
    pagination.page = page
    loadUsers()
  }
})
const filter = reactive({ role: null as string | null, status: null as string | null, keyword: '' })

const modalVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInst | null>(null)
const form = reactive<{
  id?: number
  username: string
  password: string
  email?: string
  nickname?: string
  role: string
  status: string
}>({
  username: '',
  password: '',
  email: '',
  nickname: '',
  role: 'user',
  status: 'active'
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }]
}

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' }
]

const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'disabled' }
]

function getRowKey(row: UserListResponse) {
  return row.id
}

const columns: DataTableColumns<UserListResponse> = [
  { title: 'ID', key: 'id', width: 80 },
  { title: '用户名', key: 'username', width: 120 },
  { title: '昵称', key: 'nickname', width: 120 },
  { title: '邮箱', key: 'email', width: 180 },
  { title: '角色', key: 'role', width: 100, render: (row) => h(NTag, { type: row.role === 'admin' ? 'success' : 'default' }, () => row.role === 'admin' ? '管理员' : '普通用户') },
  { title: '状态', key: 'status', width: 80, render: (row) => h(NTag, { type: row.status === 'active' ? 'success' : 'error' }, () => row.status === 'active' ? '启用' : '禁用') },
  { title: '最后登录', key: 'last_login', width: 180 },
  { title: '创建时间', key: 'created_at', width: 180 },
  {
    title: '操作', key: 'actions', width: 200, render: (row) => h(NSpace, {}, () => [
      h(NButton, { size: 'small', onClick: () => openModal(row) }, () => '编辑'),
      h(NButton, { size: 'small', type: 'warning', onClick: () => openPwdModal(row.id) }, () => '重置密码'),
      h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row.id), disabled: row.username === 'admin' }, () => '删除')
    ])
  }
]

// 重置密码相关
const pwdModalVisible = ref(false)
const pwdSubmitLoading = ref(false)
const pwdFormRef = ref<FormInst | null>(null)
const pwdForm = reactive({
  user_id: 0,
  new_password: ''
})
const pwdRules: FormRules = {
  new_password: [{ required: true, message: '请输入新密码' }]
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await userApi.getUsers({
      role: filter.role || undefined,
      status: filter.status || undefined,
      keyword: filter.keyword || undefined,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    userList.value = res.items
    pagination.itemCount = res.total
  } catch (e: any) {
    message.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function openModal(row?: UserListResponse) {
  if (row) {
    form.id = row.id
    form.username = row.username
    form.password = ''
    form.email = row.email || ''
    form.nickname = row.nickname || ''
    form.role = row.role
    form.status = row.status
  } else {
    form.id = undefined
    form.username = ''
    form.password = ''
    form.email = ''
    form.nickname = ''
    form.role = 'user'
    form.status = 'active'
  }
  modalVisible.value = true
}

function openPwdModal(userId: number) {
  pwdForm.user_id = userId
  pwdForm.new_password = ''
  pwdModalVisible.value = true
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitLoading.value = true
  try {
    if (form.id) {
      const data: UserUpdate = {
        email: form.email,
        nickname: form.nickname,
        status: form.status
      }
      await userApi.updateUser(form.id, data)
      message.success('更新成功')
    } else {
      const data: UserCreate = {
        username: form.username,
        password: form.password,
        email: form.email,
        nickname: form.nickname,
        role: form.role as any
      }
      await userApi.createUser(data)
      message.success('创建成功')
    }
    modalVisible.value = false
    loadUsers()
  } catch (e: any) {
    message.error(e.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

async function submitPassword() {
  try {
    await pwdFormRef.value?.validate()
  } catch {
    return
  }

  pwdSubmitLoading.value = true
  try {
    await userApi.resetPassword(pwdForm.user_id, { new_password: pwdForm.new_password })
    message.success('密码重置成功')
    pwdModalVisible.value = false
  } catch (e: any) {
    message.error(e.message || '密码重置失败')
  } finally {
    pwdSubmitLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await userApi.deleteUser(id)
    message.success('删除成功')
    loadUsers()
  } catch (e: any) {
    message.error(e.message || '删除失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped lang="scss">
.user-page {
  padding: 16px;

  .toolbar {
    margin-bottom: 16px;
  }
}
</style>