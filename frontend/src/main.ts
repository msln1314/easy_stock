/**
 * 应用入口
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import NaiveUI from 'naive-ui'
import router from './router'
import App from './App.vue'

// ECharts 完整导入
import { setupECharts } from './utils/echarts'

// 权限指令
import { setupPermissionDirectives } from './directives/permission'

// 样式
import '@unocss/reset/tailwind-compat.css'
import 'virtual:uno.css'
import './styles/index.scss'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(NaiveUI)

// 注册 ECharts 组件
setupECharts(app)

// 注册权限指令
setupPermissionDirectives(app)

app.mount('#app')