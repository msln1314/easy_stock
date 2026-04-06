<template>
  <div class="stock-analysis-container">
    <!-- 左侧：分析历史列表 -->
    <div class="history-panel">
      <div class="panel-header">
        <h3>分析历史</h3>
        <n-button type="primary" size="small" @click="showCreateDialog">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          新建分析
        </n-button>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <n-input
          v-model:value="searchStockCode"
          placeholder="搜索股票代码"
          clearable
          size="small"
          @clear="loadHistory"
          @keyup.enter="loadHistory"
        >
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>
        <n-select
          v-model:value="filterStatus"
          placeholder="状态筛选"
          size="small"
          clearable
          :options="statusOptions"
          @update:value="loadHistory"
        />
      </div>

      <!-- 历史列表 -->
      <div class="history-list">
        <n-scrollbar style="max-height: calc(100vh - 300px)">
          <div
            v-for="item in historyList"
            :key="item.id"
            class="history-item"
            :class="{ active: selectedReport?.id === item.id }"
            @click="selectReport(item)"
          >
            <div class="item-header">
              <span class="stock-name">{{ item.stock_name }}</span>
              <span class="stock-code">{{ item.stock_code }}</span>
            </div>
            <div class="item-meta">
              <n-tag :type="getStatusTagType(item.status)" size="small">
                {{ item.status_display }}
              </n-tag>
              <n-tag type="info" size="small">
                {{ item.analysis_type_display }}
              </n-tag>
            </div>
            <div class="item-prompt">{{ item.request_prompt }}</div>
            <div class="item-time">{{ formatDate(item.created_at) }}</div>
          </div>
          <n-empty v-if="historyList.length === 0" description="暂无分析历史" />
        </n-scrollbar>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar">
        <n-pagination
          v-model:page="currentPage"
          :page-size="pageSize"
          :item-count="total"
          simple
          @update:page="loadHistory"
        />
      </div>
    </div>

    <!-- 右侧：报告详情 -->
    <div class="report-panel">
      <template v-if="selectedReport">
        <div class="panel-header">
          <h3>{{ selectedReport.stock_name }} ({{ selectedReport.stock_code }})</h3>
          <div class="header-actions">
            <n-tag :type="getStatusTagType(selectedReport.status)">
              {{ selectedReport.status_display }}
            </n-tag>
            <n-button type="error" size="small" @click="handleDelete">
              <template #icon>
                <n-icon><TrashOutline /></n-icon>
              </template>
              删除
            </n-button>
          </div>
        </div>

        <!-- 报告加载中 -->
        <div v-if="loadingReport" class="loading-container">
          <n-skeleton text :repeat="10" />
        </div>

        <!-- 报告内容 -->
        <template v-else-if="reportDetail">
          <n-scrollbar style="max-height: calc(100vh - 200px)">
            <!-- 摘要 -->
            <div v-if="reportDetail.summary" class="report-section">
              <div class="section-title">
                <n-icon><DocumentTextOutline /></n-icon>
                摘要
              </div>
              <div class="section-content" v-html="renderMarkdown(reportDetail.summary)" />
            </div>

            <!-- 基本面分析 -->
            <div v-if="reportDetail.fundamental_analysis" class="report-section">
              <div class="section-title">
                <n-icon><TrendingUpOutline /></n-icon>
                基本面分析
              </div>
              <div class="section-content" v-html="renderMarkdown(reportDetail.fundamental_analysis)" />
            </div>

            <!-- 技术面分析 -->
            <div v-if="reportDetail.technical_analysis" class="report-section">
              <div class="section-title">
                <n-icon><StatsChartOutline /></n-icon>
                技术面分析
              </div>
              <div class="section-content" v-html="renderMarkdown(reportDetail.technical_analysis)" />
            </div>

            <!-- 风险分析 -->
            <div v-if="reportDetail.risk_analysis" class="report-section">
              <div class="section-title">
                <n-icon><WarningOutline /></n-icon>
                风险分析
              </div>
              <div class="section-content" v-html="renderMarkdown(reportDetail.risk_analysis)" />
            </div>

            <!-- 投资建议 -->
            <div v-if="reportDetail.recommendation" class="report-section recommendation">
              <div class="section-title">
                <n-icon><StarOutline /></n-icon>
                投资建议
              </div>
              <div class="section-content" v-html="renderMarkdown(reportDetail.recommendation)" />
            </div>

            <!-- 综合评分 -->
            <div v-if="reportDetail.rating" class="rating-section">
              <span class="rating-label">综合评分:</span>
              <n-rate v-model:value="reportDetail.rating" readonly />
            </div>

            <!-- 元信息 -->
            <div class="meta-section">
              <span>分析类型: {{ reportDetail.analysis_type_display }}</span>
              <span>模型: {{ reportDetail.model_name || 'N/A' }}</span>
              <span>耗时: {{ reportDetail.duration_ms || 0 }}ms</span>
              <span>Tokens: {{ reportDetail.tokens_used || 0 }}</span>
            </div>
          </n-scrollbar>
        </template>

        <!-- 空状态 -->
        <n-empty v-else description="请选择一条分析记录" />
      </template>

      <!-- 未选择状态 -->
      <div v-else class="empty-container">
        <n-empty description="请从左侧选择一条分析记录查看详情">
          <template #extra>
            <n-button type="primary" @click="showCreateDialog">新建分析</n-button>
          </template>
        </n-empty>
      </div>
    </div>

    <!-- 创建分析对话框 -->
    <n-modal
      v-model:show="createDialogVisible"
      preset="dialog"
      title="新建AI分析报告"
      positive-text="开始分析"
      negative-text="取消"
      :loading="creating"
      @positive-click="handleCreate"
    >
      <n-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px" label-placement="left">
        <n-form-item label="股票代码" path="stock_code">
          <n-input v-model:value="createForm.stock_code" placeholder="如: 000001" />
        </n-form-item>
        <n-form-item label="股票名称" path="stock_name">
          <n-input v-model:value="createForm.stock_name" placeholder="如: 平安银行" />
        </n-form-item>
        <n-form-item label="分析类型" path="analysis_type">
          <n-select v-model:value="createForm.analysis_type" placeholder="选择分析类型" :options="analysisTypeOptions" />
        </n-form-item>
        <n-form-item label="分析请求" path="request_prompt">
          <n-input
            v-model:value="createForm.request_prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入您的分析需求，如：分析该股票的投资价值、风险评估等"
          />
        </n-form-item>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage, useDialog, type FormInst, type FormRules } from 'naive-ui'
import {
  AddOutline,
  SearchOutline,
  TrashOutline,
  DocumentTextOutline,
  TrendingUpOutline,
  StatsChartOutline,
  WarningOutline,
  StarOutline,
} from '@vicons/ionicons5'
import {
  getAnalysisHistory,
  getAnalysisReport,
  createAnalysis,
  deleteAnalysisReport,
  type AnalysisHistoryItem,
  type AnalysisReport,
  type AnalysisType,
  type AnalysisStatus,
} from '@/api/stockAnalysis'

const message = useMessage()
const dialog = useDialog()

// 状态选项
const statusOptions = [
  { label: '已完成', value: 'completed' },
  { label: '处理中', value: 'processing' },
  { label: '失败', value: 'failed' },
]

// 分析类型选项
const analysisTypeOptions = [
  { label: '综合分析', value: 'comprehensive' },
  { label: '基本面分析', value: 'fundamental' },
  { label: '技术面分析', value: 'technical' },
  { label: '行业分析', value: 'industry' },
  { label: '风险分析', value: 'risk' },
  { label: '情绪分析', value: 'sentiment' },
]

// 历史列表
const historyList = ref<AnalysisHistoryItem[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchStockCode = ref('')
const filterStatus = ref<AnalysisStatus | ''>('')

// 选中报告
const selectedReport = ref<AnalysisHistoryItem | null>(null)
const reportDetail = ref<AnalysisReport | null>(null)
const loadingReport = ref(false)

// 创建对话框
const createDialogVisible = ref(false)
const createFormRef = ref<FormInst | null>(null)
const creating = ref(false)
const createForm = reactive({
  stock_code: '',
  stock_name: '',
  analysis_type: 'comprehensive' as AnalysisType,
  request_prompt: '',
})
const createRules: FormRules = {
  stock_code: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
  stock_name: [{ required: true, message: '请输入股票名称', trigger: 'blur' }],
  request_prompt: [{ required: true, message: '请输入分析请求', trigger: 'blur' }],
}

// 加载历史列表
async function loadHistory() {
  try {
    const res = await getAnalysisHistory({
      stock_code: searchStockCode.value || undefined,
      status: filterStatus.value || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    historyList.value = res.items
    total.value = res.total
  } catch (error) {
    message.error('加载历史列表失败')
  }
}

// 选择报告
async function selectReport(item: AnalysisHistoryItem) {
  selectedReport.value = item
  loadingReport.value = true
  try {
    const res = await getAnalysisReport(item.id)
    reportDetail.value = res
  } catch (error) {
    message.error('加载报告详情失败')
    reportDetail.value = null
  } finally {
    loadingReport.value = false
  }
}

// 显示创建对话框
function showCreateDialog() {
  createForm.stock_code = ''
  createForm.stock_name = ''
  createForm.analysis_type = 'comprehensive'
  createForm.request_prompt = ''
  createDialogVisible.value = true
}

// 创建分析
async function handleCreate() {
  try {
    await createFormRef.value?.validate()
    creating.value = true
    const res = await createAnalysis(createForm)
    message.success(res.message)
    createDialogVisible.value = false
    // 重新加载历史
    await loadHistory()
    // 如果创建成功，自动选中新报告
    if (res.id) {
      const newItem = historyList.value.find(h => h.id === res.id)
      if (newItem) {
        await selectReport(newItem)
      }
    }
  } catch (error) {
    message.error('创建分析失败')
  } finally {
    creating.value = false
  }
}

// 删除报告
async function handleDelete() {
  if (!selectedReport.value) return
  dialog.warning({
    title: '确认删除',
    content: '确定要删除该分析报告吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteAnalysisReport(selectedReport.value!.id)
        message.success('删除成功')
        selectedReport.value = null
        reportDetail.value = null
        await loadHistory()
      } catch (error) {
        message.error('删除失败')
      }
    },
  })
}

// 获取状态标签类型
function getStatusTagType(status: AnalysisStatus): 'success' | 'warning' | 'error' | 'default' {
  const map: Record<AnalysisStatus, 'success' | 'warning' | 'error' | 'default'> = {
    completed: 'success',
    processing: 'warning',
    pending: 'default',
    failed: 'error',
  }
  return map[status] || 'default'
}

// 格式化日期
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// 渲染Markdown (简单处理)
function renderMarkdown(content: string): string {
  if (!content) return ''
  // 简单的换行处理
  return content
    .replace(/\n/g, '<br>')
    .replace(/## (.*)/g, '<h3>$1</h3>')
    .replace(/### (.*)/g, '<h4>$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

// 初始化
onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.stock-analysis-container {
  display: flex;
  height: calc(100vh - 120px);
  gap: 16px;
  padding: 16px;
}

.history-panel {
  width: 320px;
  background: var(--n-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--n-border-color);
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--n-border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.filter-bar {
  padding: 12px 16px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--n-border-color);
}

.history-list {
  flex: 1;
  overflow: hidden;
}

.history-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--n-border-color);
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: var(--n-color-hover);
}

.history-item.active {
  background: rgba(24, 144, 255, 0.1);
  border-left: 3px solid #1890ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.stock-name {
  font-weight: 500;
}

.stock-code {
  color: var(--n-text-color-3);
  font-size: 12px;
}

.item-meta {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.item-prompt {
  font-size: 13px;
  color: var(--n-text-color-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-time {
  font-size: 12px;
  color: var(--n-text-color-3);
  margin-top: 4px;
}

.pagination-bar {
  padding: 12px 16px;
  border-top: 1px solid var(--n-border-color);
  display: flex;
  justify-content: center;
}

.report-panel {
  flex: 1;
  background: var(--n-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--n-border-color);
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.loading-container,
.empty-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.report-section {
  padding: 16px 24px;
  border-bottom: 1px solid var(--n-border-color);
}

.section-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-content {
  line-height: 1.8;
}

.section-content :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
}

.recommendation {
  background: rgba(24, 144, 255, 0.05);
}

.rating-section {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-label {
  font-weight: 500;
}

.meta-section {
  padding: 12px 24px;
  font-size: 12px;
  color: var(--n-text-color-3);
  display: flex;
  gap: 16px;
  background: var(--n-color-modal);
}
</style>