<template>
  <div class="group-editor">
    <div class="editor-header">
      <h3>{{ group.group_name }}</h3>
      <n-space>
        <n-button v-if="mode === 'view'" type="primary" @click="mode = 'edit'">编辑</n-button>
        <n-button v-if="mode === 'edit'" type="primary" @click="handleSave" :loading="saving">保存</n-button>
        <n-button v-if="mode === 'edit'" @click="handleCancel">取消</n-button>
      </n-space>
    </div>

    <n-divider />

    <!-- 基本信息 -->
    <n-form :model="formData" label-placement="left" label-width="80">
      <n-form-item label="组合名称">
        <n-input v-if="mode === 'edit'" v-model:value="formData.group_name" />
        <span v-else>{{ group.group_name }}</span>
      </n-form-item>
      <n-form-item label="逻辑类型">
        <n-radio-group v-if="mode === 'edit'" v-model:value="formData.logic_type">
          <n-radio-button value="AND">AND（全部满足）</n-radio-button>
          <n-radio-button value="OR">OR（任一满足）</n-radio-button>
        </n-radio-group>
        <n-tag v-else :type="group.logic_type === 'AND' ? 'info' : 'warning'">
          {{ group.logic_type }}
        </n-tag>
      </n-form-item>
      <n-form-item label="优先级">
        <n-select v-if="mode === 'edit'" v-model:value="formData.priority" :options="priorityOptions" />
        <n-tag v-else :type="getPriorityType(group.priority)">{{ getPriorityLabel(group.priority) }}</n-tag>
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-if="mode === 'edit'" v-model:value="formData.description" type="textarea" />
        <span v-else>{{ group.description || '--' }}</span>
      </n-form-item>
    </n-form>

    <n-divider />

    <!-- 条件列表 -->
    <div class="section-title">
      <span>条件列表</span>
      <n-button v-if="mode === 'edit'" size="small" @click="showAddCondition = true">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        添加条件
      </n-button>
    </div>

    <div class="condition-list">
      <n-empty v-if="!group.conditions?.length" description="暂无条件" />
      <div v-else class="condition-items">
        <div v-for="cond in group.conditions" :key="cond.condition_id" class="condition-item">
          <n-tag type="info">{{ cond.condition_name }}</n-tag>
          <n-button v-if="mode === 'edit'" size="tiny" quaternary type="error" @click="handleRemoveCondition(cond)">
            移除
          </n-button>
        </div>
      </div>
    </div>

    <!-- 子分组 -->
    <n-divider />

    <div class="section-title">
      <span>子分组</span>
    </div>

    <div class="subgroup-list">
      <n-empty v-if="!group.subgroups?.length" description="暂无子分组" />
      <div v-else class="subgroup-items">
        <n-card v-for="sub in group.subgroups" :key="sub.id" size="small" :title="sub.group_name">
          <template #header-extra>
            <n-tag :type="sub.logic_type === 'AND' ? 'info' : 'warning'" size="small">
              {{ sub.logic_type }}
            </n-tag>
          </template>
          <div class="subgroup-conditions">
            <n-tag v-for="cond in sub.conditions" :key="cond.condition_id" size="small" style="margin: 2px">
              {{ cond.condition_name }}
            </n-tag>
          </div>
        </n-card>
      </div>
    </div>

    <!-- 添加条件弹窗 -->
    <n-modal v-model:show="showAddCondition" preset="card" title="添加条件" style="width: 500px">
      <n-select
        v-model:value="selectedConditionId"
        :options="conditionOptions"
        filterable
        placeholder="选择预警条件"
      />
      <template #footer>
        <n-space justify="end">
          <n-button @click="showAddCondition = false">取消</n-button>
          <n-button type="primary" @click="handleAddCondition" :disabled="!selectedConditionId">添加</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { NForm, NFormItem, NInput, NRadioGroup, NRadioButton, NSelect, NTag, NButton, NSpace, NDivider, NEmpty, NCard, NModal, NIcon, useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import {
  updateConditionGroup,
  addConditionItem,
  removeConditionItem,
  type ConditionGroupTreeNode,
  type ConditionItem
} from '@/api/conditionGroup'
import { fetchWarningConditions, type WarningCondition } from '@/api/warning'

const props = defineProps<{
  group: ConditionGroupTreeNode
  mode: 'view' | 'edit'
}>()

const emit = defineEmits<{
  save: []
  cancel: []
}>()

const message = useMessage()

const mode = ref(props.mode)
const saving = ref(false)
const formData = ref({
  group_name: '',
  logic_type: 'AND' as 'AND' | 'OR',
  priority: 'warning',
  description: ''
})

const showAddCondition = ref(false)
const selectedConditionId = ref<number | null>(null)
const allConditions = ref<WarningCondition[]>([])

const priorityOptions = [
  { label: '严重', value: 'critical' },
  { label: '警告', value: 'warning' },
  { label: '提示', value: 'info' }
]

const conditionOptions = computed(() =>
  allConditions.value.map(c => ({
    label: c.condition_name,
    value: c.id
  }))
)

function getPriorityType(priority: string): 'error' | 'warning' | 'info' {
  if (priority === 'critical') return 'error'
  if (priority === 'warning') return 'warning'
  return 'info'
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = { critical: '严重', warning: '警告', info: '提示' }
  return labels[priority] || priority
}

watch(() => props.group, (val) => {
  formData.value = {
    group_name: val.group_name,
    logic_type: val.logic_type,
    priority: val.priority,
    description: val.description || ''
  }
}, { immediate: true })

async function loadConditions() {
  try {
    allConditions.value = await fetchWarningConditions()
  } catch (error) {
    console.error('加载条件失败', error)
  }
}

async function handleSave() {
  saving.value = true
  try {
    await updateConditionGroup(props.group.id, formData.value)
    message.success('保存成功')
    mode.value = 'view'
    emit('save')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleCancel() {
  mode.value = 'view'
  emit('cancel')
}

async function handleAddCondition() {
  if (!selectedConditionId.value) return

  try {
    await addConditionItem(props.group.id, selectedConditionId.value)
    message.success('添加成功')
    showAddCondition.value = false
    selectedConditionId.value = null
    emit('save')
  } catch (error) {
    message.error('添加失败')
  }
}

async function handleRemoveCondition(cond: ConditionItem) {
  if (!cond.item_id) return

  try {
    await removeConditionItem(props.group.id, cond.item_id)
    message.success('移除成功')
    emit('save')
  } catch (error) {
    message.error('移除失败')
  }
}

loadConditions()
</script>

<style scoped lang="scss">
.group-editor {
  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
    }
  }

  .section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-weight: 500;
  }

  .condition-list {
    min-height: 60px;
  }

  .condition-items {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .condition-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .subgroup-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .subgroup-conditions {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
}
</style>