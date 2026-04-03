<template>
  <n-modal v-model:show="visible" preset="card" :title="indicator?.indicator_name" style="width: 700px">
    <template v-if="indicator">
      <n-descriptions label-placement="left" :column="2">
        <n-descriptions-item label="指标KEY">
          <n-tag type="primary">{{ indicator.indicator_key }}</n-tag>
        </n-descriptions-item>
        <n-descriptions-item label="分类">
          {{ indicator.category_name }}
        </n-descriptions-item>
        <n-descriptions-item label="值类型">
          {{ getValueTypeLabel(indicator.value_type) }}
        </n-descriptions-item>
        <n-descriptions-item label="状态">
          <n-switch
            :value="indicator.is_enabled"
            @update:value="handleToggle"
          />
        </n-descriptions-item>
      </n-descriptions>

      <n-divider>指标说明</n-divider>
      <p class="detail-desc">{{ indicator.description }}</p>

      <n-divider>参数配置</n-divider>
      <n-data-table
        :columns="paramsColumns"
        :data="indicator.params || []"
        size="small"
        v-if="indicator.params?.length"
      />
      <n-empty v-else description="无参数" size="small" />

      <n-divider>输出字段</n-divider>
      <n-data-table
        :columns="outputColumns"
        :data="indicator.output_fields || []"
        size="small"
        v-if="indicator.output_fields?.length"
      />
      <n-empty v-else description="无输出定义" size="small" />

      <template v-if="indicator.usage_guide">
        <n-divider>使用说明</n-divider>
        <p class="usage-guide">{{ indicator.usage_guide }}</p>
      </template>

      <template v-if="indicator.signal_interpretation">
        <n-divider>信号解读</n-divider>
        <div class="signal-list">
          <div
            class="signal-item"
            v-for="(desc, key) in indicator.signal_interpretation"
            :key="key"
          >
            <n-tag size="small">{{ key }}</n-tag>
            <span>{{ desc }}</span>
          </div>
        </div>
      </template>
    </template>

    <template #footer>
      <div class="modal-footer">
        <n-button
          v-if="!indicator?.is_builtin"
          type="error"
          @click="handleDelete"
        >
          删除
        </n-button>
        <n-button @click="handleClose">关闭</n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import {
  NModal, NDescriptions, NDescriptionsItem, NDivider, NDataTable,
  NEmpty, NSwitch, NTag, NButton, useMessage
} from 'naive-ui'
import request from '@/utils/request'

const props = defineProps<{
  show: boolean
  indicator: any
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  updated: []
}>()

const message = useMessage()

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

// 参数表格列
const paramsColumns = [
  { title: '参数KEY', key: 'key' },
  { title: '参数名', key: 'name' },
  { title: '类型', key: 'type' },
  { title: '默认值', key: 'default' },
  { title: '范围', key: 'range', render: (row: any) => row.min && row.max ? `${row.min} ~ ${row.max}` : '-' }
]

// 输出字段表格列
const outputColumns = [
  { title: '字段KEY', key: 'key' },
  { title: '字段名', key: 'name' },
  { title: '类型', key: 'type' },
  { title: '说明', key: 'desc' }
]

function getValueTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    single: '单值',
    multi: '多值',
    series: '序列'
  }
  return labels[type] || type
}

async function handleToggle(enabled: boolean) {
  if (!props.indicator) return

  try {
    await request.put(`/indicators/${props.indicator.id}`, {
      is_enabled: enabled
    })
    props.indicator.is_enabled = enabled
    message.success(enabled ? '已启用' : '已禁用')
    emit('updated')
  } catch (error) {
    message.error('操作失败')
  }
}

async function handleDelete() {
  if (!props.indicator) return

  try {
    await request.delete(`/indicators/${props.indicator.id}`)
    message.success('删除成功')
    handleClose()
    emit('updated')
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '删除失败')
  }
}

function handleClose() {
  emit('update:show', false)
}
</script>

<script lang="ts">
import { computed } from 'vue'
</script>

<style scoped lang="scss">
.detail-desc,
.usage-guide {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  line-height: 1.6;
}

.signal-list {
  .signal-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(100, 150, 255, 0.1);

    &:last-child {
      border-bottom: none;
    }

    span {
      color: rgba(255, 255, 255, 0.8);
      font-size: 13px;
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>