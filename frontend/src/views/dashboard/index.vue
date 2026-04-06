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

    <!-- 第二行：涨跌比 + 板块资金 + 策略数 + 因子数 + 市场情绪 + QMT按钮 -->
    <div class="row-stats">
      <div class="stat-item limit-ratio">
        <div class="limit-values">
          <span class="limit-up">{{ limitUpCount }}</span>
          <span class="limit-sep">/</span>
          <span class="limit-down">{{ limitDownCount }}</span>
        </div>
        <div class="stat-label">涨停/跌停</div>
      </div>
      <div class="stat-item sector-funds">
        <div class="sector-list">
          <div class="sector-item" v-for="sector in topSectors" :key="sector.name">
            <span class="sector-name">{{ sector.name }}</span>
            <span class="sector-amount" :class="sector.amount >= 0 ? 'rise' : 'fall'">
              {{ formatSectorAmount(sector.amount) }}
            </span>
          </div>
        </div>
        <div class="stat-label">板块资金TOP5</div>
      </div>
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
            <span class="stock-entry">{{ formatPrice(stock.entry_price) }}</span>
            <span class="stock-price">{{ formatPrice(stock.current_price) }}</span>
            <span class="stock-change" :class="getChangeClass(stock.change_percent)">
              {{ formatChange(stock.change_percent) }}
            </span>
          </div>
        </div>
      </div>

      <div class="panel positions">
        <div class="panel-header">
          <span class="panel-title">持仓信息</span>
          <div class="panel-info">
            <span class="info-item">总资产: ¥{{ formatMoney(balanceInfo.total_asset) }}</span>
            <span class="info-item">可用: ¥{{ formatMoney(balanceInfo.available_cash) }}</span>
            <span class="info-item">市值: ¥{{ formatMoney(totalMarketValue) }}</span>
          </div>
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
          <span class="panel-title">AI交易助手</span>
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NIcon, NAvatar, NDropdown, NDataTable, NTag } from 'naive-ui'
import { PersonOutline, SettingsOutline, TvOutline } from '@vicons/ionicons5'
import dayjs from 'dayjs'
import { fetchPositions, fetchBalance, fetchIndexQuotes } from '@/api/dashboard'
import { sendAIMessage } from '@/api/ai'

const router = useRouter()

// 时间状态
const currentTime = ref(dayjs().format('HH:mm:ss'))
const dateInfo = ref(dayjs().format('YYYY年MM月DD日 dddd'))

// 指数信息（从qmt-service获取）
const indexData = ref([
  { code: 'sh', name: '上证指数', price: 0, change: 0 },
  { code: 'sz', name: '深证成指', price: 0, change: 0 },
  { code: 'cy', name: '创业板指', price: 0, change: 0 },
  { code: 'hs300', name: '沪深300', price: 0, change: 0 }
])

// 加载指数数据
async function loadIndexData() {
  try {
    const indexes = await fetchIndexQuotes()
    if (indexes && indexes.length > 0) {
      indexData.value = indexes.map(idx => ({
        code: idx.code,
        name: idx.name,
        price: idx.price,
        change: idx.change
      }))
      // 更新QMT接口状态为正常
      qmtApiStatus.value = 'healthy'
    }
  } catch (e) {
    console.error('加载指数数据失败', e)
    qmtApiStatus.value = 'error'
  }
}

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

// 涨停跌停统计
const limitUpCount = ref(0)
const limitDownCount = ref(0)

// 板块资金TOP5
const topSectors = ref<{ name: string; amount: number }[]>([])

// 格式化板块资金
function formatSectorAmount(value: number): string {
  if (!value) return '-'
  const absValue = Math.abs(value)
  const sign = value >= 0 ? '+' : '-'
  if (absValue >= 100000000) {
    return sign + (absValue / 100000000).toFixed(2) + '亿'
  } else if (absValue >= 10000) {
    return sign + (absValue / 10000).toFixed(2) + '万'
  }
  return sign + absValue.toFixed(0)
}

// 加载涨跌停和板块资金数据
async function loadMarketData() {
  try {
    // 从QMT服务获取市场统计数据
    const response = await fetch('/api/v1/position/market-stats')
    if (response.ok) {
      const result = await response.json()
      if (result.code === 200 && result.data) {
        limitUpCount.value = result.data.limit_up_count || 0
        limitDownCount.value = result.data.limit_down_count || 0
        topSectors.value = result.data.top_sectors || []
      }
    }
  } catch (e) {
    console.error('加载市场数据失败', e)
    // 模拟数据
    limitUpCount.value = 45
    limitDownCount.value = 12
    topSectors.value = [
      { name: '半导体', amount: 156000000 },
      { name: '新能源', amount: 89000000 },
      { name: '医药', amount: 45000000 },
      { name: '白酒', amount: -23000000 },
      { name: '地产', amount: -56000000 }
    ]
  }
}

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
const selectionPoolRanked = ref<any[]>([])

// 加载选股池数据（监控股票池）
async function loadSelectionPool() {
  try {
    const response = await fetch('/api/monitor/stocks')
    const result = await response.json()
    if (result.code === 200 && result.data) {
      const stocks = result.data
        .filter((item: any) => item.stock_code && item.stock_code !== '2222')
        .map((item: any) => ({
          code: item.stock_code,
          name: item.stock_name,
          score: item.conditions?.length || 0,
          entry_price: item.entry_price,
          current_price: item.last_price,
          change_percent: item.change_percent,
          monitor_type: item.monitor_type,
          remark: item.remark
        }))

      selectionPoolRanked.value = stocks

      // 直接请求QMT获取实时行情
      refreshSelectionPoolQuotes()
    }
  } catch (e) {
    console.error('加载选股池数据失败', e)
  }
}

// 刷新选股池实时行情（从QMT服务）
async function refreshSelectionPoolQuotes() {
  const stockCodes = selectionPoolRanked.value.map(s => s.code).slice(0, 20) // 限制最多20个

  for (const code of stockCodes) {
    try {
      // 转换股票代码格式
      const qmtCode = code.startsWith('6') ? `${code}.SH` : `${code}.SZ`
      const response = await fetch(`/api/v1/position/quote/${qmtCode}`)
      const result = await response.json()

      if (result.code === 200 && result.data && result.data.price) {
        const q = result.data
        const stock = selectionPoolRanked.value.find(s => s.code === code)
        if (stock) {
          const preClose = q.pre_close || 0
          const price = q.price || 0
          stock.current_price = price
          stock.change_percent = preClose > 0 ? ((price - preClose) / preClose * 100) : 0
        }
      } else {
        console.warn(`获取 ${code} 行情数据为空，可能QMT未连接`)
      }
    } catch (e) {
      console.error(`获取 ${code} 行情失败`, e)
    }
  }
}

// 批量获取股票行情
async function fetchStockQuotes(stockCodes: string[]): Promise<Record<string, any>> {
  try {
    const quoteMap: Record<string, any> = {}
    // 逐个获取行情（批量接口有问题）
    for (const code of stockCodes.slice(0, 10)) { // 限制最多10个
      try {
        const response = await fetch(`/api/v1/position/quote/${code}`)
        const result = await response.json()
        if (result.code === 200 && result.data) {
          const q = result.data
          const preClose = q.pre_close || 0
          const lastPrice = q.price || 0
          quoteMap[code] = {
            price: lastPrice,
            change_percent: preClose > 0 ? ((lastPrice - preClose) / preClose * 100) : 0
          }
        }
      } catch (e) {
        console.error(`获取 ${code} 行情失败`, e)
      }
    }
    return quoteMap
  } catch (e) {
    console.error('获取行情失败', e)
    return {}
  }
}

// 持仓信息
const positions = ref<any[]>([])
const balanceInfo = ref({
  total_asset: 0,
  available_cash: 0,
  market_value: 0,
  profit_today: 0,
  profit_total: 0
})

const totalMarketValue = computed(() => {
  const total = positions.value.reduce((sum, p) => sum + p.market_value, 0)
  return total
})

// 格式化金额
function formatMoney(value: number): string {
  if (!value) return '0'
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toLocaleString()
}

// 格式化价格
function formatPrice(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  return value.toFixed(2)
}

// 格式化涨跌幅
function formatChange(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-'
  const sign = value >= 0 ? '+' : ''
  return sign + value.toFixed(2) + '%'
}

// 获取涨跌样式
function getChangeClass(value: number | null | undefined): string {
  if (value === null || value === undefined) return ''
  return value >= 0 ? 'rise' : 'fall'
}

// 加载持仓和资金数据
async function loadPositionData() {
  try {
    const [posData, balData] = await Promise.all([
      fetchPositions(),
      fetchBalance()
    ])
    // fetchPositions已经转换了字段名: position_size, profit_loss, profit_percent
    positions.value = posData.map((p: any) => ({
      code: p.stock_code,
      name: p.stock_name,
      size: p.position_size,
      cost: p.cost_price,
      current: p.current_price,
      profit: p.profit_loss,
      profitPercent: p.profit_percent,
      market_value: p.market_value
    }))
    balanceInfo.value = balData
  } catch (e) {
    console.error('加载持仓数据失败', e)
  }
}

// 分析结果滚动 - 替换为AI聊天
interface ChatMsg {
  role: 'user' | 'assistant'
  content: string
}

const chatMessages = ref<ChatMsg[]>([
  { role: 'assistant', content: '您好！我是AI交易助手，可以帮您查询行情、查看持仓、买卖股票。例如：\n• 平安银行现在多少钱\n• 我的持仓\n• 买入平安银行100股' }
])
const userInput = ref('')
const aiThinking = ref(false)

const chatMessagesRef = ref<HTMLElement | null>(null)

// 滚动聊天到底部
function scrollChatToBottom() {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

async function sendChatMessage() {
  if (!userInput.value.trim() || aiThinking.value) return

  const message = userInput.value.trim()
  chatMessages.value.push({ role: 'user', content: message })
  scrollChatToBottom()
  userInput.value = ''
  aiThinking.value = true

  try {
    const result = await sendAIMessage(message)
    chatMessages.value.push({
      role: 'assistant',
      content: result.content
    })
    scrollChatToBottom()
  } catch (e) {
    chatMessages.value.push({
      role: 'assistant',
      content: '抱歉，处理您的请求时出错：' + ((e as Error).message || '未知错误')
    })
    scrollChatToBottom()
  } finally {
    aiThinking.value = false
  }
}

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
let dataTimer: number

onMounted(() => {
  timeTimer = window.setInterval(() => {
    currentTime.value = dayjs().format('HH:mm:ss')
    dateInfo.value = dayjs().format('YYYY年MM月DD日 dddd')
  }, 1000)

  // 加载指数数据
  loadIndexData()

  // 加载持仓数据
  loadPositionData()

  // 加载选股池数据
  loadSelectionPool()

  // 加载市场数据（涨跌停、板块资金）
  loadMarketData()

  // 每30秒刷新数据
  dataTimer = window.setInterval(() => {
    loadIndexData()
    loadPositionData()
    loadSelectionPool()
    loadMarketData()
  }, 30000)
})

onUnmounted(() => {
  clearInterval(timeTimer)
  clearInterval(dataTimer)
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

// 涨跌颜色（红涨绿跌）
.rise { color: #ff4466; }
.fall { color: #00ff88; }

// 第二行：统计
.row-stats {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
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

  .limit-ratio {
    min-width: 80px;

    .limit-values {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      font-size: 24px;
      font-weight: 600;

      .limit-up {
        color: #ff4466;
      }

      .limit-down {
        color: #00ff88;
      }

      .limit-sep {
        color: rgba(255, 255, 255, 0.5);
        margin: 0 2px;
      }
    }
  }

  .sector-funds {
    min-width: 500px;

    .sector-list {
      display: flex;
      align-items: center;
      justify-content: space-around;
      gap: 10px;
      height: 40px;

      .sector-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 11px;

        .sector-name {
          color: rgba(255, 255, 255, 0.8);
          margin-bottom: 2px;
        }

        .sector-amount {
          font-weight: 500;
          font-size: 12px;
        }
      }
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

      .panel-info {
        display: flex;
        gap: 15px;

        .info-item {
          font-size: 12px;
          color: rgba(255, 255, 255, 0.8);
        }
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

    .chat-window {
      display: flex;
      flex-direction: column;
      padding: 0;
      height: 100%;

      .chat-messages {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 8px;

        &::-webkit-scrollbar {
          width: 4px;
        }

        &::-webkit-scrollbar-thumb {
          background: rgba(100, 150, 255, 0.3);
          border-radius: 2px;
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
        display: flex;
        gap: 8px;
        padding: 8px;
        border-top: 1px solid rgba(100, 150, 255, 0.2);
        background: rgba(20, 40, 80, 0.3);

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

// 股票项样式
.stock-item, .rank-item {
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

  .stock-entry {
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
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