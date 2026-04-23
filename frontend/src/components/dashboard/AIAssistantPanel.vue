<template>
  <div class="ai-assistant-panel">
    <div class="panel-header">
      <span class="panel-title">AI交易助手</span>
      <div class="ai-toggle">
        <n-switch
          :value="aiTradeEnabled"
          :loading="aiToggleLoading"
          @update:value="handleAiTradeToggle"
        >
          <template #checked>开启</template>
          <template #unchecked>关闭</template>
        </n-switch>
      </div>
    </div>
    <div class="panel-content chat-window">
      <div class="chat-messages" ref="chatMessagesRef">
        <div class="chat-message" v-for="(msg, idx) in chatMessages" :key="idx" :class="msg.role">
          <div class="message-content">{{ msg.content }}</div>
        </div>
        <div v-if="aiThinking" class="chat-message assistant">
          <div class="message-content thinking">思考中...</div>
        </div>
      </div>
      <div class="chat-input">
        <input
          v-model="userInput"
          @keyup.enter="sendChatMessage"
          placeholder="输入指令，如：买入平安银行100股"
          class="chat-input-field"
        />
        <button @click="sendChatMessage" :disabled="!userInput.trim() || aiThinking" class="chat-send-btn">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { NSwitch } from 'naive-ui'
import { sendAIMessage } from '@/api/ai'
import { useAuthStore } from '@/stores/auth'
import * as authApi from '@/api/auth'

interface ChatMsg {
  role: 'user' | 'assistant'
  content: string
  timestamp?: number
}

const CHAT_STORAGE_KEY = 'stock_policy_ai_chat_history'
const MAX_CHAT_HISTORY = 100

const chatMessages = ref<ChatMsg[]>([])
const userInput = ref('')
const aiThinking = ref(false)
const chatMessagesRef = ref<HTMLElement | null>(null)

// AI交易开关状态
const authStore = useAuthStore()
const aiTradeEnabled = computed(() => authStore.user?.qmt_enabled ?? false)
const aiToggleLoading = ref(false)

// 加载本地存储的聊天历史
function loadChatHistory() {
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY)
    if (stored) {
      const messages = JSON.parse(stored) as ChatMsg[]
      chatMessages.value = messages.slice(-MAX_CHAT_HISTORY)
    } else {
      chatMessages.value = [
        { role: 'assistant', content: '您好！我是AI交易助手，可以帮您查询行情、查看持仓、买卖股票。例如：\n• 平安银行现在多少钱\n• 我的持仓\n• 买入平安银行100股', timestamp: Date.now() }
      ]
    }
    scrollChatToBottom()
  } catch (e) {
    console.error('加载聊天历史失败', e)
    chatMessages.value = [
      { role: 'assistant', content: '您好！我是AI交易助手，可以帮您查询行情、查看持仓、买卖股票。', timestamp: Date.now() }
    ]
    scrollChatToBottom()
  }
}

// 保存聊天历史到本地存储
function saveChatHistory() {
  try {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(chatMessages.value.slice(-MAX_CHAT_HISTORY)))
  } catch (e) {
    console.error('保存聊天历史失败', e)
  }
}

// 滚动聊天到底部
function scrollChatToBottom() {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// 切换AI交易状态
async function handleAiTradeToggle(value: boolean) {
  if (!authStore.user?.id) {
    await authStore.fetchProfile()
    if (!authStore.user?.id) return
  }

  aiToggleLoading.value = true
  try {
    await authApi.updateQmtAccount(authStore.user.id, {
      qmt_enabled: value
    })
    await authStore.fetchProfile()
  } catch (e) {
    console.error('切换AI交易状态失败', e)
  } finally {
    aiToggleLoading.value = false
  }
}

// 发送聊天消息
async function sendChatMessage() {
  if (!userInput.value.trim() || aiThinking.value) return

  const message = userInput.value.trim()
  chatMessages.value.push({ role: 'user', content: message, timestamp: Date.now() })
  saveChatHistory()
  scrollChatToBottom()
  userInput.value = ''
  aiThinking.value = true

  try {
    const result = await sendAIMessage(message)
    chatMessages.value.push({
      role: 'assistant',
      content: result.content,
      timestamp: Date.now()
    })
    saveChatHistory()
    scrollChatToBottom()
  } catch (e) {
    chatMessages.value.push({
      role: 'assistant',
      content: '抱歉，处理您的请求时出错：' + ((e as Error).message || '未知错误'),
      timestamp: Date.now()
    })
    saveChatHistory()
    scrollChatToBottom()
  } finally {
    aiThinking.value = false
  }
}

onMounted(() => {
  loadChatHistory()
})

// 暴露给父组件
defineExpose({
  clearChat: () => {
    chatMessages.value = [
      { role: 'assistant', content: '您好！我是AI交易助手。', timestamp: Date.now() }
    ]
    localStorage.removeItem(CHAT_STORAGE_KEY)
  }
})
</script>

<style scoped lang="scss">
.ai-assistant-panel {
  height: 100%;
  background: rgba(20, 40, 80, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);
  display: flex;
  flex-direction: column;

  .panel-header {
    height: 35px;
    flex-shrink: 0;
    padding: 0 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(100, 150, 255, 0.2);

    .panel-title {
      font-size: 14px;
      color: #00aaff;
      font-weight: 500;
    }

    .ai-toggle {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
    }
  }

  .panel-content {
    flex: 1;
    min-height: 0;

    &.chat-window {
      display: flex;
      flex-direction: column;
      padding: 0;

      .chat-messages {
        flex: 1;
        min-height: 60px;
        overflow-y: auto;
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        scrollbar-width: thin;
        scrollbar-color: rgba(100, 150, 255, 0.5) rgba(0, 0, 0, 0.2);

        &::-webkit-scrollbar {
          width: 6px;
        }

        &::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 3px;
        }

        &::-webkit-scrollbar-thumb {
          background: rgba(100, 150, 255, 0.5);
          border-radius: 3px;
        }
      }

      .chat-message {
        max-width: 90%;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre-wrap;

        &.user {
          align-self: flex-end;
          background: rgba(0, 170, 255, 0.3);
          color: #fff;
        }

        &.assistant {
          align-self: flex-start;
          background: rgba(100, 150, 255, 0.15);
          color: rgba(255, 255, 255, 0.9);
        }

        .thinking {
          color: rgba(255, 255, 255, 0.5);
          font-style: italic;
        }
      }

      .chat-input {
        flex: 0 0 auto;
        display: flex;
        gap: 8px;
        padding: 8px;
        border-top: 1px solid rgba(100, 150, 255, 0.2);
        background: rgba(20, 40, 80, 0.3);
        min-height: 44px;

        .chat-input-field {
          flex: 1;
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(100, 150, 255, 0.3);
          border-radius: 4px;
          padding: 8px 12px;
          color: #fff;
          font-size: 13px;
          outline: none;

          &::placeholder {
            color: rgba(255, 255, 255, 0.4);
          }

          &:focus {
            border-color: rgba(0, 170, 255, 0.6);
          }
        }

        .chat-send-btn {
          padding: 8px 16px;
          background: rgba(0, 170, 255, 0.3);
          border: 1px solid rgba(0, 170, 255, 0.5);
          border-radius: 4px;
          color: #fff;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s;

          &:hover:not(:disabled) {
            background: rgba(0, 170, 255, 0.5);
          }

          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
        }
      }
    }
  }
}
</style>