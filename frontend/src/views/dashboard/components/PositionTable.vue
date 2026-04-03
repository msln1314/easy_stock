<template>
  <div class="position-table">
    <n-data-table
      :columns="columns"
      :data="data"
      :max-height="180"
      :row-class-name="getRowClass"
      striped
      size="small"
    />
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { NDataTable, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

interface Position {
  stock_code: string
  stock_name: string
  position_size: number
  cost_price: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_percent: number
}

const props = defineProps<{
  data: Position[]
}>()

const columns: DataTableColumns<Position> = [
  {
    title: '股票代码',
    key: 'stock_code',
    width: 100
  },
  {
    title: '股票名称',
    key: 'stock_name',
    width: 120
  },
  {
    title: '持仓数量',
    key: 'position_size',
    width: 100,
    render: (row) => `${row.position_size}股`
  },
  {
    title: '成本价',
    key: 'cost_price',
    width: 100,
    render: (row) => row.cost_price?.toFixed(2)
  },
  {
    title: '现价',
    key: 'current_price',
    width: 100,
    render: (row) => h('span', { class: row.profit_percent >= 0 ? 'price-rise' : 'price-fall' }, row.current_price?.toFixed(2))
  },
  {
    title: '市值',
    key: 'market_value',
    width: 120,
    render: (row) => `¥${row.market_value?.toLocaleString()}`
  },
  {
    title: '盈亏',
    key: 'profit_loss',
    width: 100,
    render: (row) => h('span', { class: row.profit_loss >= 0 ? 'price-rise' : 'price-fall' }, `${row.profit_loss >= 0 ? '+' : ''}¥${row.profit_loss?.toFixed(2)}`)
  },
  {
    title: '盈亏比例',
    key: 'profit_percent',
    width: 100,
    render: (row) => h(NTag, {
      type: row.profit_percent >= 0 ? 'success' : 'error',
      size: 'small',
      bordered: false
    }, { default: () => `${row.profit_percent >= 0 ? '+' : ''}${(row.profit_percent * 100).toFixed(2)}%` })
  }
]

function getRowClass(row: Position): string {
  return row.profit_percent >= 0 ? 'row-profit' : 'row-loss'
}
</script>

<style scoped lang="scss">
.position-table {
  height: 100%;

  :deep(.n-data-table) {
    background: transparent;

    .n-data-table-th {
      background: rgba(0, 100, 200, 0.3);
      color: #00aaff;
    }

    .n-data-table-td {
      background: transparent;
      color: #fff;
    }

    .row-profit .n-data-table-td {
      background: rgba(0, 255, 136, 0.05);
    }

    .row-loss .n-data-table-td {
      background: rgba(255, 68, 102, 0.05);
    }
  }

  .price-rise {
    color: #00ff88;
  }

  .price-fall {
    color: #ff4466;
  }
}
</style>