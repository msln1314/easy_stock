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
            <n-form-item label="API Key">
              <n-space>
                <n-input :value="apiKey" disabled style="width: 180px" />
                <n-button type="primary" @click="handleRefreshApiKey" :loading="apiKeyLoading">
                  刷新
                </n-button>
              </n-space>
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="infoLoading" @click="handleUpdateInfo">
                保存修改
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>
        <n-tab-pane name="qmt" tab="QMT配置">
          <n-form ref="qmtFormRef" :model="qmtForm" label-placement="left" label-width="120">
            <n-form-item label="QMT账户ID">
              <n-input v-model:value="qmtForm.qmt_account_id" placeholder="请输入QMT账户ID" />
            </n-form-item>
            <n-form-item label="QMT客户端路径">
              <n-input v-model:value="qmtForm.qmt_client_path" placeholder="如: C:\\国信QMT\\userdata_mini" />
            </n-form-item>
            <n-form-item label="QMT会话ID">
              <n-input-number v-model:value="qmtForm.qmt_session_id" :min="1" placeholder="默认123456" />
            </n-form-item>
            <n-form-item label="启用QMT交易">
              <n-switch v-model:value="qmtForm.qmt_enabled" />
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="qmtLoading" @click="handleUpdateQmt">
                保存配置
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
import * as authApi from '@/api/auth'

const message = useMessage()
const authStore = useAuthStore()

const activeTab = ref('info')
const user = ref(authStore.user)
const apiKey = ref('')
const apiKeyLoading = ref(false)

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

const qmtFormRef = ref<FormInst | null>(null)
const qmtLoading = ref(false)
const qmtForm = reactive({
  qmt_account_id: '',
  qmt_client_path: '',
  qmt_session_id: 123456,
  qmt_enabled: false
})

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

onMounted(async () => {
  if (user.value) {
    infoForm.email = user.value.email || ''
    infoForm.nickname = user.value.nickname || ''
    // 加载 API Key
    await loadApiKey()
    // 加载 QMT 配置
    await loadQmtConfig()
  }
})

async function loadApiKey() {
  try {
    const res = await authApi.getApiKey()
    apiKey.value = res.api_key || ''
  } catch (e: any) {
    console.log('API Key加载失败:', e.message)
  }
}

async function handleRefreshApiKey() {
  apiKeyLoading.value = true
  try {
    const res = await authApi.refreshApiKey()
    apiKey.value = res.api_key
    message.success('API Key 已刷新')
  } catch (e: any) {
    message.error(e.message || '刷新失败')
  } finally {
    apiKeyLoading.value = false
  }
}

async function loadQmtConfig() {
  if (!user.value?.id) return
  try {
    const config = await authApi.getQmtAccount(user.value.id)
    qmtForm.qmt_account_id = config.qmt_account_id || ''
    qmtForm.qmt_client_path = config.qmt_client_path || ''
    qmtForm.qmt_session_id = config.qmt_session_id || 123456
    qmtForm.qmt_enabled = config.qmt_enabled
  } catch (e: any) {
    console.log('QMT配置加载失败:', e.message)
  }
}

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

async function handleUpdateQmt() {
  if (!user.value?.id) return

  qmtLoading.value = true
  try {
    await authApi.updateQmtAccount(user.value.id, {
      qmt_account_id: qmtForm.qmt_account_id || undefined,
      qmt_client_path: qmtForm.qmt_client_path || undefined,
      qmt_session_id: qmtForm.qmt_session_id,
      qmt_enabled: qmtForm.qmt_enabled
    })
    message.success('QMT配置更新成功')
  } catch (e: any) {
    message.error(e.message || '更新失败')
  } finally {
    qmtLoading.value = false
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