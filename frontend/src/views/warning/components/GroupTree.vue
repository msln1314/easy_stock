<template>
  <div class="group-tree">
    <n-tree
      :data="treeData"
      :selected-keys="selectedKeys"
      :render-label="renderLabel"
      :render-suffix="renderSuffix"
      block-line
      @update:selected-keys="handleSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { NTree, NButton, NTag, NSpace, NIcon } from 'naive-ui'
import { FolderOutline, AddOutline, TrashOutline } from '@vicons/ionicons5'
import type { ConditionGroupTreeNode } from '@/api/conditionGroup'

const props = defineProps<{
  treeData: ConditionGroupTreeNode[]
  selectedKey: number | null
}>()

const emit = defineEmits<{
  select: [id: number]
  addSubgroup: [id: number]
  delete: [id: number]
}>()

const selectedKeys = computed(() => props.selectedKey ? [props.selectedKey] : [])

interface TreeOption {
  key: number
  label: string
  children?: TreeOption[]
  raw: ConditionGroupTreeNode
}

function transformData(data: ConditionGroupTreeNode[]): TreeOption[] {
  return data.map(item => ({
    key: item.id,
    label: item.group_name,
    children: item.subgroups?.length ? transformData(item.subgroups) : undefined,
    raw: item
  }))
}

const treeData = computed(() => transformData(props.treeData))

function handleSelect(keys: number[]) {
  if (keys.length > 0) {
    emit('select', keys[0])
  }
}

function renderLabel({ option }: { option: TreeOption }) {
  const raw = option.raw
  return h('div', { class: 'tree-node-label' }, [
    h(NIcon, { size: 16, style: 'margin-right: 4px' }, { default: () => h(FolderOutline) }),
    h('span', raw.group_name),
    h(NTag, {
      size: 'small',
      type: raw.logic_type === 'AND' ? 'info' : 'warning',
      style: 'margin-left: 8px'
    }, { default: () => raw.logic_type })
  ])
}

function renderSuffix({ option }: { option: TreeOption }) {
  const raw = option.raw
  return h(NSpace, { size: 4 }, {
    default: () => [
      h(NButton, {
        size: 'tiny',
        quaternary: true,
        onClick: (e: Event) => {
          e.stopPropagation()
          emit('addSubgroup', raw.id)
        }
      }, { icon: () => h(NIcon, null, { default: () => h(AddOutline) }) }),
      h(NButton, {
        size: 'tiny',
        quaternary: true,
        type: 'error',
        onClick: (e: Event) => {
          e.stopPropagation()
          emit('delete', raw.id)
        }
      }, { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) })
    ]
  })
}
</script>

<style scoped lang="scss">
.group-tree {
  :deep(.tree-node-label) {
    display: flex;
    align-items: center;
  }
}
</style>