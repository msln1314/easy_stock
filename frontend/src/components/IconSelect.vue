<template>
  <n-popover trigger="click" placement="bottom-start" :width="400">
    <template #trigger>
      <n-input
        :value="modelValue"
        placeholder="点击选择图标"
        readonly
        clearable
        @clear="handleClear"
      >
        <template #prefix v-if="modelValue">
          <n-icon :component="selectedIcon" />
        </template>
      </n-input>
    </template>

    <div class="icon-picker">
      <n-input
        v-model:value="searchKeyword"
        placeholder="搜索图标"
        size="small"
        clearable
        class="mb-2"
      />

      <n-scrollbar style="max-height: 300px">
        <div class="icon-grid">
          <div
            v-for="icon in filteredIcons"
            :key="icon.name"
            class="icon-item"
            :class="{ selected: modelValue === icon.name }"
            @click="handleSelect(icon.name)"
          >
            <n-icon :component="icon.component" size="24" />
            <span class="icon-name">{{ icon.name }}</span>
          </div>
        </div>
      </n-scrollbar>
    </div>
  </n-popover>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  GridOutline,
  TrendingUpOutline,
  TrendingDownOutline,
  AnalyticsOutline,
  FilterOutline,
  LibraryOutline,
  EyeOutline,
  TimeOutline,
  SwapHorizontalOutline,
  BookOutline,
  CogOutline,
  ListOutline,
  ShieldOutline,
  SettingsOutline,
  PeopleOutline,
  FolderOutline,
  ChatbubbleOutline,
  AlertOutline,
  WarningOutline,
  FlashOutline,
  SparklesOutline,
  FunnelOutline,
  GitBranchOutline,
  DocumentTextOutline,
  HomeOutline,
  PersonOutline,
  LogOutOutline,
  AddOutline,
  CreateOutline,
  TrashOutline,
  SearchOutline,
  RefreshOutline,
  DownloadOutline,
  CloudOutline,
  CloudDownloadOutline,
  MailOutline,
  NotificationsOutline,
  CalendarOutline,
  LocationOutline,
  MapOutline,
  GlobeOutline,
  CodeOutline,
  RocketOutline,
  HeartOutline,
  StarOutline,
  ThumbsUpOutline,
  LockClosedOutline,
  KeyOutline,
  CardOutline,
  CashOutline,
  CubeOutline,
  LayersOutline,
  AppsOutline,
  MenuOutline,
  ArrowBackOutline,
  ArrowForwardOutline,
  ArrowUpOutline,
  ArrowDownOutline,
  CheckmarkOutline,
  CloseOutline,
  InformationOutline,
  HelpOutline,
  AddCircleOutline,
  LinkOutline,
  ShareOutline,
  CopyOutline,
  ClipboardOutline,
  ImageOutline,
  PlayOutline,
  PauseOutline,
  StopOutline,
  TvOutline,
  RadioOutline,
  MicOutline,
  PrintOutline,
  PowerOutline,
  MedalOutline,
  GiftOutline,
  FlagOutline,
  FlameOutline,
  MoonOutline,
  SunnyOutline,
  UmbrellaOutline,
} from '@vicons/ionicons5'

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const searchKeyword = ref('')

// 图标列表
const iconList = [
  { name: 'GridOutline', component: GridOutline },
  { name: 'TrendingUpOutline', component: TrendingUpOutline },
  { name: 'TrendingDownOutline', component: TrendingDownOutline },
  { name: 'AnalyticsOutline', component: AnalyticsOutline },
  { name: 'FilterOutline', component: FilterOutline },
  { name: 'LibraryOutline', component: LibraryOutline },
  { name: 'EyeOutline', component: EyeOutline },
  { name: 'TimeOutline', component: TimeOutline },
  { name: 'SwapHorizontalOutline', component: SwapHorizontalOutline },
  { name: 'BookOutline', component: BookOutline },
  { name: 'CogOutline', component: CogOutline },
  { name: 'ListOutline', component: ListOutline },
  { name: 'ShieldOutline', component: ShieldOutline },
  { name: 'SettingsOutline', component: SettingsOutline },
  { name: 'PeopleOutline', component: PeopleOutline },
  { name: 'FolderOutline', component: FolderOutline },
  { name: 'ChatbubbleOutline', component: ChatbubbleOutline },
  { name: 'AlertOutline', component: AlertOutline },
  { name: 'WarningOutline', component: WarningOutline },
  { name: 'FlashOutline', component: FlashOutline },
  { name: 'SparklesOutline', component: SparklesOutline },
  { name: 'FunnelOutline', component: FunnelOutline },
  { name: 'GitBranchOutline', component: GitBranchOutline },
  { name: 'DocumentTextOutline', component: DocumentTextOutline },
  { name: 'HomeOutline', component: HomeOutline },
  { name: 'PersonOutline', component: PersonOutline },
  { name: 'LogOutOutline', component: LogOutOutline },
  { name: 'AddOutline', component: AddOutline },
  { name: 'CreateOutline', component: CreateOutline },
  { name: 'TrashOutline', component: TrashOutline },
  { name: 'SearchOutline', component: SearchOutline },
  { name: 'RefreshOutline', component: RefreshOutline },
  { name: 'DownloadOutline', component: DownloadOutline },
  { name: 'CloudOutline', component: CloudOutline },
  { name: 'CloudDownloadOutline', component: CloudDownloadOutline },
  { name: 'MailOutline', component: MailOutline },
  { name: 'NotificationsOutline', component: NotificationsOutline },
  { name: 'CalendarOutline', component: CalendarOutline },
  { name: 'LocationOutline', component: LocationOutline },
  { name: 'MapOutline', component: MapOutline },
  { name: 'GlobeOutline', component: GlobeOutline },
  { name: 'CodeOutline', component: CodeOutline },
  { name: 'RocketOutline', component: RocketOutline },
  { name: 'HeartOutline', component: HeartOutline },
  { name: 'StarOutline', component: StarOutline },
  { name: 'ThumbsUpOutline', component: ThumbsUpOutline },
  { name: 'LockClosedOutline', component: LockClosedOutline },
  { name: 'KeyOutline', component: KeyOutline },
  { name: 'CardOutline', component: CardOutline },
  { name: 'CashOutline', component: CashOutline },
  { name: 'CubeOutline', component: CubeOutline },
  { name: 'LayersOutline', component: LayersOutline },
  { name: 'AppsOutline', component: AppsOutline },
  { name: 'MenuOutline', component: MenuOutline },
  { name: 'ArrowBackOutline', component: ArrowBackOutline },
  { name: 'ArrowForwardOutline', component: ArrowForwardOutline },
  { name: 'ArrowUpOutline', component: ArrowUpOutline },
  { name: 'ArrowDownOutline', component: ArrowDownOutline },
  { name: 'CheckmarkOutline', component: CheckmarkOutline },
  { name: 'CloseOutline', component: CloseOutline },
  { name: 'InformationOutline', component: InformationOutline },
  { name: 'HelpOutline', component: HelpOutline },
  { name: 'AddCircleOutline', component: AddCircleOutline },
  { name: 'LinkOutline', component: LinkOutline },
  { name: 'ShareOutline', component: ShareOutline },
  { name: 'CopyOutline', component: CopyOutline },
  { name: 'ClipboardOutline', component: ClipboardOutline },
  { name: 'ImageOutline', component: ImageOutline },
  { name: 'PlayOutline', component: PlayOutline },
  { name: 'PauseOutline', component: PauseOutline },
  { name: 'StopOutline', component: StopOutline },
  { name: 'TvOutline', component: TvOutline },
  { name: 'RadioOutline', component: RadioOutline },
  { name: 'MicOutline', component: MicOutline },
  { name: 'PrintOutline', component: PrintOutline },
  { name: 'PowerOutline', component: PowerOutline },
  { name: 'MedalOutline', component: MedalOutline },
  { name: 'GiftOutline', component: GiftOutline },
  { name: 'FlagOutline', component: FlagOutline },
  { name: 'FlameOutline', component: FlameOutline },
  { name: 'MoonOutline', component: MoonOutline },
  { name: 'SunnyOutline', component: SunnyOutline },
  { name: 'UmbrellaOutline', component: UmbrellaOutline },
]

// 过滤后的图标列表
const filteredIcons = computed(() => {
  if (!searchKeyword.value) return iconList

  const keyword = searchKeyword.value.toLowerCase()
  return iconList.filter(icon =>
    icon.name.toLowerCase().includes(keyword)
  )
})

// 选中的图标组件
const selectedIcon = computed(() => {
  const icon = iconList.find(i => i.name === props.modelValue)
  return icon?.component || FolderOutline
})

function handleSelect(name: string) {
  emit('update:modelValue', name)
}

function handleClear() {
  emit('update:modelValue', '')
}
</script>

<style scoped lang="scss">
.icon-picker {
  .mb-2 {
    margin-bottom: 8px;
  }
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #18a058;
    background-color: #f0f9f4;
  }

  &.selected {
    border-color: #18a058;
    background-color: #e8f5e9;
  }

  .icon-name {
    font-size: 10px;
    color: #666;
    margin-top: 4px;
    text-align: center;
    word-break: break-all;
  }
}
</style>