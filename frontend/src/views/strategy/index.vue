<template>
  <div class="strategy-page flex gap-4 h-full">
    <!-- 左侧筛选导航 -->
    <div class="filter-panel w-200px">
      <StrategyFilter />
    </div>

    <!-- 右侧策略列表 -->
    <div class="strategy-content flex-1 flex flex-col">
      <!-- 操作栏 -->
      <div class="action-bar mb-4 flex-between">
        <n-button type="primary" @click="showWizard = true">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          新增策略
        </n-button>
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索策略名称..."
          clearable
          @update:value="handleSearch"
        >
          <template #prefix>
            <n-icon><SearchOutline /></n-icon>
          </template>
        </n-input>
      </div>

      <!-- 策略列表 -->
      <div class="strategy-list flex-1 overflow-auto">
        <n-spin :show="store.loading">
          <div v-if="store.strategies.length === 0" class="empty-state flex-center py-20">
            <n-empty description="暂无策略数据">
              <template #extra>
                <n-button size="small" @click="showWizard = true">创建第一个策略</n-button>
              </template>
            </n-empty>
          </div>
          <div v-else class="grid gap-4">
            <StrategyCard
              v-for="strategy in store.strategies"
              :key="strategy.id"
              :strategy="strategy"
              @edit="handleEdit"
              @delete="handleDelete"
              @toggle-status="handleToggleStatus"
            />
          </div>
        </n-spin>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar mt-4 flex-center">
        <n-pagination
          v-model:page="store.page"
          :page-count="Math.ceil(store.total / store.pageSize)"
          @update:page="store.setPage"
        />
      </div>
    </div>

    <!-- 新增/编辑向导 -->
    <StrategyWizard v-model:show="showWizard" @success="handleWizardSuccess" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NIcon, NInput, NSpin, NEmpty, NPagination, useMessage, useDialog } from 'naive-ui'
import { AddOutline, SearchOutline } from '@vicons/ionicons5'
import StrategyFilter from './components/StrategyFilter.vue'
import StrategyCard from './components/StrategyCard.vue'
import StrategyWizard from './components/StrategyWizard.vue'
import { useStrategyStore } from '@/stores/strategy'

const store = useStrategyStore()
const message = useMessage()
const dialog = useDialog()

const showWizard = ref(false)
const searchKeyword = ref('')

onMounted(() => {
  store.init()
})

function handleSearch(value: string) {
  store.setFilters({ keyword: value })
}

function handleEdit(id: number) {
  // TODO: 打开编辑向导
  message.info(`编辑策略: ${id}`)
}

function handleDelete(id: number) {
  dialog.warning({
    title: '确认删除',
    content: '删除后将无法恢复，确定要删除该策略吗？',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      await store.removeStrategy(id)
      message.success('删除成功')
    }
  })
}

function handleToggleStatus(id: number, currentStatus: string) {
  const newStatus = currentStatus === 'running' ? 'paused' : 'running'
  store.changeStatus(id, newStatus)
  message.success(`状态已更新为: ${newStatus === 'running' ? '运行中' : '已暂停'}`)
}

function handleWizardSuccess() {
  showWizard.value = false
  store.init()
  message.success('策略创建成功')
}
</script>

<style scoped lang="scss">
.strategy-page {
  height: calc(100vh - 50px - 32px);
}

.filter-panel {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.strategy-content {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.action-bar {
  .n-input {
    width: 200px;
  }
}

.strategy-list {
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}
</style>