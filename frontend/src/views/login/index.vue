<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
    <n-card class="login-card">
      <div class="login-header">
        <div class="logo-container">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="#667eea">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <h1 class="site-name">{{ siteConfig.site_name || '策略中心系统' }}</h1>
        <p class="site-version" v-if="siteConfig.site_version">v{{ siteConfig.site_version }}</p>
      </div>

      <n-form ref="formRef" :model="formValue" :rules="rules" label-placement="top">
        <n-form-item label="用户名" path="username">
          <n-input
            v-model:value="formValue.username"
            placeholder="请输入用户名"
            size="large"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="formValue.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password-on="click"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
              </svg>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="验证码" path="captcha_code" v-if="captchaEnabled">
          <div class="captcha-row">
            <n-input
              v-model:value="formValue.captcha_code"
              placeholder="请输入验证码"
              size="large"
              @keyup.enter="handleLogin"
            />
            <div class="captcha-image" @click="refreshCaptcha">
              <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
              <n-spin v-else size="small" />
            </div>
          </div>
        </n-form-item>

        <n-form-item>
          <n-button type="primary" block size="large" :loading="loading" @click="handleLogin">
            登 录
          </n-button>
        </n-form-item>
      </n-form>

      <div class="login-footer">
        <p class="footer-text">{{ siteConfig.footer_text || '© 2024 策略中心系统' }}</p>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { getCaptcha } from '@/api/captcha'
import { getPublicConfigs } from '@/api/config'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const captchaEnabled = ref(false)
const captchaImage = ref('')
const captchaId = ref('')
const siteConfig = ref({
  site_name: '',
  site_version: '',
  footer_text: ''
})

const formValue = ref({
  username: '',
  password: '',
  captcha_code: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  captcha_code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

async function loadSiteConfig() {
  try {
    const configs = await getPublicConfigs()
    siteConfig.value = {
      site_name: configs.site_name || '',
      site_version: configs.site_version || '',
      footer_text: configs.footer_text || ''
    }
    captchaEnabled.value = configs.login_captcha_enabled === 'true'

    if (captchaEnabled.value) {
      await refreshCaptcha()
    }
  } catch (e) {
    // 使用默认配置
  }
}

async function refreshCaptcha() {
  try {
    const res = await getCaptcha()
    if (res.code === 200) {
      captchaId.value = res.data.captcha_id
      captchaImage.value = res.data.image
      formValue.value.captcha_code = ''
    }
  } catch (e) {
    message.error('获取验证码失败')
  }
}

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const loginData = {
      username: formValue.value.username,
      password: formValue.value.password,
      captcha_id: captchaEnabled.value ? captchaId.value : undefined,
      captcha_code: captchaEnabled.value ? formValue.value.captcha_code : undefined
    }
    await authStore.login(loginData)
    message.success('登录成功')
    router.push('/')
  } catch (e) {
    const err = e as Error
    message.error(err.message || '登录失败')
    if (captchaEnabled.value) {
      await refreshCaptcha()
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSiteConfig()
})
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  inset: 0;
  overflow: hidden;

  .bg-shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;

    &.shape-1 {
      width: 600px;
      height: 600px;
      background: white;
      top: -200px;
      left: -100px;
    }

    &.shape-2 {
      width: 400px;
      height: 400px;
      background: white;
      bottom: -100px;
      right: -50px;
    }

    &.shape-3 {
      width: 200px;
      height: 200px;
      background: white;
      top: 50%;
      right: 20%;
    }
  }
}

.login-card {
  width: 420px;
  max-width: 90%;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  padding: 40px 30px;

  :deep(.n-card__content) {
    padding: 0;
  }
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  .logo-container {
    margin-bottom: 16px;
  }

  .site-name {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin: 0;
    letter-spacing: 2px;
  }

  .site-version {
    font-size: 12px;
    color: #999;
    margin-top: 8px;
  }
}

.captcha-row {
  display: flex;
  gap: 12px;
  width: 100%;

  .n-input {
    flex: 1;
  }

  .captcha-image {
    width: 120px;
    height: 40px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    cursor: pointer;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    &:hover {
      border-color: #667eea;
    }
  }
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;

  .footer-text {
    font-size: 12px;
    color: #999;
    margin: 0;
  }
}

:deep(.n-form-item-label) {
  font-weight: 500;
}

:deep(.n-button--primary-type) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  height: 44px;
  font-size: 16px;

  &:hover {
    opacity: 0.9;
  }
}
</style>