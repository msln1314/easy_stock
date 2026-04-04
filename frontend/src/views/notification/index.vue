<template>
  <div class="notification-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>通知配置</h2>
        <n-button type="primary" @click="showAddModal = true">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          添加渠道
        </n-button>
      </div>
      <div class="header-right">
        <n-button @click="showLogsModal = true">
          <template #icon>
            <n-icon><ListOutline /></n-icon>
          </template>
          查看记录
        </n-button>
      </div>
    </div>

    <!-- 渠道列表 -->
    <div class="channel-panel">
      <n-spin :show="loading">
        <div class="channel-grid">
          <div v-for="channel in channels" :key="channel.id" class="channel-card">
            <div class="channel-header">
              <div class="channel-icon">
                <n-icon size="24">
                  <component :is="getChannelIcon(channel.channel_type)" />
                </n-icon>
              </div>
              <div class="channel-info">
                <h3>{{ channel.channel_name }}</h3>
                <n-tag :type="getChannelTagType(channel.channel_type)" size="small">
                  {{ getChannelTypeName(channel.channel_type) }}
                </n-tag>
              </div>
              <n-switch v-model:value="channel.is_enabled" @update:value="toggleChannel(channel)" />
            </div>

            <div class="channel-config">
              <div class="config-item">
                <span class="label">预警级别：</span>
                <n-space size="small">
                  <n-tag v-for="level in channel.warning_levels" :key="level"
                         :type="getLevelTagType(level)" size="small">
                    {{ level }}
                  </n-tag>
                </n-space>
              </div>
              <div class="config-item">
                <span class="label">监控类型：</span>
                <n-space size="small">
                  <n-tag v-for="type in channel.monitor_types" :key="type" size="small">
                    {{ type === 'hold' ? '持仓' : '关注' }}
                  </n-tag>
                </n-space>
              </div>
              <div class="config-item">
                <span class="label">频率限制：</span>
                <span>{{ channel.rate_limit_minutes }} 分钟</span>
              </div>
              <div class="config-item" v-if="channel.last_sent_at">
                <span class="label">最后发送：</span>
                <span>{{ formatTime(channel.last_sent_at) }}</span>
              </div>
            </div>

            <div class="channel-actions">
              <n-button size="small" type="info" @click="testChannel(channel)" :loading="channel._testing">
                测试
              </n-button>
              <n-button size="small" @click="openEditModal(channel)">
                编辑
              </n-button>
              <n-button size="small" type="error" @click="deleteChannel(channel)">
                删除
              </n-button>
            </div>
          </div>
        </div>
        <n-empty v-if="!loading && channels.length === 0" description="暂无通知渠道" class="py-8" />
      </n-spin>
    </div>

    <!-- 添加渠道弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="添加通知渠道" style="width: 700px">
      <n-form ref="addFormRef" :model="addForm" label-placement="left" label-width="100">
        <n-form-item label="渠道类型" required>
          <n-select v-model:value="addForm.channel_type" :options="channelTypeOptions"
                    @update:value="onChannelTypeChange" placeholder="选择渠道类型" />
        </n-form-item>
        <n-form-item label="渠道名称" required>
          <n-input v-model:value="addForm.channel_name" placeholder="如：钉钉预警群" />
        </n-form-item>

        <!-- 动态配置字段 -->
        <n-divider>渠道配置</n-divider>
        <template v-if="addForm.channel_type === 'dingtalk'">
          <n-form-item label="Webhook URL" required>
            <n-input v-model:value="addForm.config.webhook_url" placeholder="钉钉机器人Webhook地址" />
          </n-form-item>
          <n-form-item label="签名密钥">
            <n-input v-model:value="addForm.config.secret" placeholder="选填，用于签名验证" />
          </n-form-item>
        </template>
        <template v-else-if="addForm.channel_type === 'telegram'">
          <n-form-item label="Bot Token" required>
            <n-input v-model:value="addForm.config.bot_token" placeholder="Telegram Bot Token" />
          </n-form-item>
          <n-form-item label="Chat ID" required>
            <n-input v-model:value="addForm.config.chat_id" placeholder="接收消息的Chat ID" />
          </n-form-item>
        </template>
        <template v-else-if="addForm.channel_type === 'wechat_work'">
          <n-form-item label="Webhook URL" required>
            <n-input v-model:value="addForm.config.webhook_url" placeholder="企业微信机器人Webhook地址" />
          </n-form-item>
        </template>
        <template v-else-if="addForm.channel_type === 'webhook'">
          <n-form-item label="URL" required>
            <n-input v-model:value="addForm.config.url" placeholder="自定义Webhook地址" />
          </n-form-item>
          <n-form-item label="请求方法">
            <n-select v-model:value="addForm.config.method" :options="['POST', 'GET'].map(v => ({label: v, value: v}))" />
          </n-form-item>
          <n-form-item label="请求头">
            <n-input v-model:value="addForm.config.headers_json" type="textarea"
                     placeholder="JSON格式的请求头，如：{\"Authorization\": \"Bearer xxx\"}" />
          </n-form-item>
        </template>
        <template v-else-if="addForm.channel_type === 'email'">
          <n-form-item label="SMTP服务器" required>
            <n-input v-model:value="addForm.config.smtp_server" placeholder="如：smtp.qq.com" />
          </n-form-item>
          <n-form-item label="SMTP端口">
            <n-input-number v-model:value="addForm.config.smtp_port" :min="1" :max="65535" />
          </n-form-item>
          <n-form-item label="用户名" required>
            <n-input v-model:value="addForm.config.username" placeholder="邮箱账号" />
          </n-form-item>
          <n-form-item label="密码" required>
            <n-input v-model:value="addForm.config.password" type="password" placeholder="邮箱密码或授权码" />
          </n-form-item>
          <n-form-item label="发件地址" required>
            <n-input v-model:value="addForm.config.from_addr" placeholder="发件人邮箱" />
          </n-form-item>
          <n-form-item label="收件列表" required>
            <n-dynamic-tags v-model:value="addForm.config.to_list" />
          </n-form-item>
        </template>

        <n-divider>过滤规则</n-divider>
        <n-form-item label="预警级别">
          <n-checkbox-group v-model:value="addForm.warning_levels">
            <n-space>
              <n-checkbox value="critical" label="严重" />
              <n-checkbox value="warning" label="警告" />
              <n-checkbox value="info" label="信息" />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
        <n-form-item label="监控类型">
          <n-checkbox-group v-model:value="addForm.monitor_types">
            <n-space>
              <n-checkbox value="hold" label="持仓监控" />
              <n-checkbox value="watch" label="关注监控" />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
        <n-form-item label="频率限制">
          <n-input-number v-model:value="addForm.rate_limit_minutes" :min="1" :max="60" />
          <span class="ml-2">分钟内不重复发送</span>
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="addForm.remark" type="textarea" placeholder="备注信息" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleAddChannel" :loading="adding">添加</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 编辑渠道弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" title="编辑通知渠道" style="width: 700px">
      <n-form ref="editFormRef" :model="editForm" label-placement="left" label-width="100">
        <n-form-item label="渠道类型">
          <n-tag :type="getChannelTagType(editForm.channel_type)">
            {{ getChannelTypeName(editForm.channel_type) }}
          </n-tag>
        </n-form-item>
        <n-form-item label="渠道名称" required>
          <n-input v-model:value="editForm.channel_name" />
        </n-form-item>

        <!-- 动态配置字段 -->
        <n-divider>渠道配置</n-divider>
        <template v-if="editForm.channel_type === 'dingtalk'">
          <n-form-item label="Webhook URL" required>
            <n-input v-model:value="editForm.config.webhook_url" />
          </n-form-item>
          <n-form-item label="签名密钥">
            <n-input v-model:value="editForm.config.secret" />
          </n-form-item>
        </template>
        <template v-else-if="editForm.channel_type === 'telegram'">
          <n-form-item label="Bot Token" required>
            <n-input v-model:value="editForm.config.bot_token" />
          </n-form-item>
          <n-form-item label="Chat ID" required>
            <n-input v-model:value="editForm.config.chat_id" />
          </n-form-item>
        </template>
        <template v-else-if="editForm.channel_type === 'wechat_work'">
          <n-form-item label="Webhook URL" required>
            <n-input v-model:value="editForm.config.webhook_url" />
          </n-form-item>
        </template>
        <template v-else-if="editForm.channel_type === 'webhook'">
          <n-form-item label="URL" required>
            <n-input v-model:value="editForm.config.url" />
          </n-form-item>
          <n-form-item label="请求方法">
            <n-select v-model:value="editForm.config.method" :options="['POST', 'GET'].map(v => ({label: v, value: v}))" />
          </n-form-item>
          <n-form-item label="请求头">
            <n-input v-model:value="editForm.config.headers_json" type="textarea" />
          </n-form-item>
        </template>
        <template v-else-if="editForm.channel_type === 'email'">
          <n-form-item label="SMTP服务器" required>
            <n-input v-model:value="editForm.config.smtp_server" />
          </n-form-item>
          <n-form-item label="SMTP端口">
            <n-input-number v-model:value="editForm.config.smtp_port" :min="1" :max="65535" />
          </n-form-item>
          <n-form-item label="用户名" required>
            <n-input v-model:value="editForm.config.username" />
          </n-form-item>
          <n-form-item label="密码" required>
            <n-input v-model:value="editForm.config.password" type="password" />
          </n-form-item>
          <n-form-item label="发件地址" required>
            <n-input v-model:value="editForm.config.from_addr" />
          </n-form-item>
          <n-form-item label="收件列表" required>
            <n-dynamic-tags v-model:value="editForm.config.to_list" />
          </n-form-item>
        </template>

        <n-divider>过滤规则</n-divider>
        <n-form-item label="预警级别">
          <n-checkbox-group v-model:value="editForm.warning_levels">
            <n-space>
              <n-checkbox value="critical" label="严重" />
              <n-checkbox value="warning" label="警告" />
              <n-checkbox value="info" label="信息" />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
        <n-form-item label="监控类型">
          <n-checkbox-group v-model:value="editForm.monitor_types">
            <n-space>
              <n-checkbox value="hold" label="持仓监控" />
              <n-checkbox value="watch" label="关注监控" />
            </n-space>
          </n-checkbox-group>
        </n-form-item>
        <n-form-item label="频率限制">
          <n-input-number v-model:value="editForm.rate_limit_minutes" :min="1" :max="60" />
          <span class="ml-2">分钟内不重复发送</span>
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="editForm.remark" type="textarea" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleEditChannel" :loading="editing">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 通知记录弹窗 -->
    <n-modal v-model:show="showLogsModal" preset="card" title="通知记录" style="width: 900px">
      <div class="logs-header">
        <n-space>
          <n-select v-model:value="logFilter.status" :options="statusOptions"
                    placeholder="状态筛选" clearable size="small" style="width: 100px" />
          <n-select v-model:value="logFilter.channel_type" :options="channelTypeOptions"
                    placeholder="渠道筛选" clearable size="small" style="width: 120px" />
          <n-button size="small" @click="loadLogs">刷新</n-button>
        </n-space>
      </div>
      <n-data-table :columns="logColumns" :data="logs" :loading="logsLoading"
                    striped size="small" max-height="400" />
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, computed } from 'vue'
import {
  NButton, NIcon, NInput, NInputNumber, NSelect, NSwitch, NSpin, NTag, NModal,
  NDataTable, NEmpty, NForm, NFormItem, NCheckboxGroup, NCheckbox, NSpace,
  NDivider, NDynamicTags, useMessage
} from 'naive-ui'
import { AddOutline, ListOutline, ChatbubbleOutline, MailOutline, GlobeOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import {
  fetchNotificationChannels, fetchChannelTypes, createNotificationChannel,
  updateNotificationChannel, deleteNotificationChannel, testNotificationChannel,
  fetchNotificationLogs, NotificationChannel, ChannelTypeOption, NotificationLog
} from '@/api/notification'

const message = useMessage()

// 数据
const channels = ref<NotificationChannel[]>([])
const channelTypeOptions = ref<ChannelTypeOption[]>([])
const logs = ref<NotificationLog[]>([])
const loading = ref(false)
const adding = ref(false)
const editing = ref(false)
const logsLoading = ref(false)

// 弹窗
const showAddModal = ref(false)
const showEditModal = ref(false)
const showLogsModal = ref(false)

// 表单
const addFormRef = ref()
const addForm = ref({
  channel_type: '',
  channel_name: '',
  config: {} as Record<string, any>,
  warning_levels: ['critical', 'warning'] as string[],
  monitor_types: ['hold'] as string[],
  rate_limit_minutes: 5,
  remark: ''
})

const editFormRef = ref()
const editForm = ref<NotificationChannel>({
  id: 0,
  channel_type: '',
  channel_name: '',
  is_enabled: true,
  config: {},
  warning_levels: [],
  monitor_types: [],
  rate_limit_minutes: 5,
  remark: ''
})

// 日志筛选
const logFilter = ref({
  status: '',
  channel_type: ''
})

const statusOptions = [
  { label: '待发送', value: 'pending' },
  { label: '已发送', value: 'sent' },
  { label: '失败', value: 'failed' }
]

// 渠道图标
function getChannelIcon(type: string) {
  const icons: Record<string, any> = {
    dingtalk: ChatbubbleOutline,
    telegram: ChatbubbleOutline,
    wechat_work: ChatbubbleOutline,
    email: MailOutline,
    webhook: GlobeOutline
  }
  return icons[type] || ChatbubbleOutline
}

function getChannelTypeName(type: string) {
  const names: Record<string, string> = {
    dingtalk: '钉钉',
    telegram: 'Telegram',
    wechat_work: '企业微信',
    email: '邮件',
    webhook: 'Webhook'
  }
  return names[type] || type
}

function getChannelTagType(type: string) {
  const types: Record<string, string> = {
    dingtalk: 'info',
    telegram: 'success',
    wechat_work: 'warning',
    email: 'default',
    webhook: 'error'
  }
  return types[type] || 'default'
}

function getLevelTagType(level: string) {
  const types: Record<string, string> = {
    critical: 'error',
    warning: 'warning',
    info: 'info'
  }
  return types[level] || 'default'
}

function formatTime(time: string) {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

// 渠道类型变更时初始化配置
function onChannelTypeChange(type: string) {
  addForm.value.config = {}
  if (type === 'dingtalk') {
    addForm.value.config = { webhook_url: '', secret: '' }
  } else if (type === 'telegram') {
    addForm.value.config = { bot_token: '', chat_id: '' }
  } else if (type === 'wechat_work') {
    addForm.value.config = { webhook_url: '' }
  } else if (type === 'webhook') {
    addForm.value.config = { url: '', method: 'POST', headers_json: '' }
  } else if (type === 'email') {
    addForm.value.config = { smtp_server: '', smtp_port: 465, username: '', password: '', from_addr: '', to_list: [] }
  }
}

// 日志表格列
const logColumns = [
  { title: '时间', key: 'created_at', width: 140, render: (row: NotificationLog) => formatTime(row.created_at) },
  { title: '股票', key: 'stock_name', width: 100 },
  { title: '标题', key: 'title', width: 150, ellipsis: { tooltip: true } },
  { title: '级别', key: 'warning_level', width: 70, render: (row: NotificationLog) =>
    h(NTag, { type: getLevelTagType(row.warning_level), size: 'small' }, { default: () => row.warning_level })
  },
  { title: '渠道', key: 'channel_name', width: 100 },
  { title: '状态', key: 'status', width: 70, render: (row: NotificationLog) =>
    h(NTag, { type: row.status === 'sent' ? 'success' : row.status === 'failed' ? 'error' : 'default', size: 'small' },
       { default: () => row.status === 'sent' ? '成功' : row.status === 'failed' ? '失败' : '待发' })
  },
  { title: '错误', key: 'error_message', width: 150, ellipsis: { tooltip: true } }
]

// 加载渠道列表
async function loadChannels() {
  loading.value = true
  try {
    channels.value = await fetchNotificationChannels()
  } catch (error) {
    console.error('加载渠道失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadChannelTypes() {
  try {
    channelTypeOptions.value = await fetchChannelTypes()
  } catch (error) {
    console.error('加载渠道类型失败:', error)
  }
}

// 加载通知记录
async function loadLogs() {
  logsLoading.value = true
  try {
    logs.value = await fetchNotificationLogs({
      status: logFilter.value.status || undefined,
      channel_type: logFilter.value.channel_type || undefined,
      limit: 100
    })
  } catch (error) {
    console.error('加载记录失败:', error)
  } finally {
    logsLoading.value = false
  }
}

// 切换启用状态
async function toggleChannel(channel: NotificationChannel) {
  try {
    await updateNotificationChannel(channel.id, { is_enabled: channel.is_enabled })
    message.success(channel.is_enabled ? '已启用' : '已禁用')
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '操作失败')
    channel.is_enabled = !channel.is_enabled
  }
}

// 添加渠道
async function handleAddChannel() {
  if (!addForm.value.channel_type || !addForm.value.channel_name) {
    message.warning('请填写必填字段')
    return
  }

  // 处理webhook的headers
  let config = { ...addForm.value.config }
  if (addForm.value.channel_type === 'webhook' && config.headers_json) {
    try {
      config.headers = JSON.parse(config.headers_json)
      delete config.headers_json
    } catch {
      message.error('请求头JSON格式错误')
      return
    }
  }

  adding.value = true
  try {
    await createNotificationChannel({
      channel_type: addForm.value.channel_type,
      channel_name: addForm.value.channel_name,
      config,
      warning_levels: addForm.value.warning_levels,
      monitor_types: addForm.value.monitor_types,
      rate_limit_minutes: addForm.value.rate_limit_minutes,
      remark: addForm.value.remark
    })
    message.success('添加成功')
    showAddModal.value = false
    addForm.value = {
      channel_type: '',
      channel_name: '',
      config: {},
      warning_levels: ['critical', 'warning'],
      monitor_types: ['hold'],
      rate_limit_minutes: 5,
      remark: ''
    }
    loadChannels()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

// 编辑渠道
function openEditModal(channel: NotificationChannel) {
  editForm.value = {
    ...channel,
    config: { ...channel.config }
  }
  // 处理webhook的headers显示
  if (channel.channel_type === 'webhook' && channel.config.headers) {
    editForm.value.config.headers_json = JSON.stringify(channel.config.headers, null, 2)
  }
  showEditModal.value = true
}

async function handleEditChannel() {
  // 处理webhook的headers
  let config = { ...editForm.value.config }
  if (editForm.value.channel_type === 'webhook' && config.headers_json) {
    try {
      config.headers = JSON.parse(config.headers_json)
      delete config.headers_json
    } catch {
      message.error('请求头JSON格式错误')
      return
    }
  }

  editing.value = true
  try {
    await updateNotificationChannel(editForm.value.id, {
      channel_name: editForm.value.channel_name,
      config,
      warning_levels: editForm.value.warning_levels,
      monitor_types: editForm.value.monitor_types,
      rate_limit_minutes: editForm.value.rate_limit_minutes,
      remark: editForm.value.remark
    })
    message.success('保存成功')
    showEditModal.value = false
    loadChannels()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '保存失败')
  } finally {
    editing.value = false
  }
}

// 删除渠道
async function deleteChannel(channel: NotificationChannel) {
  try {
    await deleteNotificationChannel(channel.id)
    message.success('删除成功')
    loadChannels()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '删除失败')
  }
}

// 测试渠道
async function testChannel(channel: NotificationChannel & { _testing?: boolean }) {
  channel._testing = true
  try {
    await testNotificationChannel(channel.id)
    message.success('测试通知发送成功')
  } catch (error: any) {
    message.error(error?.response?.data?.message || '测试失败')
  } finally {
    channel._testing = false
  }
}

onMounted(() => {
  loadChannels()
  loadChannelTypes()
})
</script>

<style scoped lang="scss">
.notification-page {
  padding: 16px;
  height: calc(100vh - 50px - 32px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }
}

.channel-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  flex: 1;
}

.channel-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.channel-card {
  border: 1px solid #e0e0e6;
  border-radius: 8px;
  padding: 16px;
  transition: box-shadow 0.2s;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .channel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;

    .channel-icon {
      color: #18a058;
    }

    .channel-info {
      flex: 1;

      h3 {
        margin: 0;
        font-size: 16px;
      }
    }
  }

  .channel-config {
    margin-bottom: 12px;

    .config-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
      font-size: 13px;

      .label {
        color: #666;
        min-width: 70px;
      }
    }
  }

  .channel-actions {
    display: flex;
    gap: 8px;
  }
}

.logs-header {
  margin-bottom: 12px;
}

.ml-2 {
  margin-left: 8px;
}

.py-8 {
  padding-top: 32px;
  padding-bottom: 32px;
}
</style>