<template>
  <div class="stock-analysis-container">
    <!-- 左侧：分析历史列表 -->
    <div class="history-panel">
      <div class="panel-header">
        <h3>分析历史</h3>
        <el-button type="primary" size="small" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建分析
        </el-button>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchStockCode"
          placeholder="搜索股票代码"
          clearable
          size="small"
          @clear="loadHistory"
          @keyup.enter="loadHistory"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterStatus" placeholder="状态筛选" size="small" clearable @change="loadHistory">
          <el-option label="已完成" value="completed" />
          <el-option label="处理中" value="processing" />
          <el-option label="失败" value="failed" />
        </el-select>
      </div>

      <!-- 历史列表 -->
      <div class="history-list">
        <el-scrollbar>
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
              <el-tag :type="getStatusTagType(item.status)" size="small">
                {{ item.status_display }}
              </el-tag>
              <el-tag type="info" size="small">
                {{ item.analysis_type_display }}
              </el-tag>
            </div>
            <div class="item-prompt">{{ item.request_prompt }}</div>
            <div class="item-time">{{ formatDate(item.created_at) }}</div>
          </div>
          <el-empty v-if="historyList.length === 0" description="暂无分析历史" />
        </el-scrollbar>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          small
          @current-change="loadHistory"
        />
      </div>
    </div>

    <!-- 右侧：报告详情 -->
    <div class="report-panel">
      <template v-if="selectedReport">
        <div class="panel-header">
          <h3>{{ selectedReport.stock_name }} ({{ selectedReport.stock_code }})</h3>
          <div class="header-actions">
            <el-tag :type="getStatusTagType(selectedReport.status)">
              {{ selectedReport.status_display }}
            </el-tag>
            <el-button type="danger" size="small" @click="handleDelete">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>

        <!-- 报告加载中 -->
        <div v-if="loadingReport" class="loading-container">
          <el-skeleton :rows="10" animated />
        </div>

        <!-- 报告内容 -->
        <template v-else-if="reportDetail">
          <!-- 摘要 -->
          <div v-if="reportDetail.summary" class="report-section">
            <div class="section-title">
              <el-icon><Document /></el-icon>
              摘要
            </div>
            <div class="section-content" v-html="renderMarkdown(reportDetail.summary)" />
          </div>

          <!-- 基本面分析 -->
          <div v-if="reportDetail.fundamental_analysis" class="report-section">
            <div class="section-title">
              <el-icon><TrendCharts /></el-icon>
              基本面分析
            </div>
            <div class="section-content" v-html="renderMarkdown(reportDetail.fundamental_analysis)" />
          </div>

          <!-- 技术面分析 -->
          <div v-if="reportDetail.technical_analysis" class="report-section">
            <div class="section-title">
              <el-icon><DataLine /></el-icon>
              技术面分析
            </div>
            <div class="section-content" v-html="renderMarkdown(reportDetail.technical_analysis)" />
          </div>

          <!-- 风险分析 -->
          <div v-if="reportDetail.risk_analysis" class="report-section">
            <div class="section-title">
              <el-icon><Warning /></el-icon>
              风险分析
            </div>
            <div class="section-content" v-html="renderMarkdown(reportDetail.risk_analysis)" />
          </div>

          <!-- 投资建议 -->
          <div v-if="reportDetail.recommendation" class="report-section recommendation">
            <div class="section-title">
              <el-icon><Star /></el-icon>
              投资建议
            </div>
            <div class="section-content" v-html="renderMarkdown(reportDetail.recommendation)" />
          </div>

          <!-- 综合评分 -->
          <div v-if="reportDetail.rating" class="rating-section">
            <span class="rating-label">综合评分:</span>
            <el-rate v-model="reportDetail.rating" disabled show-score />
          </div>

          <!-- 元信息 -->
          <div class="meta-section">
            <span>分析类型: {{ reportDetail.analysis_type_display }}</span>
            <span>模型: {{ reportDetail.model_name || 'N/A' }}</span>
            <span>耗时: {{ reportDetail.duration_ms || 0 }}ms</span>
            <span>Tokens: {{ reportDetail.tokens_used || 0 }}</span>
          </div>
        </template>

        <!-- 空状态 -->
        <el-empty v-else description="请选择一条分析记录" />
      </template>

      <!-- 未选择状态 -->
      <div v-else class="empty-container">
        <el-empty description="请从左侧选择一条分析记录查看详情">
          <el-button type="primary" @click="showCreateDialog">新建分析</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 创建分析对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建AI分析报告"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="股票代码" prop="stock_code">
          <el-input v-model="createForm.stock_code" placeholder="如: 000001" />
        </el-form-item>
        <el-form-item label="股票名称" prop="stock_name">
          <el-input v-model="createForm.stock_name" placeholder="如: 平安银行" />
        </el-form-item>
        <el-form-item label="分析类型" prop="analysis_type">
          <el-select v-model="createForm.analysis_type" placeholder="选择分析类型">
            <el-option label="综合分析" value="comprehensive" />
            <el-option label="基本面分析" value="fundamental" />
            <el-option label="技术面分析" value="technical" />
            <el-option label="行业分析" value="industry" />
            <el-option label="风险分析" value="risk" />
            <el-option label="情绪分析" value="sentiment" />
          </el-select>
        </el-form-item>
        <el-form-item label="分析请求" prop="request_prompt">
          <el-input
            v-model="createForm.request_prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入您的分析需求，如：分析该股票的投资价值、风险评估等"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          开始分析
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Delete, Document, TrendCharts, DataLine, Warning, Star } from '@element-plus/icons-vue'
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
import { marked } from 'marked'

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
const createFormRef = ref()
const creating = ref(false)
const createForm = reactive({
  stock_code: '',
  stock_name: '',
  analysis_type: 'comprehensive' as AnalysisType,
  request_prompt: '',
})
const createRules = {
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
    historyList.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    ElMessage.error('加载历史列表失败')
  }
}

// 选择报告
async function selectReport(item: AnalysisHistoryItem) {
  selectedReport.value = item
  loadingReport.value = true
  try {
    const res = await getAnalysisReport(item.id)
    reportDetail.value = res.data
  } catch (error) {
    ElMessage.error('加载报告详情失败')
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
    await createFormRef.value.validate()
    creating.value = true
    const res = await createAnalysis(createForm)
    ElMessage.success(res.data.message)
    createDialogVisible.value = false
    // 重新加载历史
    await loadHistory()
    // 如果创建成功，自动选中新报告
    if (res.data.id) {
      const newItem = historyList.value.find(h => h.id === res.data.id)
      if (newItem) {
        await selectReport(newItem)
      }
    }
  } catch (error) {
    ElMessage.error('创建分析失败')
  } finally {
    creating.value = false
  }
}

// 删除报告
async function handleDelete() {
  if (!selectedReport.value) return
  try {
    await ElMessageBox.confirm('确定要删除该分析报告吗？', '提示', {
      type: 'warning',
    })
    await deleteAnalysisReport(selectedReport.value.id)
    ElMessage.success('删除成功')
    selectedReport.value = null
    reportDetail.value = null
    await loadHistory()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 获取状态标签类型
function getStatusTagType(status: AnalysisStatus): 'success' | 'warning' | 'danger' | 'info' {
  const map: Record<AnalysisStatus, 'success' | 'warning' | 'danger' | 'info'> = {
    completed: 'success',
    processing: 'warning',
    pending: 'info',
    failed: 'danger',
  }
  return map[status] || 'info'
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

// 渲染Markdown
function renderMarkdown(content: string): string {
  if (!content) return ''
  return marked(content) as string
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
  background: var(--el-bg-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
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
  border-bottom: 1px solid var(--el-border-color-light);
}

.history-list {
  flex: 1;
  overflow: hidden;
}

.history-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: var(--el-fill-color-light);
}

.history-item.active {
  background: var(--el-color-primary-light-9);
  border-left: 3px solid var(--el-color-primary);
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.stock-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.stock-code {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.item-meta {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.item-prompt {
  font-size: 13px;
  color: var(--el-text-color-regular);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.pagination-bar {
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: center;
}

.report-panel {
  flex: 1;
  background: var(--el-bg-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.section-title {
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-content {
  color: var(--el-text-color-regular);
  line-height: 1.8;
}

.section-content :deep(h1),
.section-content :deep(h2),
.section-content :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
}

.section-content :deep(p) {
  margin-bottom: 8px;
}

.section-content :deep(ul),
.section-content :deep(ol) {
  margin-left: 20px;
}

.recommendation {
  background: var(--el-color-primary-light-9);
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
  color: var(--el-text-color-secondary);
  display: flex;
  gap: 16px;
  background: var(--el-fill-color-lighter);
}
</style>