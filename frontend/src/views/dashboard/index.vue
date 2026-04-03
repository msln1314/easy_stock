<template>
  <div class="dashboard-screen">
    <!-- 第一行：指数信息 + 时间 + 接口状态 -->
    <header class="row-header">
      <div class="index-info">
        <div class="index-item" v-for="idx in indexData" :key="idx.code">
          <span class="index-name">{{ idx.name }}</span>
          <span class="index-price" :class="idx.change >= 0 ? 'rise' : 'fall'">{{ idx.price.toFixed(2) }}</span>
          <span class="index-change" :class="idx.change >= 0 ? 'rise' : 'fall'">
            {{ idx.change >= 0 ? '+' : '' }}{{ idx.change.toFixed(2) }}%
          </span>
        </div>
      </div>
      <div class="center-time">
        <div class="current-time">{{ currentTime }}</div>
        <div class="date-info">{{ dateInfo }}</div>
      </div>
      <div class="api-status">
        <div class="status-item">
          <span class="status-label">数据接口</span>
          <span class="status-dot" :class="dataApiStatus"></span>
          <span class="status-text" :class="dataApiStatus">{{ dataApiStatusText }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">QMT接口</span>
          <span class="status-dot" :class="qmtApiStatus"></span>
          <span class="status-text" :class="qmtApiStatus">{{ qmtApiStatusText }}</span>
        </div>
        <!-- 头像下拉跳转管理页 -->
        <n-dropdown :options="dropdownOptions" @select="handleDropdown">
          <n-avatar round size="small" class="user-avatar">
            <n-icon><PersonOutline /></n-icon>
          </n-avatar>
        </n-dropdown>
      </div>
    </header>

    <!-- 第二行：策略数 + 因子数 + 市场情绪 + QMT按钮 -->
    <div class="row-stats">
      <div class="stat-item">
        <div class="stat-value">{{ strategyCount }}</div>
        <div class="stat-label">策略数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ factorCount }}</div>
        <div class="stat-label">因子数</div>
      </div>
      <div class="stat-item market-sentiment">
        <div class="sentiment-value" :class="marketSentimentClass">{{ marketSentimentText }}</div>
        <div class="stat-label">市场情绪</div>
      </div>
      <div class="qmt-control">
        <n-button :type="qmtConnected ? 'success' : 'warning'" @click="toggleQMT">
          {{ qmtConnected ? 'QMT已连接' : '开启QMT' }}
        </n-button>
      </div>
    </div>

    <!-- 第三行：策略选股列表 -->
    <div class="row-selection">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">策略选股列表</span>
          <span class="panel-count">共 {{ selectedStocks.length }} 只</span>
        </div>
        <div class="panel-content">
          <n-data-table
            :columns="selectionColumns"
            :data="selectedStocks"
            :max-height="200"
            striped
            size="small"
          />
        </div>
      </div>
    </div>

    <!-- 第四行：卖出预警 + 选股池排序 + 持仓信息 + 分析结果 -->
    <div class="row-bottom">
      <div class="panel sell-warning">
        <div class="panel-header">
          <span class="panel-title">卖出预警股票池</span>
        </div>
        <div class="panel-content scroll-content">
          <div class="stock-item" v-for="stock in sellWarningStocks" :key="stock.code">
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
            <span class="warning-reason">{{ stock.reason }}</span>
          </div>
        </div>
      </div>

      <div class="panel selection-pool">
        <div class="panel-header">
          <span class="panel-title">选股池排序</span>
        </div>
        <div class="panel-content scroll-content">
          <div class="rank-item" v-for="(stock, idx) in selectionPoolRanked" :key="stock.code">
            <span class="rank-num">{{ idx + 1 }}</span>
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
            <span class="rank-score">{{ stock.score }}</span>
          </div>
        </div>
      </div>

      <div class="panel positions">
        <div class="panel-header">
          <span class="panel-title">持仓信息</span>
          <span class="panel-total">总市值: {{ totalMarketValue }}</span>
        </div>
        <div class="panel-content scroll-content">
          <n-data-table
            :columns="positionColumns"
            :data="positions"
            striped
            size="small"
          />
        </div>
      </div>

      <div class="panel analysis">
        <div class="panel-header">
          <span class="panel-title">分析结果</span>
        </div>
        <div class="panel-content scroll-content">
          <div class="analysis-item" v-for="item in analysisResults" :key="item.id">
            <span class="analysis-time">{{ item.time }}</span>
            <span class="analysis-content">{{ item.content }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NIcon, NAvatar, NDropdown, NDataTable, NTag } from 'naive-ui'
import { PersonOutline, SettingsOutline, TvOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'

const router = useRouter()

// 时间状态
const currentTime = ref(dayjs().format('HH:mm:ss'))
const dateInfo = ref(dayjs().format('YYYY年MM月DD日 dddd'))

// 模拟数据 - 指数信息
const indexData = ref([
  { code: 'sh', name: '上证指数', price: 3250.68, change: 1.25 },
  { code: 'sz', name: '深证成指', price: 10580.32, change: -0.58 },
  { code: 'cy', name: '创业板指', price: 2150.45, change: 0.82 },
  { code: 'hs300', name: '沪深300', price: 3850.12, change: 0.35 }
])

// 接口状态
const dataApiStatus = ref<'healthy' | 'error' | 'warning'>('healthy')
const qmtApiStatus = ref<'healthy' | 'error' | 'warning'>('warning')
const dataApiStatusText = computed(() => dataApiStatus.value === 'healthy' ? '正常' : dataApiStatus.value === 'warning' ? '延迟' : '异常')
const qmtApiStatusText = computed(() => qmtApiStatus.value === 'healthy' ? '已连接' : qmtApiStatus.value === 'warning' ? '未连接' : '异常')

// 统计数据
const strategyCount = ref(12)
const factorCount = ref(45)
const marketSentiment = ref<'bullish' | 'bearish' | 'neutral'>('bullish')
const marketSentimentText = computed(() => marketSentiment.value === 'bullish' ? '看涨' : marketSentiment.value === 'bearish' ? '看跌' : '中性')
const marketSentimentClass = computed(() => marketSentiment.value)

// QMT连接状态
const qmtConnected = ref(false)

// 策略选股列表
const selectedStocks = ref([
  { code: '000001', name: '平安银行', strategy: '均线突破', score: 85, status: '持仓' },
  { code: '000002', name: '万科A', strategy: '量价共振', score: 78, status: '观察' },
  { code: '600519', name: '贵州茅台', strategy: '趋势跟踪', score: 92, status: '持仓' },
  { code: '000858', name: '五粮液', strategy: '均线突破', score: 88, status: '建仓' }
])

// 卖出预警股票池
const sellWarningStocks = ref([
  { code: '000001', name: '平安银行', reason: '跌破止损线' },
  { code: '600036', name: '招商银行', reason: '技术指标转弱' },
  { code: '000333', name: '美的集团', reason: '成交量萎缩' }
])

// 选股池排序
const selectionPoolRanked = ref([
  { code: '600519', name: '贵州茅台', score: 92 },
  { code: '000858', name: '五粮液', score: 88 },
  { code: '000001', name: '平安银行', score: 85 },
  { code: '000002', name: '万科A', score: 78 },
  { code: '601318', name: '中国平安', score: 75 }
])

// 持仓信息
const positions = ref([
  { code: '000001', name: '平安银行', size: 500, cost: 12.00, current: 12.35, profit: 175, profitPercent: 2.92 },
  { code: '600519', name: '贵州茅台', size: 100, cost: 1850.00, current: 1920.00, profit: 7000, profitPercent: 3.78 },
  { code: '000858', name: '五粮液', size: 200, cost: 150.00, current: 155.50, profit: 1100, profitPercent: 3.67 }
])

const totalMarketValue = computed(() => {
  const total = positions.value.reduce((sum, p) => sum + p.size * p.current, 0)
  return `¥${total.toLocaleString()}`
})

// 分析结果滚动
const analysisResults = ref([
  { id: 1, time: '10:30', content: '策略A触发买入信号：000001突破20日均线' },
  { id: 2, time: '10:25', content: '市场情绪指标：资金流向偏积极' },
  { id: 3, time: '10:20', content: '因子分析：动量因子表现强势' },
  { id: 4, time: '10:15', content: '风险提示：仓位已接近上限80%' }
])

// 下拉菜单选项
const dropdownOptions = [
  { label: '管理页面', key: 'strategy', icon: () => h(NIcon, null, { default: () => h(SettingsOutline) }) },
  { label: '全屏模式', key: 'fullscreen', icon: () => h(NIcon, null, { default: () => h(TvOutline) }) }
]

function handleDropdown(key: string) {
  if (key === 'strategy') {
    router.push({ name: 'Strategy' })
  } else if (key === 'fullscreen') {
    document.documentElement.requestFullscreen()
  }
}

function toggleQMT() {
  qmtConnected.value = !qmtConnected.value
  qmtApiStatus.value = qmtConnected.value ? 'healthy' : 'warning'
}

// 表格列定义
const selectionColumns = [
  { title: '代码', key: 'code', width: 70 },
  { title: '名称', key: 'name', width: 90 },
  { title: '策略', key: 'strategy', width: 100 },
  { title: '评分', key: 'score', width: 60, render: (row: any) => h(NTag, { type: 'success', size: 'small' }, { default: () => row.score }) },
  { title: '状态', key: 'status', width: 70 }
]

const positionColumns = [
  { title: '代码', key: 'code', width: 70 },
  { title: '名称', key: 'name', width: 90 },
  { title: '持仓', key: 'size', width: 60 },
  { title: '成本', key: 'cost', width: 70, render: (row: any) => row.cost.toFixed(2) },
  { title: '现价', key: 'current', width: 70, render: (row: any) => row.current.toFixed(2) },
  { title: '盈亏', key: 'profit', width: 80, render: (row: any) => h('span', { class: row.profit >= 0 ? 'rise' : 'fall' }, row.profit) },
  { title: '盈亏%', key: 'profitPercent', width: 70, render: (row: any) => h('span', { class: row.profitPercent >= 0 ? 'rise' : 'fall' }, `${row.profitPercent.toFixed(2)}%`) }
]

// 定时器
let timeTimer: number

onMounted(() => {
  timeTimer = window.setInterval(() => {
    currentTime.value = dayjs().format('HH:mm:ss')
    dateInfo.value = dayjs().format('YYYY年MM月DD日 dddd')
  }, 1000)
})

onUnmounted(() => {
  clearInterval(timeTimer)
})
</script>

<style scoped lang="scss">
.dashboard-screen {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0a1628 100%);
  display: flex;
  flex-direction: column;
  padding: 10px;
  gap: 10px;
  overflow: hidden;
  color: #fff;
}

// 第一行：头部
.row-header {
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: rgba(20, 40, 80, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);

  .index-info {
    display: flex;
    gap: 20px;

    .index-item {
      display: flex;
      align-items: center;
      gap: 8px;

      .index-name {
        color: rgba(255, 255, 255, 0.7);
        font-size: 13px;
      }

      .index-price {
        font-size: 15px;
        font-weight: 600;
      }

      .index-change {
        font-size: 12px;
      }
    }
  }

  .center-time {
    text-align: center;

    .current-time {
      font-size: 24px;
      font-weight: 600;
      color: #00ffcc;
      font-family: 'Courier New', monospace;
    }

    .date-info {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
    }
  }

  .api-status {
    display: flex;
    align-items: center;
    gap: 20px;

    .status-item {
      display: flex;
      align-items: center;
      gap: 6px;

      .status-label {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
      }

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;

        &.healthy { background: #00ff88; }
        &.warning { background: #ffaa00; }
        &.error { background: #ff4466; }
      }

      .status-text {
        font-size: 12px;

        &.healthy { color: #00ff88; }
        &.warning { color: #ffaa00; }
        &.error { color: #ff4466; }
      }
    }

    .user-avatar {
      cursor: pointer;
      background: rgba(0, 170, 255, 0.3);
    }
  }
}

// 涨跌颜色
.rise { color: #00ff88; }
.fall { color: #ff4466; }

// 第二行：统计
.row-stats {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  background: rgba(20, 40, 80, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(100, 150, 255, 0.2);

  .stat-item {
    text-align: center;

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #00ffcc;
    }

    .stat-label {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
    }
  }

  .market-sentiment {
    .sentiment-value {
      font-size: 20px;
      font-weight: 600;

      &.bullish { color: #00ff88; }
      &.bearish { color: #ff4466; }
      &.neutral { color: #ffaa00; }
    }
  }

  .qmt-control {
    margin-left: 20px;
  }
}

// 第三行：选股列表
.row-selection {
  height: 220px;

  .panel {
    height: 100%;
    background: rgba(20, 40, 80, 0.4);
    border-radius: 8px;
    border: 1px solid rgba(100, 150, 255, 0.2);
    display: flex;
    flex-direction: column;

    .panel-header {
      height: 35px;
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

      .panel-count, .panel-total {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.6);
      }
    }

    .panel-content {
      flex: 1;
      padding: 8px;
      overflow: hidden;
    }
  }
}

// 第四行：四个面板
.row-bottom {
  flex: 1;
  display: flex;
  gap: 10px;

  .panel {
    flex: 1;
    background: rgba(20, 40, 80, 0.4);
    border-radius: 8px;
    border: 1px solid rgba(100, 150, 255, 0.2);
    display: flex;
    flex-direction: column;

    .panel-header {
      height: 35px;
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

      .panel-count, .panel-total {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.6);
      }
    }

    .panel-content {
      flex: 1;
      padding: 8px;
      overflow: hidden;
    }

    .scroll-content {
      overflow-y: auto;

      &::-webkit-scrollbar {
        width: 4px;
      }

      &::-webkit-scrollbar-thumb {
        background: rgba(100, 150, 255, 0.3);
        border-radius: 2px;
      }
    }
  }
}

// 股票项样式
.stock-item, .rank-item, .analysis-item {
  padding: 6px 10px;
  border-bottom: 1px solid rgba(100, 150, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;

  .stock-code {
    color: #00aaff;
    min-width: 60px;
  }

  .stock-name {
    color: rgba(255, 255, 255, 0.9);
    min-width: 80px;
  }

  .warning-reason {
    color: #ff4466;
    font-size: 12px;
  }
}

.rank-item {
  .rank-num {
    color: #00ffcc;
    font-weight: 600;
    min-width: 20px;
  }

  .rank-score {
    color: #00ff88;
    font-weight: 500;
  }
}

.analysis-item {
  .analysis-time {
    color: rgba(255, 255, 255, 0.5);
    min-width: 50px;
    font-size: 12px;
  }

  .analysis-content {
    color: rgba(255, 255, 255, 0.8);
  }
}

// 表格样式覆盖
:deep(.n-data-table) {
  background: transparent;

  .n-data-table-th {
    background: rgba(0, 100, 200, 0.3);
    color: #00aaff;
    font-size: 12px;
  }

  .n-data-table-td {
    background: transparent;
    color: #fff;
    font-size: 12px;
  }
}
</style>