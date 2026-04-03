<template>
  <div class="stock-quote-table">
    <n-data-table
      :columns="columns"
      :data="data"
      :max-height="280"
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

interface StockQuote {
  stock_code: string
  stock_name: string
  current_price: number
  change_percent: number
  change_amount: number
  volume: number
  high: number
  low: number
  update_time: string
}

const props = defineProps<{
  data: StockQuote[]
}>()

const columns: DataTableColumns<StockQuote> = [
  {
    title: '股票代码',
    key: 'stock_code',
    width: 80,
    fixed: 'left'
  },
  {
    title: '股票名称',
    key: 'stock_name',
    width: 100,
    fixed: 'left'
  },
  {
    title: '当前价',
    key: 'current_price',
    width: 80,
    render: (row) => h('span', { class: row.change_percent >= 0 ? 'price-rise' : 'price-fall' }, row.current_price?.toFixed(2))
  },
  {
    title: '涨跌幅',
    key: 'change_percent',
    width: 80,
    render: (row) => h(NTag, {
      type: row.change_percent >= 0 ? 'success' : 'error',
      size: 'small',
      bordered: false
    }, { default: () => `${row.change_percent >= 0 ? '+' : ''}${(row.change_percent * 100).toFixed(2)}%` })
  },
  {
    title: '涨跌额',
    key: 'change_amount',
    width: 80,
    render: (row) => h('span', { class: row.change_amount >= 0 ? 'price-rise' : 'price-fall' }, `${row.change_amount >= 0 ? '+' : ''}${row.change_amount?.toFixed(2)}`)
  },
  {
    title: '成交量',
    key: 'volume',
    width: 100,
    render: (row) => formatVolume(row.volume)
  },
  {
    title: '最高',
    key: 'high',
    width: 70,
    render: (row) => row.high?.toFixed(2)
  },
  {
    title: '最低',
    key: 'low',
    width: 70,
    render: (row) => row.low?.toFixed(2)
  }
]

function formatVolume(vol: number): string {
  if (!vol) return '-'
  if (vol >= 100000000) return `${(vol / 100000000).toFixed(2)}亿`
  if (vol >= 10000) return `${(vol / 10000).toFixed(2)}万`
  return vol.toString()
}

function getRowClass(row: StockQuote): string {
  return row.change_percent >= 0 ? 'row-rise' : 'row-fall'
}
</script>

<style scoped lang="scss">
.stock-quote-table {
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

    .row-rise .n-data-table-td {
      background: rgba(0, 255, 136, 0.05);
    }

    .row-fall .n-data-table-td {
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