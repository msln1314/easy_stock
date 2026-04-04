/**
 * 外部链接嵌入组件
 * 用于在系统中嵌入外部链接（iframe模式）
 */
<template>
  <div class="external-link-container">
    <div class="iframe-header" v-if="title">
      <span class="iframe-title">{{ title }}</span>
      <n-button size="small" quaternary @click="refreshIframe">
        <template #icon>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
        </template>
        刷新
      </n-button>
      <n-button size="small" quaternary @click="openInNewTab">
        <template #icon>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
          </svg>
        </template>
        新窗口打开
      </n-button>
    </div>
    <div class="iframe-wrapper">
      <iframe
        ref="iframeRef"
        :src="url"
        :title="title"
        class="embedded-iframe"
        frameborder="0"
        allowfullscreen
        @load="onIframeLoad"
      />
      <div class="iframe-loading" v-if="loading">
        <n-spin size="large" />
        <p>正在加载...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const iframeRef = ref<HTMLIFrameElement | null>(null)
const loading = ref(true)

// 从路由参数解码URL
const url = computed(() => {
  const encodedUrl = route.params.encodedUrl as string
  try {
    return decodeURIComponent(encodedUrl)
  } catch {
    return ''
  }
})

const title = computed(() => {
  return (route.query.title as string) || '外部链接'
})

function onIframeLoad() {
  loading.value = false
}

function refreshIframe() {
  loading.value = true
  if (iframeRef.value) {
    iframeRef.value.src = url.value
  }
}

function openInNewTab() {
  window.open(url.value, '_blank')
}
</script>

<style scoped lang="scss">
.external-link-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.iframe-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  gap: 12px;

  .iframe-title {
    font-weight: 500;
    font-size: 14px;
    color: #333;
  }
}

.iframe-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.embedded-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.iframe-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  gap: 12px;

  p {
    color: #999;
    font-size: 14px;
  }
}
</style>