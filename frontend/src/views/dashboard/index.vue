<template>
  <div class="dashboard-screen">
    <!-- 固定头部：指数 + 时间 + 接口状态 + 布局控制 + 用户 -->
    <HeaderBar
      ref="headerBarRef"
      :edit-mode="editMode"
      :current-layout-id="currentLayoutId"
      :layout-options="layoutOptions"
      :unused-modules="unusedModules"
      @toggle-edit="toggleEditMode"
      @change-layout="handleLayoutChange"
      @save="openSaveModal"
      @reset="resetToDefault"
      @add-module="handleAddModule"
      @user-action="handleUserAction"
    />

    <!-- Grid布局区域 -->
    <div class="grid-container" ref="gridContainerRef" :class="{ 'edit-mode': editMode }">
      <GridLayout
        v-model:layout="currentLayout"
        :col-num="12"
        :row-height="80"
        :margin="[8, 8]"
        :is-draggable="editMode"
        :is-resizable="editMode"
        :vertical-compact="true"
        :use-css-transforms="true"
        :responsive="true"
        :width="containerWidth"
      >
        <GridItem
          v-for="item in currentLayout"
          :key="item.i"
          :i="item.i"
          :x="item.x"
          :y="item.y"
          :w="item.w"
          :h="item.h"
          :min-w="item.minW || 2"
          :min-h="item.minH || 2"
        >
          <div class="grid-item-content" :class="{ 'edit-mode': editMode }">
            <!-- 编辑模式下显示移除按钮 -->
            <div v-if="editMode" class="remove-btn" @click="handleRemoveModule(item.i)">
              <n-icon size="16"><CloseOutline /></n-icon>
            </div>
            <MarketOverview v-if="item.i === 'market-overview'" ref="marketOverviewRef" />
            <PositionsPanel v-else-if="item.i === 'positions'" ref="positionsRef" />
            <AIAssistantPanel v-else-if="item.i === 'ai-assistant'" ref="aiAssistantRef" />
            <SellWarningPanel v-else-if="item.i === 'sell-warning'" ref="sellWarningRef" />
            <TradeRecordsPanel v-else-if="item.i === 'trade-records'" ref="tradeRecordsRef" />
            <SelectionPoolPanel v-else-if="item.i === 'selection-pool'" ref="selectionPoolRef" />
            <NotificationPanel v-else-if="item.i === 'notification'" ref="notificationRef" />
            <StrategyTrackPool v-else-if="item.i === 'strategy-track-pool'" ref="strategyTrackPoolRef" />
            <RealTradeRecords v-else-if="item.i === 'real-trade-records'" ref="realTradeRecordsRef" />
            <StrategyMonitorPanel v-else-if="item.i === 'strategy-monitor'" ref="strategyMonitorRef" />
            <CapitalOverviewPanel v-else-if="item.i === 'capital-overview'" ref="capitalOverviewRef" />
            <ETFRotationSignalPanel v-else-if="item.i === 'etf-rotation-signal'" ref="etfRotationSignalRef" />
            <RiskControlPanel v-else-if="item.i === 'risk-control'" ref="riskControlRef" />
            <FundFlowPanel v-else-if="item.i === 'fund-flow'" ref="fundFlowRef" />
            <OrderStatusPanel v-else-if="item.i === 'order-status'" ref="orderStatusRef" />
            <MarketSentimentPanel v-else-if="item.i === 'market-sentiment'" ref="marketSentimentRef" />
          </div>
        </GridItem>
      </GridLayout>
    </div>

    <!-- 保存布局弹窗 -->
    <n-modal v-model:show="showSaveModal" preset="dialog" :title="saveModalTitle">
      <n-form>
        <n-form-item label="布局名称">
          <n-input
            v-model:value="newLayoutName"
            :placeholder="isUpdatingExisting ? '修改布局名称（可选）' : '请输入新的布局名称'"
            :disabled="isUpdatingExisting"
          />
          <div v-if="isNameDuplicate && !isUpdatingExisting" class="name-error-tip">此名称已存在，请使用其他名称</div>
        </n-form-item>
        <n-form-item label="设为默认">
          <n-switch v-model:value="saveAsDefault" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showSaveModal = false">取消</n-button>
        <n-button
          type="primary"
          :disabled="(!isUpdatingExisting && (isNameDuplicate || !newLayoutName.trim()))"
          @click="saveLayout"
        >
          {{ isUpdatingExisting ? '更新' : '保存' }}
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { NModal, NForm, NFormItem, NInput, NSwitch, NButton, NIcon, useMessage, useDialog } from 'naive-ui'
import { CloseOutline } from '@vicons/ionicons5'
import { GridLayout, GridItem } from 'grid-layout-plus'
import type { GridLayoutItem, DashboardModule } from '@/types/dashboard'
import { ALL_MODULES, DEFAULT_MODULES, getModuleDefaultLayout, getUnusedModules } from '@/types/dashboard'
import { getLayouts, getDefaultLayout as fetchDefaultLayout, createLayout, updateLayout, deleteLayout } from '@/api/dashboard'

import HeaderBar from '@/components/dashboard/HeaderBar.vue'
import MarketOverview from '@/components/dashboard/MarketOverview.vue'
import PositionsPanel from '@/components/dashboard/PositionsPanel.vue'
import AIAssistantPanel from '@/components/dashboard/AIAssistantPanel.vue'
import SellWarningPanel from '@/components/dashboard/SellWarningPanel.vue'
import TradeRecordsPanel from '@/components/dashboard/TradeRecordsPanel.vue'
import SelectionPoolPanel from '@/components/dashboard/SelectionPoolPanel.vue'
import NotificationPanel from '@/components/dashboard/NotificationPanel.vue'
import StrategyTrackPool from '@/components/dashboard/StrategyTrackPool.vue'
import RealTradeRecords from '@/components/dashboard/RealTradeRecords.vue'
import StrategyMonitorPanel from '@/components/dashboard/StrategyMonitorPanel.vue'
import CapitalOverviewPanel from '@/components/dashboard/CapitalOverviewPanel.vue'
import ETFRotationSignalPanel from '@/components/dashboard/ETFRotationSignalPanel.vue'
import RiskControlPanel from '@/components/dashboard/RiskControlPanel.vue'
import FundFlowPanel from '@/components/dashboard/FundFlowPanel.vue'
import OrderStatusPanel from '@/components/dashboard/OrderStatusPanel.vue'
import MarketSentimentPanel from '@/components/dashboard/MarketSentimentPanel.vue'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

// Grid容器
const gridContainerRef = ref<HTMLElement | null>(null)
const containerWidth = ref(1200)

// 编辑模式
const editMode = ref(false)

// 布局数据
const currentLayout = ref<GridLayoutItem[]>(getDefaultLayout())
const savedLayouts = ref<any[]>([])
const currentLayoutId = ref<number | null>(null)

// 组件引用
const headerBarRef = ref<any>(null)
const marketOverviewRef = ref<any>(null)
const positionsRef = ref<any>(null)
const aiAssistantRef = ref<any>(null)
const sellWarningRef = ref<any>(null)
const tradeRecordsRef = ref<any>(null)
const selectionPoolRef = ref<any>(null)
const notificationRef = ref<any>(null)
const strategyTrackPoolRef = ref<any>(null)
const realTradeRecordsRef = ref<any>(null)
const strategyMonitorRef = ref<any>(null)
const capitalOverviewRef = ref<any>(null)
const etfRotationSignalRef = ref<any>(null)
const riskControlRef = ref<any>(null)
const fundFlowRef = ref<any>(null)
const orderStatusRef = ref<any>(null)
const marketSentimentRef = ref<any>(null)

// 保存布局弹窗
const showSaveModal = ref(false)
const newLayoutName = ref('')
const saveAsDefault = ref(false)

// 名称重复检查（仅新增时）
const isNameDuplicate = computed(() => {
  const name = newLayoutName.value.trim().toLowerCase()
  if (!name) return false
  return savedLayouts.value.some(l => l.name.toLowerCase() === name)
})

// 是否更新已有布局
const isUpdatingExisting = computed(() => {
  return currentLayoutId.value !== null && currentLayoutId.value !== 0
})

// 弹窗标题
const saveModalTitle = computed(() => {
  return isUpdatingExisting.value ? '更新当前布局' : '保存为新布局'
})

// 布局选项
const layoutOptions = computed(() => [
  { label: '默认布局', value: 0 },
  ...savedLayouts.value.map(l => ({
    label: l.name + (l.is_default ? '(默认)' : ''),
    value: l.id
  }))
])

// 未使用的模块（可用于添加）
const unusedModules = computed(() => getUnusedModules(currentLayout.value))

// 获取默认布局
function getDefaultLayout(): GridLayoutItem[] {
  return DEFAULT_MODULES.map(m => m.defaultLayout)
}

// 加载布局列表
async function loadLayouts() {
  try {
    const layouts = await getLayouts()
    savedLayouts.value = layouts

    // 加载默认布局
    const defaultLayout = await fetchDefaultLayout()
    if (defaultLayout && defaultLayout.id !== 0) {
      currentLayoutId.value = defaultLayout.id
      currentLayout.value = defaultLayout.layout.map((item: any) => ({
        i: item.i,
        x: item.x,
        y: item.y,
        w: item.w,
        h: item.h,
        minW: item.minW,
        minH: item.minH
      }))
    }
  } catch (e) {
    console.error('加载布局失败', e)
  }
}

// 切换布局
function handleLayoutChange(layoutId: number) {
  if (layoutId === 0) {
    resetToDefault()
    return
  }

  const layout = savedLayouts.value.find(l => l.id === layoutId)
  if (layout) {
    currentLayoutId.value = layoutId
    currentLayout.value = layout.layout.map((item: any) => ({
      i: item.i,
      x: item.x,
      y: item.y,
      w: item.w,
      h: item.h,
      minW: item.minW,
      minH: item.minH
    }))
  }
}

// 切换编辑模式
function toggleEditMode() {
  editMode.value = !editMode.value
  if (!editMode.value) {
    // 退出编辑模式时自动保存
    if (currentLayoutId.value && currentLayoutId.value !== 0) {
      autoSaveLayout()
    }
  }
}

// 重置到默认布局
function resetToDefault() {
  currentLayoutId.value = 0
  currentLayout.value = getDefaultLayout()
  editMode.value = false
}

// 添加模块
function handleAddModule(moduleId: string) {
  const moduleLayout = getModuleDefaultLayout(moduleId)
  if (moduleLayout) {
    // 找到合适的位置放置新模块
    const maxY = currentLayout.value.reduce((max, item) => Math.max(max, item.y + item.h), 0)
    const newLayout = {
      ...moduleLayout,
      y: maxY // 放在最底部
    }
    currentLayout.value.push(newLayout)
    message.success(`已添加模块`)
  }
}

// 移除模块（点击模块上的关闭按钮）
function handleRemoveModule(moduleId: string) {
  currentLayout.value = currentLayout.value.filter(item => item.i !== moduleId)
  message.success('已移除模块')
}

// 自动保存布局变更（防抖）
let saveTimer: number | null = null

function autoSaveLayout() {
  if (currentLayoutId.value && currentLayoutId.value !== 0) {
    if (saveTimer) {
      clearTimeout(saveTimer)
    }
    saveTimer = window.setTimeout(async () => {
      try {
        await updateLayout(currentLayoutId.value!, {
          layout: currentLayout.value
        })
        message.success('布局已自动保存')
      } catch (e) {
        console.error('自动保存布局失败', e)
      }
    }, 1000)
  }
}

// 保存布局
// 打开保存弹窗（预填充当前布局名称）
function openSaveModal() {
  if (isUpdatingExisting.value) {
    // 更新已有布局，显示当前名称
    const currentLayoutData = savedLayouts.value.find(l => l.id === currentLayoutId.value)
    newLayoutName.value = currentLayoutData?.name || ''
  } else {
    // 新增布局，清空名称
    newLayoutName.value = ''
  }
  saveAsDefault.value = false
  showSaveModal.value = true
}

// 保存布局（区分新增和更新）
async function saveLayout() {
  try {
    if (isUpdatingExisting.value) {
      // 更新已有布局
      await updateLayout(currentLayoutId.value!, {
        layout: currentLayout.value,
        is_default: saveAsDefault.value
      })
      message.success('布局已更新')
    } else {
      // 新增布局
      if (!newLayoutName.value.trim() || isNameDuplicate.value) {
        message.warning('请输入有效的布局名称')
        return
      }
      const newLayout = await createLayout({
        name: newLayoutName.value.trim(),
        layout: currentLayout.value,
        is_default: saveAsDefault.value
      })
      currentLayoutId.value = newLayout.id
      message.success('布局已保存')
    }

    showSaveModal.value = false
    newLayoutName.value = ''
    saveAsDefault.value = false
    await loadLayouts()
  } catch (e) {
    console.error('保存布局失败', e)
    message.error('保存布局失败')
  }
}

// 删除布局
function handleDeleteLayout() {
  if (!currentLayoutId.value || currentLayoutId.value === 0) {
    return
  }

  const layout = savedLayouts.value.find(l => l.id === currentLayoutId.value)
  const layoutName = layout?.name || '当前布局'

  dialog.warning({
    title: '确认删除',
    content: `确定要删除布局 "${layoutName}" 吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteLayout(currentLayoutId.value!)
        message.success('布局已删除')
        currentLayoutId.value = 0
        currentLayout.value = getDefaultLayout()
        await loadLayouts()
      } catch (e) {
        console.error('删除布局失败', e)
        message.error('删除布局失败')
      }
    }
  })
}

// 用户操作
function handleUserAction(key: string) {
  if (key === 'manage') {
    router.push('/strategy')
  } else if (key === 'fullscreen') {
    document.documentElement.requestFullscreen()
  }
}

// 更新容器宽度
function updateContainerWidth() {
  nextTick(() => {
    if (gridContainerRef.value) {
      containerWidth.value = gridContainerRef.value.offsetWidth
    }
  })
}

// 定时器
let dataTimer: number

onMounted(() => {
  loadLayouts()
  updateContainerWidth()
  window.addEventListener('resize', updateContainerWidth)

  // 每30秒刷新数据
  dataTimer = window.setInterval(() => {
    marketOverviewRef.value?.loadData()
    positionsRef.value?.loadData()
    sellWarningRef.value?.loadData()
    tradeRecordsRef.value?.loadData()
    selectionPoolRef.value?.loadData()
  }, 30000)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerWidth)
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
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
  padding: 8px;
  gap: 8px;
  overflow: hidden;
  color: #fff;
}

// Grid容器
.grid-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  background: rgba(10, 20, 40, 0.3);
  border-radius: 6px;

  // 编辑模式下允许滚动
  &.edit-mode {
    overflow-y: auto;
    overflow-x: hidden;

    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(100, 150, 255, 0.4);
      border-radius: 4px;

      &:hover {
        background: rgba(100, 150, 255, 0.6);
      }
    }

    &::-webkit-scrollbar-track {
      background: rgba(30, 50, 100, 0.3);
    }
  }
}

// Grid项内容
.grid-item-content {
  height: 100%;
  width: 100%;
  overflow: hidden;
  position: relative;

  &.edit-mode {
    border: 2px dashed rgba(100, 150, 255, 0.4);
    border-radius: 6px;
  }

  .remove-btn {
    position: absolute;
    top: 5px;
    right: 5px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 68, 102, 0.8);
    border-radius: 4px;
    cursor: pointer;
    z-index: 10;
    transition: background 0.2s;

    &:hover {
      background: #ff4466;
    }

    .n-icon {
      color: #fff;
    }
  }
}

// 名称重复提示
.name-error-tip {
  color: #ff4466;
  font-size: 12px;
  margin-top: 4px;
}

// grid-layout-plus 样式覆盖
:deep(.vue-grid-layout) {
  // 编辑模式下高度自适应内容，支持滚动
  min-height: 100%;
  height: auto !important;
}

:deep(.vue-grid-item) {
  touch-action: none;

  &.vue-grid-item--resizing {
    opacity: 0.9;
  }

  &.vue-grid-item--dragging {
    transition: none;
    z-index: 3;
  }
}

:deep(.vue-grid-item-content) {
  height: 100%;
  width: 100%;
  overflow: hidden;
}
</style>