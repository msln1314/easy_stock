/**
 * ECharts 完整导入配置
 */
import * as echarts from 'echarts'
import VChart from 'vue-echarts'
import type { App } from 'vue'

// 注册 vue-echarts 全局组件
export function setupECharts(app: App) {
  app.component('VChart', VChart)
}

export { echarts, VChart }
export default echarts