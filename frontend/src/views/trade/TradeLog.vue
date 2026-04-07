<template>
  <div class="trade-log-page">
    <n-card title="交易日志">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="filter.action_type"
            :options="actionOptions"
            placeholder="操作类型"
            clearable
            style="width: 120px"
          />
          <n-select
            v-model:value="filter.result"
            :options="resultOptions"
            placeholder="结果"
            clearable
            style="width: 100px"
          />
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            clearable
            @update:value="handleDateChange"
          />
          <n-button type="primary" @click="loadData">查询</n-button>
        </n-space>
      </template>

      <!-- 统计卡片 -->
      <n-grid :cols="4" :x-gap="16" class="stats-grid">
        <n-gi>
          <n-statistic label="今日交易" :value="stats.today_trades" />
        </n-gi>
        <n-gi>
          <n-statistic label="总交易数" :value="stats.total_trades" />
        </n-gi>
        <n-gi>
          <n-statistic label="成功率" :value="stats.success_rate" suffix="%" />
        </n-gi>
        <n-gi>
          <n-statistic label="买入/卖出" :value="`${stats.buy_count}/${stats.sell_count}`" />
        </n-gi>
      </n-grid>

      <n-divider />

      <!-- 日志表格 -->
      <n-data-table
        :columns="columns"
        :data="logs"
        :loading="loading"
        :row-key="(row: TradeLog) => row.id"
        striped
        :pagination="pagination"
        @update:page="handlePageChange"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { NTag, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  getTradeLogs,
  getTradeLogStats,
  type TradeLog,
  type TradeStats
} from '@/api/tradeLog'

const message = useMessage()
const loading = ref(false)
const logs = ref<TradeLog[]>([])
const dateRange = ref<[number, number] | null>(null)

const stats = ref<TradeStats>({
  total_trades: 0,
  today_trades: 0,
  success_rate: 0,
  buy_count: 0,
  sell_count: 0,
  cancel_count: 0
})

const filter = reactive({
  action_type: null as string | null,
  result: null as string | null,
  start_date: null as string | null,
  end_date: null as string | null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100]
})

const actionOptions = [
  { label: '买入', value: 'buy' },
  { label: '卖出', value: 'sell' },
  { label: '撤单', value: 'cancel' },
  { label: '查询', value: 'query' },
  { label: '同步', value: 'sync' }
]

const resultOptions = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
  { label: '处理中', value: 'pending' }
]

const actionTypeMap: Record<string, { type: 'success' | 'warning' | 'info' | 'error'; label: string }> = {
  buy: { type: 'success', label: '买入' },
  sell: { type: 'warning', label: '卖出' },
  cancel: { type: 'info', label: '撤单' },
  query: { type: 'info', label: '查询' },
  sync: { type: 'info', label: '同步' }
}

const resultMap: Record<string, { type: 'success' | 'error' | 'warning'; label: string }> = {
  success: { type: 'success', label: '成功' },
  failed: { type: 'error', label: '失败' },
  pending: { type: 'warning', label: '处理中' }
}

const columns: DataTableColumns<TradeLog> = [
  {
    title: '时间',
    key: 'created_at',
    width: 180,
    render: (row) => row.created_at?.replace('T', ' ').slice(0, 19) || '-'
  },
  {
    title: '操作类型',
    key: 'action_type',
    width: 80,
    render: (row) => {
      const config = actionTypeMap[row.action_type] || { type: 'info', label: row.action_type }
      return h(NTag, { type: config.type, size: 'small' }, { default: () => config.label })
    }
  },
  {
    title: '股票代码',
    key: 'stock_code',
    width: 100
  },
  {
    title: '股票名称',
    key: 'stock_name',
    width: 100
  },
  {
    title: '价格',
    key: 'price',
    width: 80,
    render: (row) => row.price?.toFixed(2) || '-'
  },
  {
    title: '数量',
    key: 'quantity',
    width: 80,
    render: (row) => row.quantity?.toLocaleString() || '-'
  },
  {
    title: '金额',
    key: 'amount',
    width: 100,
    render: (row) => row.amount?.toLocaleString() || '-'
  },
  {
    title: '结果',
    key: 'result',
    width: 80,
    render: (row) => {
      const config = resultMap[row.result] || { type: 'info', label: row.result }
      return h(NTag, { type: config.type, size: 'small' }, { default: () => config.label })
    }
  },
  {
    title: '消息',
    key: 'message',
    ellipsis: { tooltip: true }
  }
]

function handleDateChange(val: [number, number] | null) {
  if (val) {
    filter.start_date = new Date(val[0]).toISOString().slice(0, 10)
    filter.end_date = new Date(val[1]).toISOString().slice(0, 10)
  } else {
    filter.start_date = null
    filter.end_date = null
  }
}

async function loadData() {
  loading.value = true
  try {
    const [logsRes, statsRes] = await Promise.all([
      getTradeLogs({
        action_type: filter.action_type || undefined,
        result: filter.result || undefined,
        start_date: filter.start_date || undefined,
        end_date: filter.end_date || undefined,
        limit: pagination.pageSize,
        offset: (pagination.page - 1) * pagination.pageSize
      }),
      getTradeLogStats({
        start_date: filter.start_date || undefined,
        end_date: filter.end_date || undefined
      })
    ])
    logs.value = logsRes.logs
    pagination.itemCount = logsRes.total
    stats.value = statsRes
  } catch (e: any) {
    message.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function handlePageChange(page: number) {
  pagination.page = page
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.trade-log-page {
  padding: 16px;
}

.stats-grid {
  margin-bottom: 16px;
}
</style>