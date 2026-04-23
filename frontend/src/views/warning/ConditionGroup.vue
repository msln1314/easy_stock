<template>
  <div class="condition-group-page">
    <div class="page-header">
      <h2>组合条件管理</h2>
    </div>

    <div class="main-content">
      <div class="tree-panel">
        <GroupTree
          :tree-data="groupTree"
          :selected-key="selectedGroupId"
          :loading="loading"
          @select="handleSelect"
          @create="handleCreateRoot"
          @delete="handleDelete"
        />
      </div>

      <div class="editor-panel">
        <GroupEditor
          v-if="selectedGroup"
          :group="selectedGroup"
          @refresh="loadTree"
        />
        <n-empty v-else description="请选择组合条件" />
      </div>
    </div>

    <!-- 创建弹窗 -->
    <n-modal v-model:show="showCreateModal" preset="card" title="新建组合条件" style="width: 500px">
      <n-form ref="createFormRef" :model="createForm" label-placement="left" label-width="80">
        <n-form-item label="组合名称" path="group_name">
          <n-input v-model:value="createForm.group_name" placeholder="请输入组合名称" />
        </n-form-item>
        <n-form-item label="逻辑类型" path="logic_type">
          <n-radio-group v-model:value="createForm.logic_type">
            <n-radio-button value="AND">AND（全部满足）</n-radio-button>
            <n-radio-button value="OR">OR（任一满足）</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="优先级" path="priority">
          <n-select v-model:value="createForm.priority" :options="priorityOptions" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="createForm.description" type="textarea" placeholder="可选描述" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" @click="handleCreateSubmit" :loading="creating">创建</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NModal, NForm, NFormItem, NInput, NRadioGroup, NRadioButton, NSelect, NSpace, NButton, NEmpty, useMessage } from 'naive-ui'
import GroupTree from './components/GroupTree.vue'
import GroupEditor from './components/GroupEditor.vue'
import {
  fetchConditionGroupTree,
  fetchConditionGroup,
  createConditionGroup,
  deleteConditionGroup,
  type ConditionGroupTreeNode
} from '@/api/conditionGroup'

const message = useMessage()

const loading = ref(false)
const groupTree = ref<ConditionGroupTreeNode[]>([])
const selectedGroupId = ref<number | null>(null)
const selectedGroup = ref<ConditionGroupTreeNode | null>(null)

const showCreateModal = ref(false)
const creating = ref(false)
const createForm = ref({
  group_name: '',
  logic_type: 'AND' as 'AND' | 'OR',
  priority: 'warning',
  description: ''
})

const priorityOptions = [
  { label: '严重', value: 'critical' },
  { label: '警告', value: 'warning' },
  { label: '提示', value: 'info' }
]

async function loadTree() {
  loading.value = true
  try {
    groupTree.value = await fetchConditionGroupTree()
    // 重新加载当前选中的分组
    if (selectedGroupId.value) {
      const stillExists = groupTree.value.some(g => g.id === selectedGroupId.value) ||
        groupTree.value.some(g => g.subgroups?.some(s => s.id === selectedGroupId.value))
      if (stillExists) {
        selectedGroup.value = await fetchConditionGroup(selectedGroupId.value)
      } else {
        selectedGroupId.value = null
        selectedGroup.value = null
      }
    }
  } catch (error) {
    message.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function handleSelect(id: number) {
  selectedGroupId.value = id
  try {
    selectedGroup.value = await fetchConditionGroup(id)
  } catch (error) {
    message.error('加载详情失败')
  }
}

function handleCreateRoot() {
  createForm.value = { group_name: '', logic_type: 'AND', priority: 'warning', description: '' }
  showCreateModal.value = true
}

async function handleCreateSubmit() {
  if (!createForm.value.group_name) {
    message.warning('请输入组合名称')
    return
  }

  creating.value = true
  try {
    await createConditionGroup(createForm.value)
    message.success('创建成功')
    showCreateModal.value = false
    loadTree()
  } catch (error) {
    message.error('创建失败')
  } finally {
    creating.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteConditionGroup(id)
    message.success('删除成功')
    if (selectedGroupId.value === id) {
      selectedGroupId.value = null
      selectedGroup.value = null
    }
    loadTree()
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  loadTree()
})
</script>

<style scoped lang="scss">
.condition-group-page {
  padding: 16px;
  height: calc(100vh - 50px - 32px);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 16px;

  h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.main-content {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.tree-panel {
  width: 320px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
}

.editor-panel {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
}
</style>