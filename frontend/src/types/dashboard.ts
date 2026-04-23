/**
 * 仪表盘布局相关类型定义
 */

/**
 * Grid布局项（vue-grid-layout格式）
 */
export interface GridLayoutItem {
  i: string      // 模块ID
  x: number      // 列位置 (0-11)
  y: number      // 行位置
  w: number      // 宽度 (1-12)
  h: number      // 高度
  minW?: number  // 最小宽度
  minH?: number  // 最小高度
  static?: boolean // 是否固定不可拖拽
}

/**
 * 仪表盘布局配置
 */
export interface DashboardLayoutConfig {
  id: number
  name: string
  userId: number
  layout: GridLayoutItem[]
  isDefault: boolean
  createdAt: string
  updatedAt: string
}

/**
 * 创建布局请求
 */
export interface LayoutCreateRequest {
  name: string
  layout: GridLayoutItem[]
  is_default?: boolean
}

/**
 * 更新布局请求
 */
export interface LayoutUpdateRequest {
  name?: string
  layout?: GridLayoutItem[]
  is_default?: boolean
}

/**
 * 模块定义
 */
export interface DashboardModule {
  id: string
  name: string
  component: string
  defaultLayout: GridLayoutItem
  icon?: string
}

/**
 * 所有可用的模块定义（包含默认和可选模块）
 */
export const ALL_MODULES: DashboardModule[] = [
  // 默认模块
  {
    id: 'market-overview',
    name: '大盘概览',
    component: 'MarketOverview',
    defaultLayout: { i: 'market-overview', x: 0, y: 0, w: 12, h: 1, minW: 8, minH: 1 },
    icon: 'GridOutline'
  },
  {
    id: 'positions',
    name: '持仓信息',
    component: 'PositionsPanel',
    defaultLayout: { i: 'positions', x: 0, y: 1, w: 4, h: 4, minW: 3, minH: 3 },
    icon: 'WalletOutline'
  },
  {
    id: 'ai-assistant',
    name: 'AI交易助手',
    component: 'AIAssistantPanel',
    defaultLayout: { i: 'ai-assistant', x: 4, y: 1, w: 4, h: 4, minW: 3, minH: 4 },
    icon: 'SparklesOutline'
  },
  {
    id: 'sell-warning',
    name: '卖出预警池',
    component: 'SellWarningPanel',
    defaultLayout: { i: 'sell-warning', x: 8, y: 1, w: 4, h: 4, minW: 3, minH: 3 },
    icon: 'WarningOutline'
  },
  // 可选模块
  {
    id: 'market-sentiment',
    name: '市场情绪',
    component: 'MarketSentimentPanel',
    defaultLayout: { i: 'market-sentiment', x: 0, y: 5, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'PulseOutline'
  },
  {
    id: 'strategy-monitor',
    name: '策略监控',
    component: 'StrategyMonitorPanel',
    defaultLayout: { i: 'strategy-monitor', x: 3, y: 5, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'RocketOutline'
  },
  {
    id: 'capital-overview',
    name: '资金概览',
    component: 'CapitalOverviewPanel',
    defaultLayout: { i: 'capital-overview', x: 6, y: 5, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'CardOutline'
  },
  {
    id: 'etf-rotation-signal',
    name: 'ETF轮动信号',
    component: 'ETFRotationSignalPanel',
    defaultLayout: { i: 'etf-rotation-signal', x: 9, y: 5, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'RefreshOutline'
  },
  {
    id: 'risk-control',
    name: '风控指标',
    component: 'RiskControlPanel',
    defaultLayout: { i: 'risk-control', x: 0, y: 9, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'ShieldCheckmarkOutline'
  },
  {
    id: 'fund-flow',
    name: '资金流向',
    component: 'FundFlowPanel',
    defaultLayout: { i: 'fund-flow', x: 3, y: 9, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'WaterOutline'
  },
  {
    id: 'order-status',
    name: '委托状态',
    component: 'OrderStatusPanel',
    defaultLayout: { i: 'order-status', x: 6, y: 9, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'DocumentTextOutline'
  },
  {
    id: 'notification',
    name: '信息通知',
    component: 'NotificationPanel',
    defaultLayout: { i: 'notification', x: 9, y: 9, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'NotificationsOutline'
  },
  {
    id: 'strategy-track-pool',
    name: '策略选股池',
    component: 'StrategyTrackPool',
    defaultLayout: { i: 'strategy-track-pool', x: 0, y: 13, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'TrendingUpOutline'
  },
  {
    id: 'real-trade-records',
    name: '实时成交记录',
    component: 'RealTradeRecords',
    defaultLayout: { i: 'real-trade-records', x: 3, y: 13, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'SwapHorizontalOutline'
  },
  {
    id: 'trade-records',
    name: '交易记录',
    component: 'TradeRecordsPanel',
    defaultLayout: { i: 'trade-records', x: 6, y: 13, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'TimeOutline'
  },
  {
    id: 'selection-pool',
    name: '选股池排序',
    component: 'SelectionPoolPanel',
    defaultLayout: { i: 'selection-pool', x: 9, y: 13, w: 3, h: 4, minW: 3, minH: 3 },
    icon: 'FilterOutline'
  }
]

/**
 * 默认启用的模块配置（核心模块）
 */
export const DEFAULT_MODULES: DashboardModule[] = [
  ALL_MODULES[0], // 大盘概览
  ALL_MODULES[1], // 持仓信息
  ALL_MODULES[2], // AI交易助手
  ALL_MODULES[3], // 卖出预警池
]

/**
 * 获取默认布局
 */
export function getDefaultLayout(): GridLayoutItem[] {
  return DEFAULT_MODULES.map(m => m.defaultLayout)
}

/**
 * 获取模块默认布局配置
 */
export function getModuleDefaultLayout(moduleId: string): GridLayoutItem | undefined {
  return ALL_MODULES.find(m => m.id === moduleId)?.defaultLayout
}

/**
 * 获取未使用的模块列表
 */
export function getUnusedModules(currentLayout: GridLayoutItem[]): DashboardModule[] {
  const usedIds = currentLayout.map(item => item.i)
  return ALL_MODULES.filter(m => !usedIds.includes(m.id))
}