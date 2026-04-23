<template>
  <div class="trade-page">
    <!-- 交易状态头部 -->
    <div class="trade-header">
      <div class="status-card">
        <div class="status-indicator" :class="tradeStatus?.is_trade_time ? 'active' : 'inactive'"></div>
        <div class="status-info">
          <div class="status-text">
            <span class="time">{{ tradeStatus?.current_time || '--:--:--' }}</span>
            <n-tag :type="tradeStatus?.is_trade_time ? 'success' : 'default'" size="small">
              {{ tradeStatus?.is_trade_time ? '交易中' : '已闭市' }}
            </n-tag>
          </div>
          <div class="date-info">
            {{ tradeStatus?.current_date }} {{ tradeStatus?.weekday }}
            <span v-if="!tradeStatus?.is_trade_time && tradeStatus?.next_trade_time">
              | 下个交易时段: {{ tradeStatus?.next_trade_time }}
            </span>
          </div>
        </div>
      </div>

      <div class="balance-cards">
        <div class="balance-card">
          <div class="label">总资产</div>
          <div class="value">{{ formatMoney(balance?.total_asset) }}</div>
        </div>
        <div class="balance-card">
          <div class="label">可用资金</div>
          <div class="value available">{{ formatMoney(balance?.available_cash) }}</div>
        </div>
        <div class="balance-card">
          <div class="label">持仓市值</div>
          <div class="value">{{ formatMoney(balance?.market_value) }}</div>
        </div>
        <div class="balance-card">
          <div class="label">今日盈亏</div>
          <div class="value" :class="balance?.profit_today >= 0 ? 'profit' : 'loss'">
            {{ balance?.profit_today >= 0 ? '+' : '' }}{{ formatMoney(balance?.profit_today) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="trade-content">
      <!-- 左侧：持仓列表 -->
      <div class="position-panel">
        <div class="panel-header">
          <span class="title">持仓列表</span>
          <n-button size="small" @click="loadPositions">刷新</n-button>
        </div>
        <n-spin :show="loadingPositions">
          <n-data-table
            :columns="positionColumns"
            :data="positions"
            :row-key="(row: Position) => row.stock_code"
            striped
            size="small"
            :max-height="400"
          />
        </n-spin>
      </div>

      <!-- 右侧：交易面板 -->
      <div class="trade-panel">
        <n-tabs type="line" animated>
          <n-tab-pane name="buy" tab="买入">
            <div class="trade-form">
              <n-form :model="buyForm" label-placement="left" label-width="70">
                <n-form-item label="股票代码">
                  <n-input v-model:value="buyForm.stock_code" placeholder="如：000001" @blur="loadQuote(buyForm.stock_code, 'buy')" />
                </n-form-item>
                <n-form-item label="股票名称">
                  <span>{{ buyQuote?.stock_name || '--' }}</span>
                </n-form-item>
                <n-form-item label="现价">
                  <span class="price" :class="buyQuote?.change >= 0 ? 'rise' : 'fall'">
                    {{ buyQuote?.price?.toFixed(2) || '--' }}
                    <span v-if="buyQuote?.change !== undefined">
                      ({{ buyQuote?.change >= 0 ? '+' : '' }}{{ buyQuote?.change_pct?.toFixed(2) }}%)
                    </span>
                  </span>
                </n-form-item>
                <n-form-item label="委托价格">
                  <n-input-number v-model:value="buyForm.price" :precision="2" :min="0" style="width: 150px" />
                  <n-button size="small" quaternary @click="buyForm.price = buyQuote?.limit_up || 0">涨停</n-button>
                </n-form-item>
                <n-form-item label="委托数量">
                  <n-input-number v-model:value="buyForm.quantity" :min="100" :step="100" style="width: 150px" />
                  <span class="hint">可用: {{ formatMoney(balance?.available_cash) }}</span>
                </n-form-item>
                <n-form-item label="预估金额">
                  <span class="amount">{{ formatMoney(buyForm.price * buyForm.quantity) }}</span>
                </n-form-item>
                <div class="trade-actions">
                  <n-button type="primary" block @click="handleBuy" :loading="buying">
                    限价买入
                  </n-button>
                  <n-button type="info" block @click="handleQuickBuy" :loading="buying">
                    快捷买入
                  </n-button>
                </div>
              </n-form>
            </div>
          </n-tab-pane>

          <n-tab-pane name="sell" tab="卖出">
            <div class="trade-form">
              <n-form :model="sellForm" label-placement="left" label-width="70">
                <n-form-item label="股票代码">
                  <n-input v-model:value="sellForm.stock_code" placeholder="如：000001" @blur="loadQuote(sellForm.stock_code, 'sell')" />
                </n-form-item>
                <n-form-item label="股票名称">
                  <span>{{ sellQuote?.stock_name || '--' }}</span>
                </n-form-item>
                <n-form-item label="现价">
                  <span class="price" :class="sellQuote?.change >= 0 ? 'rise' : 'fall'">
                    {{ sellQuote?.price?.toFixed(2) || '--' }}
                    <span v-if="sellQuote?.change !== undefined">
                      ({{ sellQuote?.change >= 0 ? '+' : '' }}{{ sellQuote?.change_pct?.toFixed(2) }}%)
                    </span>
                  </span>
                </n-form-item>
                <n-form-item label="委托价格">
                  <n-input-number v-model:value="sellForm.price" :precision="2" :min="0" style="width: 150px" />
                  <n-button size="small" quaternary @click="sellForm.price = sellQuote?.limit_down || 0">跌停</n-button>
                </n-form-item>
                <n-form-item label="委托数量">
                  <n-input-number v-model:value="sellForm.quantity" :min="100" :step="100" style="width: 150px" />
                  <n-button size="small" quaternary v-if="selectedPosition" @click="sellForm.quantity = selectedPosition.available">
                    全部
                  </n-button>
                </n-form-item>
                <n-form-item label="可卖数量">
                  <span>{{ selectedPosition?.available || 0 }} 股</span>
                </n-form-item>
                <div class="trade-actions">
                  <n-button type="warning" block @click="handleSell" :loading="selling">
                    限价卖出
                  </n-button>
                  <n-button type="error" block @click="handleQuickSell" :loading="selling">
                    快捷卖出
                  </n-button>
                </div>
              </n-form>
            </div>
          </n-tab-pane>
        </n-tabs>
      </div>
    </div>

    <!-- 今日委托和成交 -->
    <div class="trade-records">
      <n-tabs type="line" animated>
        <n-tab-pane name="entrusts" tab="今日委托">
          <n-data-table
            :columns="entrustColumns"
            :data="entrusts"
            :row-key="(row: Entrust) => row.order_id"
            striped
            size="small"
            :max-height="200"
          />
        </n-tab-pane>
        <n-tab-pane name="trades" tab="今日成交">
          <n-data-table
            :columns="tradeColumns"
            :data="trades"
            :row-key="(row: Trade) => row.order_id"
            striped
            size="small"
            :max-height="200"
          />
        </n-tab-pane>
      </n-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import {
  NButton, NSpin, NTag, NDataTable, NInput, NInputNumber, NForm, NFormItem,
  NTabs, NTabPane, useMessage
} from 'naive-ui'
import {
  fetchPositions, fetchBalance, fetchTodayTrades, fetchTodayEntrusts,
  fetchTradeStatus, fetchStockQuote, buyStock, sellStock, quickBuy, quickSell, cancelOrder,
  Position, Balance, Trade, Entrust, TradeStatus
} from '@/api/trade'

const message = useMessage()

// 数据
const positions = ref<Position[]>([])
const balance = ref<Balance | null>(null)
const trades = ref<Trade[]>([])
const entrusts = ref<Entrust[]>([])
const tradeStatus = ref<TradeStatus | null>(null)

const loadingPositions = ref(false)
const buying = ref(false)
const selling = ref(false)

// 买入表单
const buyForm = ref({
  stock_code: '',
  price: 0,
  quantity: 100
})
const buyQuote = ref<any>(null)

// 卖出表单
const sellForm = ref({
  stock_code: '',
  price: 0,
  quantity: 100
})
const sellQuote = ref<any>(null)
const selectedPosition = computed(() =>
  positions.value.find(p => p.stock_code === sellForm.value.stock_code)
)

// 格式化金额
function formatMoney(val: number | undefined | null): string {
  if (val == null) return '--'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 持仓表格列
const positionColumns = [
  { title: '代码', key: 'stock_code', width: 80 },
  { title: '名称', key: 'stock_name', width: 80 },
  { title: '持仓', key: 'quantity', width: 80 },
  { title: '可卖', key: 'available', width: 80 },
  {
    title: '成本', key: 'cost_price', width: 80,
    render: (row: Position) => row.cost_price.toFixed(2)
  },
  {
    title: '现价', key: 'current_price', width: 80,
    render: (row: Position) => h('span', { class: row.profit_rate >= 0 ? 'rise' : 'fall' }, row.current_price.toFixed(2))
  },
  {
    title: '盈亏', key: 'profit', width: 100,
    render: (row: Position) => {
      const color = row.profit >= 0 ? '#d03050' : '#18a058'
      return h('span', { style: { color } }, `${row.profit >= 0 ? '+' : ''}${row.profit.toFixed(2)}`)
    }
  },
  {
    title: '收益率', key: 'profit_rate', width: 80,
    render: (row: Position) => {
      const color = row.profit_rate >= 0 ? '#d03050' : '#18a058'
      return h('span', { style: { color } }, `${row.profit_rate >= 0 ? '+' : ''}${row.profit_rate.toFixed(2)}%`)
    }
  },
  {
    title: '操作', key: 'actions', width: 80,
    render: (row: Position) => h(NButton, {
      size: 'tiny', type: 'warning', onClick: () => {
        sellForm.value.stock_code = row.stock_code
        sellForm.value.price = row.current_price
        sellForm.value.quantity = Math.min(100, row.available)
        loadQuote(row.stock_code, 'sell')
      }
    }, { default: () => '卖出' })
  }
]

// 委托表格列
const entrustColumns = [
  { title: '代码', key: 'stock_code', width: 80 },
  { title: '名称', key: 'stock_name', width: 80 },
  {
    title: '方向', key: 'direction', width: 60,
    render: (row: Entrust) => h(NTag, {
      type: row.direction === 'buy' ? 'success' : 'warning', size: 'small'
    }, { default: () => row.direction === 'buy' ? '买' : '卖' })
  },
  { title: '价格', key: 'price', width: 80 },
  { title: '委托', key: 'quantity', width: 80 },
  { title: '成交', key: 'traded_quantity', width: 80 },
  { title: '状态', key: 'status', width: 80 },
  { title: '时间', key: 'entrust_time', width: 100 }
]

// 成交表格列
const tradeColumns = [
  { title: '代码', key: 'stock_code', width: 80 },
  { title: '名称', key: 'stock_name', width: 80 },
  {
    title: '方向', key: 'direction', width: 60,
    render: (row: Trade) => h(NTag, {
      type: row.direction === 'buy' ? 'success' : 'warning', size: 'small'
    }, { default: () => row.direction === 'buy' ? '买' : '卖' })
  },
  { title: '价格', key: 'price', width: 80 },
  { title: '数量', key: 'quantity', width: 80 },
  { title: '金额', key: 'amount', width: 100 },
  { title: '时间', key: 'traded_time', width: 100 }
]

// 加载数据
async function loadPositions() {
  loadingPositions.value = true
  try {
    const data = await fetchPositions()
    positions.value = data.positions || []
  } catch (error) {
    console.error('加载持仓失败:', error)
  } finally {
    loadingPositions.value = false
  }
}

async function loadBalance() {
  try {
    balance.value = await fetchBalance()
  } catch (error) {
    console.error('加载资金失败:', error)
  }
}

async function loadTrades() {
  try {
    const data = await fetchTodayTrades()
    trades.value = data.trades || []
  } catch (error) {
    console.error('加载成交失败:', error)
  }
}

async function loadEntrusts() {
  try {
    const data = await fetchTodayEntrusts()
    entrusts.value = data.entrusts || []
  } catch (error) {
    console.error('加载委托失败:', error)
  }
}

async function loadTradeStatus() {
  try {
    tradeStatus.value = await fetchTradeStatus()
  } catch (error) {
    console.error('加载交易状态失败:', error)
  }
}

async function loadQuote(stockCode: string, type: 'buy' | 'sell') {
  if (!stockCode) return
  try {
    const quote = await fetchStockQuote(stockCode)
    if (type === 'buy') {
      buyQuote.value = quote
      buyForm.value.price = quote.price || 0
    } else {
      sellQuote.value = quote
      sellForm.value.price = quote.price || 0
    }
  } catch (error) {
    console.error('加载行情失败:', error)
  }
}

// 买入
async function handleBuy() {
  if (!buyForm.value.stock_code || buyForm.value.price <= 0 || buyForm.value.quantity < 100) {
    message.warning('请填写完整信息')
    return
  }
  buying.value = true
  try {
    const result = await buyStock({
      stock_code: buyForm.value.stock_code,
      price: buyForm.value.price,
      quantity: buyForm.value.quantity
    })
    message.success(result.message || '买入委托成功')
    loadEntrusts()
    loadBalance()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '买入失败')
  } finally {
    buying.value = false
  }
}

// 快捷买入
async function handleQuickBuy() {
  if (!buyForm.value.stock_code || buyForm.value.quantity < 100) {
    message.warning('请填写股票代码和数量')
    return
  }
  buying.value = true
  try {
    const result = await quickBuy({
      stock_code: buyForm.value.stock_code,
      price: buyForm.value.price,
      quantity: buyForm.value.quantity
    })
    message.success(result.message || '快捷买入成功')
    loadEntrusts()
    loadBalance()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '买入失败')
  } finally {
    buying.value = false
  }
}

// 卖出
async function handleSell() {
  if (!sellForm.value.stock_code || sellForm.value.price <= 0 || sellForm.value.quantity < 100) {
    message.warning('请填写完整信息')
    return
  }
  selling.value = true
  try {
    const result = await sellStock({
      stock_code: sellForm.value.stock_code,
      price: sellForm.value.price,
      quantity: sellForm.value.quantity
    })
    message.success(result.message || '卖出委托成功')
    loadEntrusts()
    loadBalance()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '卖出失败')
  } finally {
    selling.value = false
  }
}

// 快捷卖出
async function handleQuickSell() {
  if (!sellForm.value.stock_code || sellForm.value.quantity < 100) {
    message.warning('请填写股票代码和数量')
    return
  }
  selling.value = true
  try {
    const result = await quickSell({
      stock_code: sellForm.value.stock_code,
      price: sellForm.value.price,
      quantity: sellForm.value.quantity
    })
    message.success(result.message || '快捷卖出成功')
    loadEntrusts()
    loadBalance()
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '卖出失败')
  } finally {
    selling.value = false
  }
}

onMounted(() => {
  loadTradeStatus()
  loadPositions()
  loadBalance()
  loadTrades()
  loadEntrusts()

  // 定时刷新交易状态
  setInterval(() => {
    loadTradeStatus()
  }, 1000)
})
</script>

<style scoped lang="scss">
.trade-page {
  padding: 16px;
  height: calc(100vh - 50px - 32px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trade-header {
  display: flex;
  gap: 16px;

  .status-card {
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 280px;

    .status-indicator {
      width: 12px;
      height: 12px;
      border-radius: 50%;

      &.active {
        background: #18a058;
        box-shadow: 0 0 8px #18a058;
      }

      &.inactive {
        background: #ccc;
      }
    }

    .status-info {
      .status-text {
        display: flex;
        align-items: center;
        gap: 8px;

        .time {
          font-size: 20px;
          font-weight: 600;
          font-family: monospace;
        }
      }

      .date-info {
        font-size: 12px;
        color: #666;
        margin-top: 4px;
      }
    }
  }

  .balance-cards {
    flex: 1;
    display: flex;
    gap: 12px;

    .balance-card {
      flex: 1;
      background: #fff;
      border-radius: 8px;
      padding: 16px;

      .label {
        font-size: 12px;
        color: #666;
      }

      .value {
        font-size: 18px;
        font-weight: 600;
        margin-top: 4px;

        &.available {
          color: #2080f0;
        }

        &.profit {
          color: #d03050;
        }

        &.loss {
          color: #18a058;
        }
      }
    }
  }
}

.trade-content {
  display: flex;
  gap: 16px;
  flex: 1;

  .position-panel {
    flex: 1;
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    display: flex;
    flex-direction: column;

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .title {
        font-weight: 500;
      }
    }
  }

  .trade-panel {
    width: 360px;
    background: #fff;
    border-radius: 8px;
    padding: 16px;

    .trade-form {
      padding: 8px 0;

      .price {
        font-size: 16px;
        font-weight: 600;

        &.rise { color: #18a058; }
        &.fall { color: #d03050; }
      }

      .hint {
        margin-left: 8px;
        font-size: 12px;
        color: #666;
      }

      .amount {
        font-size: 16px;
        font-weight: 600;
        color: #2080f0;
      }

      .trade-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 16px;
      }
    }
  }
}

.trade-records {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.rise { color: #d03050; }
.fall { color: #18a058; }
</style>