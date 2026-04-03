<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  NTabs, NTabPane, NRadioGroup, NRadio, NInput, NInputNumber,
  NCheckboxGroup, NCheckbox, NButton, NCard, NDescriptions, NDescriptionsItem,
  NSpace, NTag, useMessage
} from 'naive-ui'
import dayjs from 'dayjs'

const message = useMessage()

// 当前选中的 tab
const activeTab = ref('seconds')

// 表达式字段
const fields = ref({
  seconds: '*',
  minutes: '*',
  hour: '*',
  day: '*',
  month: '*',
  week: '?',
  year: ''
})

// 秒配置
const secondsMode = ref('0')
const secondsCycleStart = ref<number | null>(null)
const secondsCycleEnd = ref<number | null>(null)
const secondsStepStart = ref<number | null>(null)
const secondsStepValue = ref<number | null>(null)
const secondsSpecific = ref<string[]>([])

// 分配置
const minutesMode = ref('0')
const minutesCycleStart = ref<number | null>(null)
const minutesCycleEnd = ref<number | null>(null)
const minutesStepStart = ref<number | null>(null)
const minutesStepValue = ref<number | null>(null)
const minutesSpecific = ref<string[]>([])

// 时配置
const hourMode = ref('0')
const hourCycleStart = ref<number | null>(null)
const hourCycleEnd = ref<number | null>(null)
const hourStepStart = ref<number | null>(null)
const hourStepValue = ref<number | null>(null)
const hourSpecific = ref<string[]>([])

// 日配置
const dayMode = ref('0')
const dayCycleStart = ref<number | null>(null)
const dayCycleEnd = ref<number | null>(null)
const dayStepStart = ref<number | null>(null)
const dayStepValue = ref<number | null>(null)
const dayWorkday = ref<number | null>(null)
const daySpecific = ref<string[]>([])

// 月配置
const monthMode = ref('0')
const monthCycleStart = ref<number | null>(null)
const monthCycleEnd = ref<number | null>(null)
const monthStepStart = ref<number | null>(null)
const monthStepValue = ref<number | null>(null)
const monthSpecific = ref<string[]>([])

// 周配置
const weekMode = ref('1')
const weekCycleStart = ref<number | null>(null)
const weekCycleEnd = ref<number | null>(null)
const weekNthWeek = ref<number | null>(null)
const weekNthDay = ref<number | null>(null)
const weekLast = ref<number | null>(null)
const weekSpecific = ref<string[]>([])

// 年配置
const yearMode = ref('0')
const yearCycleStart = ref<number | null>(null)
const yearCycleEnd = ref<number | null>(null)

// 星期列表
const weekLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 生成的 Cron 表达式
const cronExpression = computed(() => {
  const parts = [
    fields.value.seconds,
    fields.value.minutes,
    fields.value.hour,
    fields.value.day,
    fields.value.month,
    fields.value.week
  ]
  if (fields.value.year) {
    parts.push(fields.value.year)
  }
  return parts.join(' ')
})

// 中文描述
const cronDescription = computed(() => {
  const expr = cronExpression.value
  const parts = expr.split(' ')
  const desc: string[] = []

  if (parts[0] !== '*') {
    if (parts[0].includes('/')) desc.push(`每${parts[0].split('/')[1]}秒`)
    else if (parts[0].includes('-')) desc.push(`${parts[0].replace('-', '到')}秒`)
    else desc.push(`第${parts[0]}秒`)
  }
  if (parts[1] !== '*') {
    if (parts[1].includes('/')) desc.push(`每${parts[1].split('/')[1]}分钟`)
    else if (parts[1].includes('-')) desc.push(`${parts[1].replace('-', '到')}分`)
    else desc.push(`${parts[1]}分`)
  }
  if (parts[2] !== '*') {
    if (parts[2].includes('/')) desc.push(`每${parts[2].split('/')[1]}小时`)
    else if (parts[2].includes('-')) desc.push(`${parts[2].replace('-', '到')}时`)
    else desc.push(`${parts[2]}时`)
  }
  if (parts[3] !== '*' && parts[3] !== '?') {
    if (parts[3] === 'L') desc.push('每月最后一天')
    else if (parts[3].includes('W')) desc.push(`最近工作日${parts[3].replace('W', '')}号`)
    else desc.push(`${parts[3]}日`)
  }
  if (parts[4] !== '*') desc.push(`${parts[4]}月`)
  if (parts[5] !== '?' && parts[5] !== '*') {
    if (parts[5].includes('#')) {
      const [day, nth] = parts[5].split('#')
      desc.push(`第${nth}周${weekLabels[parseInt(day)]}`)
    } else if (parts[5].includes('L')) {
      desc.push(`最后一个${weekLabels[parseInt(parts[5].replace('L', ''))]}`)
    } else if (parts[5].includes('-')) {
      const [start, end] = parts[5].split('-')
      desc.push(`${weekLabels[parseInt(start)]}到${weekLabels[parseInt(end)]}`)
    } else {
      const days = parts[5].split(',').map(d => weekLabels[parseInt(d)]).join('、')
      desc.push(days)
    }
  }
  return desc.length === 0 ? '每秒执行' : desc.join(' ') + '执行'
})

// 秒改变
const handleSecondsChange = () => {
  switch (secondsMode.value) {
    case '0': fields.value.seconds = '*'; break
    case '1':
      if (secondsCycleStart.value !== null && secondsCycleEnd.value !== null)
        fields.value.seconds = `${secondsCycleStart.value}-${secondsCycleEnd.value}`
      break
    case '2':
      if (secondsStepStart.value !== null && secondsStepValue.value !== null)
        fields.value.seconds = `${secondsStepStart.value}/${secondsStepValue.value}`
      break
    case '3':
      if (secondsSpecific.value.length > 0) fields.value.seconds = secondsSpecific.value.join(',')
      break
  }
}

// 分改变
const handleMinutesChange = () => {
  switch (minutesMode.value) {
    case '0': fields.value.minutes = '*'; break
    case '1':
      if (minutesCycleStart.value !== null && minutesCycleEnd.value !== null)
        fields.value.minutes = `${minutesCycleStart.value}-${minutesCycleEnd.value}`
      break
    case '2':
      if (minutesStepStart.value !== null && minutesStepValue.value !== null)
        fields.value.minutes = `${minutesStepStart.value}/${minutesStepValue.value}`
      break
    case '3':
      if (minutesSpecific.value.length > 0) fields.value.minutes = minutesSpecific.value.join(',')
      break
  }
}

// 时改变
const handleHourChange = () => {
  switch (hourMode.value) {
    case '0': fields.value.hour = '*'; break
    case '1':
      if (hourCycleStart.value !== null && hourCycleEnd.value !== null)
        fields.value.hour = `${hourCycleStart.value}-${hourCycleEnd.value}`
      break
    case '2':
      if (hourStepStart.value !== null && hourStepValue.value !== null)
        fields.value.hour = `${hourStepStart.value}/${hourStepValue.value}`
      break
    case '3':
      if (hourSpecific.value.length > 0) fields.value.hour = hourSpecific.value.join(',')
      break
  }
}

// 日改变
const handleDayChange = () => {
  switch (dayMode.value) {
    case '0': fields.value.day = '*'; fields.value.week = '?'; break
    case '1': fields.value.day = '?'; break
    case '2': fields.value.day = 'L'; fields.value.week = '?'; break
    case '3':
      if (dayCycleStart.value !== null && dayCycleEnd.value !== null) {
        fields.value.day = `${dayCycleStart.value}-${dayCycleEnd.value}`; fields.value.week = '?'
      }
      break
    case '4':
      if (dayStepStart.value !== null && dayStepValue.value !== null) {
        fields.value.day = `${dayStepStart.value}/${dayStepValue.value}`; fields.value.week = '?'
      }
      break
    case '5':
      if (dayWorkday.value !== null) { fields.value.day = `${dayWorkday.value}W`; fields.value.week = '?' }
      break
    case '6':
      if (daySpecific.value.length > 0) { fields.value.day = daySpecific.value.join(','); fields.value.week = '?' }
      break
  }
}

// 月改变
const handleMonthChange = () => {
  switch (monthMode.value) {
    case '0': fields.value.month = '*'; break
    case '1':
      if (monthCycleStart.value !== null && monthCycleEnd.value !== null)
        fields.value.month = `${monthCycleStart.value}-${monthCycleEnd.value}`
      break
    case '2':
      if (monthStepStart.value !== null && monthStepValue.value !== null)
        fields.value.month = `${monthStepStart.value}/${monthStepValue.value}`
      break
    case '3':
      if (monthSpecific.value.length > 0) fields.value.month = monthSpecific.value.join(',')
      break
  }
}

// 周改变
const handleWeekChange = () => {
  switch (weekMode.value) {
    case '1': fields.value.week = '?'; break
    case '2':
      if (weekCycleStart.value !== null && weekCycleEnd.value !== null) {
        fields.value.week = `${weekCycleStart.value}-${weekCycleEnd.value}`; fields.value.day = '?'
      }
      break
    case '3':
      if (weekNthDay.value !== null && weekNthWeek.value !== null) {
        fields.value.week = `${weekNthDay.value}#${weekNthWeek.value}`; fields.value.day = '?'
      }
      break
    case '4':
      if (weekLast.value !== null) { fields.value.week = `${weekLast.value}L`; fields.value.day = '?' }
      break
    case '5':
      if (weekSpecific.value.length > 0) { fields.value.week = weekSpecific.value.join(','); fields.value.day = '?' }
      break
  }
}

// 年改变
const handleYearChange = () => {
  switch (yearMode.value) {
    case '0': fields.value.year = ''; break
    case '1': fields.value.year = '*'; break
    case '2':
      if (yearCycleStart.value !== null && yearCycleEnd.value !== null)
        fields.value.year = `${yearCycleStart.value}-${yearCycleEnd.value}`
      break
  }
}

// 监听变化
watch([secondsMode, secondsCycleStart, secondsCycleEnd, secondsStepStart, secondsStepValue, secondsSpecific], handleSecondsChange)
watch([minutesMode, minutesCycleStart, minutesCycleEnd, minutesStepStart, minutesStepValue, minutesSpecific], handleMinutesChange)
watch([hourMode, hourCycleStart, hourCycleEnd, hourStepStart, hourStepValue, hourSpecific], handleHourChange)
watch([dayMode, dayCycleStart, dayCycleEnd, dayStepStart, dayStepValue, dayWorkday, daySpecific], handleDayChange)
watch([monthMode, monthCycleStart, monthCycleEnd, monthStepStart, monthStepValue, monthSpecific], handleMonthChange)
watch([weekMode, weekCycleStart, weekCycleEnd, weekNthWeek, weekNthDay, weekLast, weekSpecific], handleWeekChange)
watch([yearMode, yearCycleStart, yearCycleEnd], handleYearChange)

// 验证表达式
const validateExpression = () => {
  const parts = cronExpression.value.split(' ')
  if (parts.length < 5 || parts.length > 7) {
    message.error('表达式格式错误，需要5-7个字段')
    return false
  }
  message.success('表达式格式正确')
  return true
}

// 暴露给父组件
defineExpose({ cronExpression, validate: validateExpression })

// Emits
const emit = defineEmits(['update:modelValue'])
watch(cronExpression, (val) => emit('update:modelValue', val))
</script>

<template>
  <div class="cron-builder">
    <n-tabs v-model:value="activeTab" type="line">
      <!-- 秒 -->
      <n-tab-pane name="seconds" tab="秒">
        <n-radio-group v-model:value="secondsMode" class="radio-group">
          <n-space vertical>
            <n-radio value="0">每秒</n-radio>
            <n-radio value="1">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="secondsCycleStart" :min="0" :max="59" size="small" style="width: 70px" />
                <span>到</span>
                <n-input-number v-model:value="secondsCycleEnd" :min="0" :max="59" size="small" style="width: 70px" />
                <span>秒</span>
              </n-space>
            </n-radio>
            <n-radio value="2">
              <n-space align="center">
                <span>从</span>
                <n-input-number v-model:value="secondsStepStart" :min="0" :max="59" size="small" style="width: 70px" />
                <span>秒开始，每</span>
                <n-input-number v-model:value="secondsStepValue" :min="1" :max="59" size="small" style="width: 70px" />
                <span>秒执行</span>
              </n-space>
            </n-radio>
            <n-radio value="3">
              <div>
                <span>指定：</span>
                <n-checkbox-group v-model:value="secondsSpecific" class="checkbox-group">
                  <n-checkbox v-for="i in 60" :key="i - 1" :value="String(i - 1)" :label="String(i - 1)" />
                </n-checkbox-group>
              </div>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>

      <!-- 分 -->
      <n-tab-pane name="minutes" tab="分">
        <n-radio-group v-model:value="minutesMode" class="radio-group">
          <n-space vertical>
            <n-radio value="0">每分</n-radio>
            <n-radio value="1">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="minutesCycleStart" :min="0" :max="59" size="small" style="width: 70px" />
                <span>到</span>
                <n-input-number v-model:value="minutesCycleEnd" :min="0" :max="59" size="small" style="width: 70px" />
                <span>分</span>
              </n-space>
            </n-radio>
            <n-radio value="2">
              <n-space align="center">
                <span>从</span>
                <n-input-number v-model:value="minutesStepStart" :min="0" :max="59" size="small" style="width: 70px" />
                <span>分开始，每</span>
                <n-input-number v-model:value="minutesStepValue" :min="1" :max="59" size="small" style="width: 70px" />
                <span>分执行</span>
              </n-space>
            </n-radio>
            <n-radio value="3">
              <div>
                <span>指定：</span>
                <n-checkbox-group v-model:value="minutesSpecific" class="checkbox-group">
                  <n-checkbox v-for="i in 60" :key="i - 1" :value="String(i - 1)" :label="String(i - 1)" />
                </n-checkbox-group>
              </div>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>

      <!-- 时 -->
      <n-tab-pane name="hour" tab="时">
        <n-radio-group v-model:value="hourMode" class="radio-group">
          <n-space vertical>
            <n-radio value="0">每小时</n-radio>
            <n-radio value="1">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="hourCycleStart" :min="0" :max="23" size="small" style="width: 70px" />
                <span>到</span>
                <n-input-number v-model:value="hourCycleEnd" :min="0" :max="23" size="small" style="width: 70px" />
                <span>时</span>
              </n-space>
            </n-radio>
            <n-radio value="2">
              <n-space align="center">
                <span>从</span>
                <n-input-number v-model:value="hourStepStart" :min="0" :max="23" size="small" style="width: 70px" />
                <span>时开始，每</span>
                <n-input-number v-model:value="hourStepValue" :min="1" :max="23" size="small" style="width: 70px" />
                <span>时执行</span>
              </n-space>
            </n-radio>
            <n-radio value="3">
              <div>
                <span>指定：</span>
                <n-checkbox-group v-model:value="hourSpecific" class="checkbox-group">
                  <n-checkbox v-for="i in 24" :key="i - 1" :value="String(i - 1)" :label="String(i - 1)" />
                </n-checkbox-group>
              </div>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>

      <!-- 日 -->
      <n-tab-pane name="day" tab="日">
        <n-radio-group v-model:value="dayMode" class="radio-group">
          <n-space vertical>
            <n-radio value="0">每天</n-radio>
            <n-radio value="1">不指定</n-radio>
            <n-radio value="2">月最后一天</n-radio>
            <n-radio value="3">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="dayCycleStart" :min="1" :max="31" size="small" style="width: 70px" />
                <span>到</span>
                <n-input-number v-model:value="dayCycleEnd" :min="1" :max="31" size="small" style="width: 70px" />
                <span>日</span>
              </n-space>
            </n-radio>
            <n-radio value="4">
              <n-space align="center">
                <span>从</span>
                <n-input-number v-model:value="dayStepStart" :min="1" :max="31" size="small" style="width: 70px" />
                <span>日开始，每</span>
                <n-input-number v-model:value="dayStepValue" :min="1" :max="31" size="small" style="width: 70px" />
                <span>日执行</span>
              </n-space>
            </n-radio>
            <n-radio value="5">
              <n-space align="center">
                <span>每月</span>
                <n-input-number v-model:value="dayWorkday" :min="1" :max="31" size="small" style="width: 70px" />
                <span>号最近工作日</span>
              </n-space>
            </n-radio>
            <n-radio value="6">
              <div>
                <span>指定：</span>
                <n-checkbox-group v-model:value="daySpecific" class="checkbox-group">
                  <n-checkbox v-for="i in 31" :key="i" :value="String(i)" :label="String(i)" />
                </n-checkbox-group>
              </div>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>

      <!-- 月 -->
      <n-tab-pane name="month" tab="月">
        <n-radio-group v-model:value="monthMode" class="radio-group">
          <n-space vertical>
            <n-radio value="0">每月</n-radio>
            <n-radio value="1">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="monthCycleStart" :min="1" :max="12" size="small" style="width: 70px" />
                <span>到</span>
                <n-input-number v-model:value="monthCycleEnd" :min="1" :max="12" size="small" style="width: 70px" />
                <span>月</span>
              </n-space>
            </n-radio>
            <n-radio value="2">
              <n-space align="center">
                <span>从</span>
                <n-input-number v-model:value="monthStepStart" :min="1" :max="12" size="small" style="width: 70px" />
                <span>月开始，每</span>
                <n-input-number v-model:value="monthStepValue" :min="1" :max="12" size="small" style="width: 70px" />
                <span>月执行</span>
              </n-space>
            </n-radio>
            <n-radio value="3">
              <div>
                <span>指定：</span>
                <n-checkbox-group v-model:value="monthSpecific" class="checkbox-group">
                  <n-checkbox v-for="i in 12" :key="i" :value="String(i)" :label="String(i)" />
                </n-checkbox-group>
              </div>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>

      <!-- 周 -->
      <n-tab-pane name="week" tab="周">
        <n-radio-group v-model:value="weekMode" class="radio-group">
          <n-space vertical>
            <n-radio value="1">不指定</n-radio>
            <n-radio value="2">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="weekCycleStart" :min="0" :max="6" size="small" style="width: 70px" />
                <span>到</span>
                <n-input-number v-model:value="weekCycleEnd" :min="0" :max="6" size="small" style="width: 70px" />
                <span>（0=周日）</span>
              </n-space>
            </n-radio>
            <n-radio value="3">
              <n-space align="center">
                <span>第</span>
                <n-input-number v-model:value="weekNthWeek" :min="1" :max="5" size="small" style="width: 70px" />
                <span>周星期</span>
                <n-input-number v-model:value="weekNthDay" :min="0" :max="6" size="small" style="width: 70px" />
              </n-space>
            </n-radio>
            <n-radio value="4">
              <n-space align="center">
                <span>最后一周星期</span>
                <n-input-number v-model:value="weekLast" :min="0" :max="6" size="small" style="width: 70px" />
              </n-space>
            </n-radio>
            <n-radio value="5">
              <div>
                <span>指定：</span>
                <n-checkbox-group v-model:value="weekSpecific" class="checkbox-group">
                  <n-checkbox v-for="(label, index) in weekLabels" :key="index" :value="String(index)" :label="label" />
                </n-checkbox-group>
              </div>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>

      <!-- 年 -->
      <n-tab-pane name="year" tab="年">
        <n-radio-group v-model:value="yearMode" class="radio-group">
          <n-space vertical>
            <n-radio value="0">不指定</n-radio>
            <n-radio value="1">每年</n-radio>
            <n-radio value="2">
              <n-space align="center">
                <span>周期从</span>
                <n-input-number v-model:value="yearCycleStart" :min="2024" :max="2099" size="small" style="width: 90px" />
                <span>到</span>
                <n-input-number v-model:value="yearCycleEnd" :min="2024" :max="2099" size="small" style="width: 90px" />
                <span>年</span>
              </n-space>
            </n-radio>
          </n-space>
        </n-radio-group>
      </n-tab-pane>
    </n-tabs>

    <!-- 生成结果 -->
    <n-card title="生成结果" size="small" class="result-card">
      <n-descriptions label-placement="left" :column="7" size="small">
        <n-descriptions-item label="秒"><n-input v-model:value="fields.seconds" size="tiny" style="width: 50px" /></n-descriptions-item>
        <n-descriptions-item label="分"><n-input v-model:value="fields.minutes" size="tiny" style="width: 50px" /></n-descriptions-item>
        <n-descriptions-item label="时"><n-input v-model:value="fields.hour" size="tiny" style="width: 50px" /></n-descriptions-item>
        <n-descriptions-item label="日"><n-input v-model:value="fields.day" size="tiny" style="width: 50px" /></n-descriptions-item>
        <n-descriptions-item label="月"><n-input v-model:value="fields.month" size="tiny" style="width: 50px" /></n-descriptions-item>
        <n-descriptions-item label="周"><n-input v-model:value="fields.week" size="tiny" style="width: 50px" /></n-descriptions-item>
        <n-descriptions-item label="年"><n-input v-model:value="fields.year" size="tiny" style="width: 50px" /></n-descriptions-item>
      </n-descriptions>

      <n-space vertical class="expression-result">
        <n-space align="center">
          <span class="label">表达式：</span>
          <n-tag type="success">{{ cronExpression }}</n-tag>
        </n-space>
        <n-space align="center">
          <span class="label">含义：</span>
          <span class="desc">{{ cronDescription }}</span>
        </n-space>
      </n-space>
    </n-card>
  </div>
</template>

<style scoped lang="scss">
.cron-builder {
  .radio-group {
    padding: 8px 0;
  }
  .checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 8px;
  }
  .result-card {
    margin-top: 12px;
  }
  .expression-result {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #eee;
    .label { color: #666; font-size: 13px; }
    .desc { color: #18a058; font-size: 13px; }
  }
}
</style>