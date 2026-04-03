<template>
  <div class="scheduler-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>计划任务管理</h2>
        <n-space>
          <n-button type="primary" @click="showAddModal = true">
            <template #icon>
              <n-icon><AddOutline /></n-icon>
            </template>
            新建任务
          </n-button>
          <n-button @click="initTasks" :loading="initializing">
            初始化预设
          </n-button>
        </n-space>
      </div>
      <div class="header-right">
        <n-space align="center">
          <span class="status-label">调度器：</span>
          <n-tag :type="schedulerStatus === 'running' ? 'success' : 'warning'" size="small">
            {{ schedulerStatus === 'running' ? '运行中' : '已停止' }}
          </n-tag>
          <span class="status-label">任务数：</span>
          <n-tag type="info" size="small">{{ jobCount }}</n-tag>
        </n-space>
      </div>
    </div>

    <!-- 任务列表 -->
    <div class="task-panel">
      <div class="panel-header">
        <span class="panel-title">任务列表</span>
        <n-space>
          <n-select
            v-model:value="filterType"
            :options="typeOptions"
            placeholder="任务类型"
            clearable
            size="small"
            style="width: 120px"
          />
          <n-select
            v-model:value="filterEnabled"
            :options="enabledOptions"
            placeholder="启用状态"
            clearable
            size="small"
            style="width: 100px"
          />
          <n-button size="small" @click="refreshStatus">刷新</n-button>
        </n-space>
      </div>

      <n-spin :show="loading">
        <n-data-table
          :columns="taskColumns"
          :data="filteredTasks"
          :row-key="(row: SchedulerTask) => row.id"
          striped
          size="small"
        />
        <n-empty v-if="!loading && filteredTasks.length === 0" description="暂无计划任务" class="py-8" />
      </n-spin>
    </div>

    <!-- 执行日志 -->
    <div class="log-panel">
      <div class="panel-header">
        <span class="panel-title">执行日志</span>
        <n-button size="small" @click="loadLogs">刷新</n-button>
      </div>
      <n-data-table
        :columns="logColumns"
        :data="logs"
        :max-height="200"
        striped
        size="small"
      />
    </div>

    <!-- 新建任务弹窗 -->
    <n-modal v-model:show="showAddModal" preset="card" title="新建计划任务" style="width: 700px">
      <n-form ref="addFormRef" :model="addForm" label-placement="left" label-width="100">
        <n-form-item label="任务KEY" required>
          <n-input v-model:value="addForm.task_key" placeholder="唯一标识，如：monitor_stock" />
        </n-form-item>
        <n-form-item label="任务名称" required>
          <n-input v-model:value="addForm.task_name" placeholder="如：股票监控任务" />
        </n-form-item>
        <n-form-item label="任务类型">
          <n-select v-model:value="addForm.task_type" :options="typeOptions" />
        </n-form-item>
        <n-form-item label="触发类型">
          <n-radio-group v-model:value="addForm.trigger_type">
            <n-radio-button value="cron">Cron表达式</n-radio-button>
            <n-radio-button value="interval">固定间隔</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="Cron表达式" required v-if="addForm.trigger_type === 'cron'">
          <n-space vertical style="width: 100%">
            <n-input v-model:value="addForm.trigger_config" placeholder="如：0 9 * * 1-5" />
            <n-button type="primary" size="small" @click="showCronBuilder = true">可视化生成</n-button>
          </n-space>
        </n-form-item>
        <n-form-item label="间隔配置" required v-else>
          <n-input v-model:value="addForm.trigger_config" placeholder="秒 分 时 天 周，如：0 10 0 0 0 表示每10秒" />
        </n-form-item>
        <n-form-item label="任务路径" required>
          <n-input v-model:value="addForm.job_path" placeholder="如：jobs.monitor_tasks.check_sell_warnings" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="addForm.description" type="textarea" placeholder="任务说明" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="createTask" :loading="creating">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Cron 表达式生成器弹窗 -->
    <n-modal v-model:show="showCronBuilder" preset="card" title="Cron 表达式生成器" style="width: 900px">
      <CronBuilder v-model="addForm.trigger_config" ref="cronBuilderRef" />
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCronBuilder = false">取消</n-button>
          <n-button type="primary" @click="showCronBuilder = false">应用表达式</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 任务详情弹窗 -->
    <n-modal v-model:show="showDetailModal" preset="card" :title="currentTask?.task_name" style="width: 700px">
      <template v-if="currentTask">
        <n-descriptions label-placement="left" :column="2" bordered size="small">
          <n-descriptions-item label="任务KEY">
            <n-tag type="info" size="small">{{ currentTask.task_key }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="任务类型">
            {{ getTypeLabel(currentTask.task_type) }}
          </n-descriptions-item>
          <n-descriptions-item label="触发类型">
            {{ currentTask.trigger_type }}
          </n-descriptions-item>
          <n-descriptions-item label="Cron表达式">
            <code>{{ currentTask.trigger_config }}</code>
          </n-descriptions-item>
          <n-descriptions-item label="任务路径">
            <code>{{ currentTask.job_path }}</code>
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="currentTask.is_enabled ? 'success' : 'warning'" size="small">
              {{ currentTask.is_enabled ? '已启用' : '已禁用' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="上次执行">
            {{ currentTask.last_run_time || '-' }}
          </n-descriptions-item>
          <n-descriptions-item label="下次执行">
            {{ currentTask.next_run_time || '-' }}
          </n-descriptions-item>
        </n-descriptions>

        <n-divider>任务描述</n-divider>
        <p class="task-desc">{{ currentTask.description || '无描述' }}</p>

        <n-divider>执行日志</n-divider>
        <n-data-table :columns="logColumns" :data="taskLogs" :max-height="150" striped size="small" />
      </template>

      <template #footer>
        <n-space justify="end">
          <n-button :type="currentTask?.is_enabled ? 'warning' : 'success'" @click="toggleTaskEnabled">
            {{ currentTask?.is_enabled ? '停止' : '启动' }}
          </n-button>
          <n-button type="info" @click="runTaskImmediate">立即执行</n-button>
          <n-button type="error" @click="deleteTask">删除</n-button>
          <n-button @click="showDetailModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton, NIcon, NSelect, NInput, NSpin, NTag, NModal, NDescriptions,
  NDescriptionsItem, NDivider, NDataTable, NEmpty, NForm, NFormItem, useMessage,
  NRadioGroup, NRadioButton, NSpace
} from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import CronBuilder from './CronBuilder.vue'
import {
  fetchSchedulerTasks, createSchedulerTask,
  deleteSchedulerTask, startTask, stopTask, runTaskNow,
  fetchTaskLogs, fetchAllLogs,
  fetchSchedulerStatus, initDefaultTasks,
  SchedulerTask, TaskLog
} from '@/api/scheduler'

const message = useMessage()

// 数据
const tasks = ref<SchedulerTask[]>([])
const logs = ref<TaskLog[]>([])
const taskLogs = ref<TaskLog[]>([])
const loading = ref(false)
const initializing = ref(false)
const creating = ref(false)

// 调度器状态
const schedulerStatus = ref('stopped')
const jobCount = ref(0)

// 筛选
const filterType = ref<string | null>(null)
const filterEnabled = ref<boolean | null>(null)

// 弹窗
const showAddModal = ref(false)
const showCronBuilder = ref(false)
const showDetailModal = ref(false)
const currentTask = ref<SchedulerTask | null>(null)
const cronBuilderRef = ref()

// 添加表单
const addFormRef = ref()
const addForm = ref({
  task_key: '',
  task_name: '',
  task_type: 'monitor',
  trigger_type: 'cron',
  trigger_config: '',
  job_path: '',
  description: ''
})

// 选项
const typeOptions = [
  { label: '监控任务', value: 'monitor' },
  { label: '报告任务', value: 'report' },
  { label: '清理任务', value: 'cleanup' },
  { label: '其他', value: 'other' }
]

const enabledOptions = [
  { label: '已启用', value: true },
  { label: '已禁用', value: false }
]

// 筛选后的任务
const filteredTasks = computed(() => {
  let result = tasks.value
  if (filterType.value) {
    result = result.filter(t => t.task_type === filterType.value)
  }
  if (filterEnabled.value !== null) {
    result = result.filter(t => t.is_enabled === filterEnabled.value)
  }
  return result
})

// 任务表格列
const taskColumns = [
  { title: 'KEY', key: 'task_key', width: 140, render: (row: SchedulerTask) => h(NTag, { type: 'info', size: 'small' }, { default: () => row.task_key }) },
  { title: '名称', key: 'task_name', width: 150 },
  { title: '类型', key: 'task_type', width: 80, render: (row: SchedulerTask) => getTypeLabel(row.task_type) },
  { title: 'Cron表达式', key: 'trigger_config', width: 140, render: (row: SchedulerTask) => h('code', {}, row.trigger_config) },
  { title: '状态', key: 'is_enabled', width: 80, render: (row: SchedulerTask) => h(NTag, { type: row.is_enabled ? 'success' : 'warning', size: 'small' }, { default: () => row.is_enabled ? '运行' : '停止' }) },
  { title: '上次执行', key: 'last_run_time', width: 150, render: (row: SchedulerTask) => row.last_run_time ? dayjs(row.last_run_time).format('YYYY-MM-DD HH:mm') : '-' },
  { title: '下次执行', key: 'next_run_time', width: 150, render: (row: SchedulerTask) => row.next_run_time ? dayjs(row.next_run_time).format('YYYY-MM-DD HH:mm') : '-' },
  { title: '执行次数', key: 'run_count', width: 80 },
  {
    title: '操作', key: 'actions', width: 180,
    render: (row: SchedulerTask) => h(NSpace, {}, {
      default: () => [
        h(NButton, { size: 'tiny', type: row.is_enabled ? 'warning' : 'success', onClick: () => toggleEnabled(row) }, { default: () => row.is_enabled ? '停止' : '启动' }),
        h(NButton, { size: 'tiny', type: 'info', onClick: () => runNow(row) }, { default: () => '执行' }),
        h(NButton, { size: 'tiny', onClick: () => showDetail(row) }, { default: () => '详情' })
      ]
    })
  }
]

// 日志表格列
const logColumns = [
  { title: '任务', key: 'task_name', width: 120 },
  { title: '状态', key: 'status', width: 60, render: (row: TaskLog) => h(NTag, { type: row.status ? 'success' : 'error', size: 'small' }, { default: () => row.status ? '成功' : '失败' }) },
  { title: '消息', key: 'job_message', width: 200, ellipsis: { tooltip: true } },
  { title: '耗时', key: 'duration', width: 80, render: (row: TaskLog) => row.duration ? `${row.duration}ms` : '-' },
  { title: '时间', key: 'created_at', width: 150, render: (row: TaskLog) => row.created_at ? dayjs(row.created_at).format('YYYY-MM-DD HH:mm:ss') : '-' }
]

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = { monitor: '监控', report: '报告', cleanup: '清理', other: '其他' }
  return labels[type] || type
}

// 加载任务列表
async function loadTasks() {
  loading.value = true
  try {
    tasks.value = await fetchSchedulerTasks()
  } catch (error) {
    console.error('加载任务失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载日志
async function loadLogs() {
  try {
    logs.value = await fetchAllLogs({ limit: 50 })
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

// 刷新调度器状态
async function refreshStatus() {
  try {
    const status = await fetchSchedulerStatus()
    schedulerStatus.value = status.status
    jobCount.value = status.job_count
  } catch (error) {
    console.error('获取状态失败:', error)
  }
}

// 初始化预设任务
async function initTasks() {
  initializing.value = true
  try {
    await initDefaultTasks()
    message.success('预设任务初始化成功')
    loadTasks()
  } catch (error) {
    message.error('初始化失败')
  } finally {
    initializing.value = false
  }
}

// 创建任务
async function createTask() {
  creating.value = true
  try {
    await createSchedulerTask(addForm.value)
    message.success('任务创建成功')
    showAddModal.value = false
    addForm.value = { task_key: '', task_name: '', task_type: 'monitor', trigger_type: 'cron', trigger_config: '', job_path: '', description: '' }
    loadTasks()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

// 切换启用状态
async function toggleEnabled(task: SchedulerTask) {
  try {
    if (task.is_enabled) {
      await stopTask(task.id)
      message.success('任务已停止')
    } else {
      await startTask(task.id)
      message.success('任务已启动')
    }
    loadTasks()
    refreshStatus()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '操作失败')
  }
}

// 立即执行
async function runNow(task: SchedulerTask) {
  try {
    await runTaskNow(task.id)
    message.success('任务已触发执行')
    setTimeout(() => loadLogs(), 2000)
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '执行失败')
  }
}

// 显示详情
async function showDetail(task: SchedulerTask) {
  currentTask.value = task
  showDetailModal.value = true
  try {
    taskLogs.value = await fetchTaskLogs(task.id, 20)
  } catch (error) {
    taskLogs.value = []
  }
}

// 切换任务启用状态（详情弹窗）
async function toggleTaskEnabled() {
  if (!currentTask.value) return
  await toggleEnabled(currentTask.value)
  currentTask.value = tasks.value.find(t => t.id === currentTask.value?.id) || currentTask.value
}

// 立即执行任务（详情弹窗）
async function runTaskImmediate() {
  if (!currentTask.value) return
  await runNow(currentTask.value)
  try {
    taskLogs.value = await fetchTaskLogs(currentTask.value.id, 20)
  } catch (error) { /* ignore */ }
}

// 删除任务
async function deleteTask() {
  if (!currentTask.value) return
  try {
    await deleteSchedulerTask(currentTask.value.id)
    message.success('任务已删除')
    showDetailModal.value = false
    loadTasks()
    refreshStatus()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadTasks()
  loadLogs()
  refreshStatus()
})
</script>

<style scoped lang="scss">
.scheduler-page {
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

  .header-right {
    display: flex;
    align-items: center;
  }

  .status-label {
    color: #666;
    font-size: 13px;
  }
}

.task-panel,
.log-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.task-panel {
  flex: 1;
  display: flex;
  flex-direction: column;

  .n-spin {
    flex: 1;
  }
}

.log-panel {
  flex-shrink: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;

  .panel-title {
    font-size: 14px;
    font-weight: 500;
    color: #333;
  }
}

.task-desc {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.py-8 {
  padding-top: 32px;
  padding-bottom: 32px;
}
</style>