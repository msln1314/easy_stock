<template>
  <div class="group-tree">
    <div class="tree-header">
      <span>组合条件列表</span>
      <n-button size="small" type="primary" @click="emit('create')">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建
      </n-button>
    </div>

    <n-divider style="margin: 8px 0" />

    <n-spin :show="loading">
      <div v-if="!treeData.length" class="empty-tip">
        <n-empty description="暂无组合条件" size="small" />
      </div>
      <div v-else class="group-list">
        <div
          v-for="item in treeData"
          :key="item.id"
          :class="['group-item', { active: selectedKey === item.id }]"
          @click="emit('select', item.id)"
        >
          <div class="item-main">
            <n-icon size="18"><FolderOutline /></n-icon>
            <span class="item-name">{{ item.group_name }}</span>
            <n-tag :type="item.logic_type === 'AND' ? 'info' : 'warning'" size="small">
              {{ item.logic_type }}
            </n-tag>
          </div>
          <div class="item-info">
            <span class="info-text">{{ item.conditions?.length || 0 }} 条件</span>
            <span class="info-text" v-if="item.subgroups?.length">{{ item.subgroups.length }} 子组</span>
          </div>
          <div class="item-actions" @click.stop>
            <n-button size="tiny" quaternary type="error" @click="emit('delete', item.id)">
              <template #icon><n-icon><TrashOutline /></n-icon></template>
            </n-button>
          </div>
        </div>
      </div>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { NButton, NIcon, NTag, NSpin, NEmpty, NDivider } from 'naive-ui'
import { AddOutline, FolderOutline, TrashOutline } from '@vicons/ionicons5'
import type { ConditionGroupTreeNode } from '@/api/conditionGroup'

defineProps<{
  treeData: ConditionGroupTreeNode[]
  selectedKey: number | null
  loading?: boolean
}>()

const emit = defineEmits<{
  select: [id: number]
  create: []
  delete: [id: number]
}>()
</script>

<style scoped lang="scss">
.group-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.empty-tip {
  padding: 20px 0;
}

.group-list {
  flex: 1;
  overflow-y: auto;
}

.group-item {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s;
  border: 1px solid transparent;

  &:hover {
    background: var(--n-color-hover);
  }

  &.active {
    background: var(--n-color-hover);
    border-color: var(--n-border-color);
  }
}

.item-main {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.item-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.item-info {
  display: flex;
  gap: 12px;
  margin-left: 26px;

  .info-text {
    font-size: 12px;
    color: #999;
  }
}

.item-actions {
  display: none;
  margin-left: auto;
}

.group-item:hover .item-actions {
  display: flex;
}
</style>