<template>
  <div class="profile-page">
    <n-card title="用户信息">
      <n-tabs v-model:value="activeTab" type="line">
        <n-tab-pane name="info" tab="基本信息">
          <n-form ref="infoFormRef" :model="infoForm" :rules="infoRules" label-placement="left" label-width="80">
            <n-form-item label="用户名">
              <n-input :value="user?.username" disabled />
            </n-form-item>
            <n-form-item label="角色">
              <n-tag :type="user?.role === 'admin' ? 'success' : 'default'">
                {{ user?.role === 'admin' ? '管理员' : '普通用户' }}
              </n-tag>
            </n-form-item>
            <n-form-item label="邮箱" path="email">
              <n-input v-model:value="infoForm.email" placeholder="请输入邮箱" />
            </n-form-item>
            <n-form-item label="昵称" path="nickname">
              <n-input v-model:value="infoForm.nickname" placeholder="请输入昵称" />
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="infoLoading" @click="handleUpdateInfo">
                保存修改
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>
        <n-tab-pane name="password" tab="修改密码">
          <n-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-placement="left" label-width="100">
            <n-form-item label="当前密码" path="old_password">
              <n-input
                v-model:value="pwdForm.old_password"
                type="password"
                placeholder="请输入当前密码"
                show-password-on="click"
              />
            </n-form-item>
            <n-form-item label="新密码" path="new_password">
              <n-input
                v-model:value="pwdForm.new_password"
                type="password"
                placeholder="请输入新密码（至少6位）"
                show-password-on="click"
              />
            </n-form-item>
            <n-form-item label="确认新密码" path="confirm_password">
              <n-input
                v-model:value="pwdForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
                show-password-on="click"
              />
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="pwdLoading" @click="handleChangePassword">
                修改密码
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage, type FormInst, type FormRules } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

const message = useMessage()
const authStore = useAuthStore()

const activeTab = ref('info')
const user = ref(authStore.user)

const infoFormRef = ref<FormInst | null>(null)
const infoLoading = ref(false)
const infoForm = reactive({
  email: '',
  nickname: ''
})

const infoRules: FormRules = {
  email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const pwdFormRef = ref<FormInst | null>(null)
const pwdLoading = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const pwdRules: FormRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule, value) => {
        return value === pwdForm.new_password
      },
      message: '两次输入的密码不一致',
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  if (user.value) {
    infoForm.email = user.value.email || ''
    infoForm.nickname = user.value.nickname || ''
  }
})

async function handleUpdateInfo() {
  try {
    await infoFormRef.value?.validate()
  } catch {
    return
  }

  infoLoading.value = true
  try {
    await authStore.updateProfile({
      email: infoForm.email || undefined,
      nickname: infoForm.nickname || undefined
    })
    message.success('信息更新成功')
  } catch (e: any) {
    message.error(e.message || '更新失败')
  } finally {
    infoLoading.value = false
  }
}

async function handleChangePassword() {
  try {
    await pwdFormRef.value?.validate()
  } catch {
    return
  }

  pwdLoading.value = true
  try {
    await authStore.updatePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    message.success('密码修改成功')
    // 清空表单
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
  } catch (e: any) {
    message.error(e.message || '修改失败')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.profile-page {
  padding: 16px;
  max-width: 600px;
}
</style>