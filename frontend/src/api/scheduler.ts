/**
 * 计划任务相关API
 */
import request from '@/utils/request'

// ==================== 类型定义 ====================

export interface SchedulerTask {
  id: number
  task_key: string
  task_name: string
  task_type: string
  trigger_type: string
  trigger_config: string
  job_path: string
  is_enabled: boolean
  is_running: boolean
  description?: string
  last_run_time?: string
  next_run_time?: string
  last_run_status?: string
  run_count: number
}

export interface TaskLog {
  id: number
  task_key: string
  task_name: string
  status: boolean
  job_message?: string
  exception_info?: string
  start_time?: string
  end_time?: string
  duration?: number
  created_at?: string
}

export interface CronExample {
  expr: string
  desc: string
}

export interface CronPreviewResult {
  cron_expr: string
  valid: boolean
  next_runs?: string[]
  error?: string
}

// ==================== 任务管理接口 ====================

/** 获取计划任务列表 */
export async function fetchSchedulerTasks(params?: {
  task_type?: string
  is_enabled?: boolean
}): Promise<SchedulerTask[]> {
  return request.get('/api/scheduler/tasks', { params })
}

/** 创建计划任务 */
export async function createSchedulerTask(data: {
  task_key: string
  task_name: string
  task_type?: string
  trigger_type?: string
  trigger_config: string
  job_path: string
  job_args?: string
  job_kwargs?: string
  description?: string
}): Promise<{ id: number }> {
  return request.post('/api/scheduler/tasks', data)
}

/** 更新计划任务 */
export async function updateSchedulerTask(id: number, data: {
  task_name?: string
  trigger_type?: string
  trigger_config?: string
  is_enabled?: boolean
  description?: string
}): Promise<void> {
  return request.put(`/api/scheduler/tasks/${id}`, data)
}

/** 删除计划任务 */
export async function deleteSchedulerTask(id: number): Promise<void> {
  return request.delete(`/api/scheduler/tasks/${id}`)
}

// ==================== 任务控制接口 ====================

/** 启动任务 */
export async function startTask(id: number): Promise<void> {
  return request.post(`/api/scheduler/tasks/${id}/start`)
}

/** 停止任务 */
export async function stopTask(id: number): Promise<void> {
  return request.post(`/api/scheduler/tasks/${id}/stop`)
}

/** 立即执行任务 */
export async function runTaskNow(id: number): Promise<void> {
  return request.post(`/api/scheduler/tasks/${id}/run`)
}

// ==================== 任务日志接口 ====================

/** 获取任务日志 */
export async function fetchTaskLogs(taskId: number, limit?: number): Promise<TaskLog[]> {
  return request.get(`/api/scheduler/tasks/${taskId}/logs`, { params: { limit } })
}

/** 获取所有日志 */
export async function fetchAllLogs(params?: {
  task_key?: string
  status?: boolean
  limit?: number
}): Promise<TaskLog[]> {
  return request.get('/api/scheduler/logs', { params })
}

// ==================== Cron辅助接口 ====================

/** 预览Cron表达式 */
export async function previewCron(cronExpr: string): Promise<CronPreviewResult> {
  return request.post('/api/scheduler/cron/preview', { cron_expr: cronExpr })
}

/** 获取Cron示例 */
export async function fetchCronExamples(): Promise<CronExample[]> {
  return request.get('/api/scheduler/cron/examples')
}

// ==================== 调度器状态接口 ====================

/** 获取调度器状态 */
export async function fetchSchedulerStatus(): Promise<{
  status: string
  job_count: number
  jobs: any[]
}> {
  return request.get('/api/scheduler/status')
}

/** 初始化预设任务 */
export async function initDefaultTasks(): Promise<void> {
  return request.post('/api/scheduler/init')
}