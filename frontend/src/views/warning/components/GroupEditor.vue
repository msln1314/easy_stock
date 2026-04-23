<template>
  <div class="group-editor">
    <!-- 基本信息编辑 -->
    <div class="editor-header">
      <n-input
        v-if="isEditing"
        v-model:value="formData.group_name"
        placeholder="组合名称"
        style="width: 200px"
      />
      <h3 v-else>{{ group.group_name }}</h3>
      <n-space>
        <template v-if="!isEditing">
          <n-button type="primary" @click="startEdit">编辑</n-button>
        </template>
        <template v-else>
          <n-button type="primary" @click="handleSave" :loading="saving">保存</n-button>
          <n-button @click="cancelEdit">取消</n-button>
        </template>
      </n-space>
    </div>

    <n-form v-if="isEditing" :model="formData" label-placement="left" label-width="80" style="margin-top: 12px">
      <n-form-item label="逻辑类型">
        <n-radio-group v-model:value="formData.logic_type">
          <n-radio-button value="AND">AND（全部满足）</n-radio-button>
          <n-radio-button value="OR">OR（任一满足）</n-radio-button>
        </n-radio-group>
      </n-form-item>
      <n-form-item label="优先级">
        <n-select v-model:value="formData.priority" :options="priorityOptions" style="width: 120px" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="formData.description" type="textarea" placeholder="可选描述" />
      </n-form-item>
    </n-form>

    <!-- 显示基本信息（非编辑模式） -->
    <div v-if="!isEditing" class="info-row">
      <n-tag :type="group.logic_type === 'AND' ? 'info' : 'warning'" size="small">{{ group.logic_type }}</n-tag>
      <n-tag :type="getPriorityType(group.priority)" size="small">{{ getPriorityLabel(group.priority) }}</n-tag>
      <span class="desc-text" v-if="group.description">{{ group.description }}</span>
    </div>

    <n-divider />

    <!-- 条件列表 -->
    <div class="section">
      <div class="section-header">
        <span class="section-title">条件列表</span>
        <n-button size="small" @click="showAddCondition = true">
          <template #icon><n-icon><AddOutline /></n-icon></template>
          添加条件
        </n-button>
      </div>
      <div class="condition-list">
        <n-empty v-if="!group.conditions?.length" description="暂无条件" size="small" />
        <div v-else class="condition-items">
          <div v-for="cond in group.conditions" :key="cond.item_id" class="condition-item">
            <n-tag type="info" size="small">{{ cond.condition_name }}</n-tag>
            <n-button v-if="isEditing" size="tiny" quaternary type="error" @click="removeCondition(cond)">
              移除
            </n-button>
          </div>
        </div>
      </div>
    </div>

    <n-divider />

    <!-- 子分组列表 -->
    <div class="section">
      <div class="section-header">
        <span class="section-title">子分组</span>
        <n-button size="small" @click="showAddSubgroup = true">
          <template #icon><n-icon><AddOutline /></n-icon></template>
          添加子分组
        </n-button>
      </div>
      <div class="subgroup-list">
        <n-empty v-if="!group.subgroups?.length" description="暂无子分组" size="small" />
        <div v-else class="subgroup-items">
          <div v-for="sub in group.subgroups" :key="sub.id" class="subgroup-item">
            <div class="subgroup-header">
              <span class="subgroup-name">{{ sub.group_name }}</span>
              <n-tag :type="sub.logic_type === 'AND' ? 'info' : 'warning'" size="small">{{ sub.logic_type }}</n-tag>
              <n-space size="small">
                <n-button size="tiny" @click="editSubgroup(sub)">编辑</n-button>
                <n-button size="tiny" type="error" @click="deleteSubgroup(sub)">删除</n-button>
              </n-space>
            </div>
            <div class="subgroup-conditions">
              <n-tag v-for="cond in sub.conditions" :key="cond.item_id" size="small" style="margin: 2px">
                {{ cond.condition_name }}
              </n-tag>
              <span v-if="!sub.conditions?.length" class="no-condition">无条件</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <n-divider />

    <!-- 逻辑预览 -->
    <div class="section">
      <div class="section-header">
        <span class="section-title">逻辑预览</span>
      </div>
      <div class="logic-preview">
        <code>{{ logicPreview }}</code>
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

    <!-- 添加/编辑子分组弹窗 -->
    <n-modal v-model:show="showAddSubgroup" preset="card" :title="editingSubgroup ? '编辑子分组' : '添加子分组'" style="width: 600px">
      <n-form :model="subgroupForm" label-placement="left" label-width="80">
        <n-form-item label="名称">
          <n-input v-model:value="subgroupForm.group_name" placeholder="子分组名称" />
        </n-form-item>
        <n-form-item label="逻辑">
          <n-radio-group v-model:value="subgroupForm.logic_type">
            <n-radio-button value="AND">AND</n-radio-button>
            <n-radio-button value="OR">OR</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="条件">
          <n-select
            v-model:value="subgroupForm.condition_ids"
            :options="conditionOptions"
            multiple
            filterable
            placeholder="选择条件"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="cancelSubgroup">取消</n-button>
          <n-button type="primary" @click="handleSaveSubgroup" :loading="savingSubgroup">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  NForm, NFormItem, NInput, NRadioGroup, NRadioButton, NSelect, NTag, NButton,
  NSpace, NDivider, NEmpty, NModal, NIcon, useMessage
} from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import {
  updateConditionGroup,
  addConditionItem,
  removeConditionItem,
  createSubgroup,
  deleteConditionGroup,
  type ConditionGroupTreeNode,
  type ConditionItem
} from '@/api/conditionGroup'
import { fetchWarningConditions, type WarningCondition } from '@/api/warning'

const props = defineProps<{
  group: ConditionGroupTreeNode
}>()

const emit = defineEmits<{
  refresh: []
}>()

const message = useMessage()

const isEditing = ref(false)
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

const showAddSubgroup = ref(false)
const editingSubgroup = ref<ConditionGroupTreeNode | null>(null)
const savingSubgroup = ref(false)
const subgroupForm = ref({
  group_name: '',
  logic_type: 'OR' as 'AND' | 'OR',
  condition_ids: [] as number[]
})

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

// 逻辑预览
const logicPreview = computed(() => {
  const parts: string[] = []

  // 添加条件
  if (props.group.conditions?.length) {
    const condNames = props.group.conditions.map(c => c.condition_name)
    parts.push(condNames.join(` ${props.group.logic_type} `))
  }

  // 添加子分组
  if (props.group.subgroups?.length) {
    for (const sub of props.group.subgroups) {
      if (sub.conditions?.length) {
        const subConds = sub.conditions.map(c => c.condition_name).join(` ${sub.logic_type} `)
        parts.push(`(${subConds})`)
      }
    }
  }

  if (parts.length === 0) return '无条件'
  return parts.join(` ${props.group.logic_type} `)
})

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

function startEdit() {
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  formData.value = {
    group_name: props.group.group_name,
    logic_type: props.group.logic_type,
    priority: props.group.priority,
    description: props.group.description || ''
  }
}

async function handleSave() {
  saving.value = true
  try {
    await updateConditionGroup(props.group.id, formData.value)
    message.success('保存成功')
    isEditing.value = false
    emit('refresh')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleAddCondition() {
  if (!selectedConditionId.value) return

  try {
    await addConditionItem(props.group.id, selectedConditionId.value)
    message.success('添加成功')
    showAddCondition.value = false
    selectedConditionId.value = null
    emit('refresh')
  } catch (error) {
    message.error('添加失败')
  }
}

async function removeCondition(cond: ConditionItem) {
  if (!cond.item_id) return

  try {
    await removeConditionItem(props.group.id, cond.item_id)
    message.success('移除成功')
    emit('refresh')
  } catch (error) {
    message.error('移除失败')
  }
}

function editSubgroup(sub: ConditionGroupTreeNode) {
  editingSubgroup.value = sub
  subgroupForm.value = {
    group_name: sub.group_name,
    logic_type: sub.logic_type,
    condition_ids: sub.conditions?.map(c => c.condition_id) || []
  }
  showAddSubgroup.value = true
}

function cancelSubgroup() {
  showAddSubgroup.value = false
  editingSubgroup.value = null
  subgroupForm.value = { group_name: '', logic_type: 'OR', condition_ids: [] }
}

async function handleSaveSubgroup() {
  if (!subgroupForm.value.group_name) {
    message.warning('请输入名称')
    return
  }

  savingSubgroup.value = true
  try {
    if (editingSubgroup.value) {
      // 更新子分组
      await updateConditionGroup(editingSubgroup.value.id, {
        group_name: subgroupForm.value.group_name,
        logic_type: subgroupForm.value.logic_type
      })
      message.success('更新成功')
    } else {
      // 创建子分组
      await createSubgroup(props.group.id, {
        group_name: subgroupForm.value.group_name,
        logic_type: subgroupForm.value.logic_type,
        condition_ids: subgroupForm.value.condition_ids
      })
      message.success('创建成功')
    }
    showAddSubgroup.value = false
    editingSubgroup.value = null
    subgroupForm.value = { group_name: '', logic_type: 'OR', condition_ids: [] }
    emit('refresh')
  } catch (error) {
    message.error('操作失败')
  } finally {
    savingSubgroup.value = false
  }
}

async function deleteSubgroup(sub: ConditionGroupTreeNode) {
  try {
    await deleteConditionGroup(sub.id)
    message.success('删除成功')
    emit('refresh')
  } catch (error) {
    message.error('删除失败')
  }
}

onMounted(() => {
  loadConditions()
})
</script>

<style scoped lang="scss">
.group-editor {
  padding: 4px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;

  .desc-text {
    color: #666;
    font-size: 13px;
  }
}

.section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .section-title {
    font-weight: 500;
    font-size: 14px;
  }
}

.condition-list {
  min-height: 40px;
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

.subgroup-item {
  padding: 12px;
  border: 1px solid #e0e0e6;
  border-radius: 8px;
  background: #fafafa;
}

.subgroup-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.subgroup-name {
  font-weight: 500;
  flex: 1;
}

.subgroup-conditions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.no-condition {
  color: #999;
  font-size: 12px;
}

.logic-preview {
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 6px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-all;
}
</style>