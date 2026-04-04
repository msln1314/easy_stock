# 卖出预警组合条件功能设计

## 1. 需求概述

### 1.1 背景

当前卖出预警系统每个预警条件独立触发，用户无法将多个条件组合在一起进行综合判断。例如，用户希望当"MA死叉 AND MACD死叉 AND 跌破EXPMA"同时满足时才发出预警，现有系统无法支持。

### 1.2 目标

- 支持多个预警条件的组合判断，包含 AND/OR 混合逻辑
- 支持任意层级的嵌套组合，不限制条件数量
- 用户可通过表单式层级配置界面创建和管理组合条件
- 预警触发时显示组合名称和满足的具体条件列表

### 1.3 关键需求点

| 需求项 | 决策 |
|--------|------|
| 组合逻辑关系 | 混合逻辑（AND/OR 组合） |
| 条件数量限制 | 不限制，支持任意复杂嵌套 |
| 管理交互方式 | 表单式层级配置（分组嵌套） |
| 条件项来源 | 引用现有预警条件（WarningCondition） |
| 预警记录展示 | 显示组合名称 + 满足的子条件列表 |

---

## 2. 数据模型设计

### 2.1 新增表：warning_condition_groups（组合条件组表）

```python
class WarningConditionGroup(Model):
    """组合条件组表"""
    id = fields.IntField(pk=True)
    group_key = fields.CharField(max_length=50, unique=True, description="组合唯一标识")
    group_name = fields.CharField(max_length=100, description="组合名称")
    logic_type = fields.CharField(max_length=10, description="逻辑类型: AND/OR")
    parent_id = fields.IntField(null=True, description="父分组ID，支持嵌套")
    priority = fields.CharField(max_length=20, default="warning", description="优先级")
    is_enabled = fields.BooleanField(default=True, description="是否启用")
    description = fields.TextField(null=True, description="描述")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warning_condition_groups"
        indexes = [("parent_id",), ("group_key",)]
```

### 2.2 新增表：group_condition_items（组合条件项表）

```python
class GroupConditionItem(Model):
    """组合条件项表 - 关联具体预警条件到分组"""
    id = fields.IntField(pk=True)
    group_id = fields.IntField(description="所属分组ID")
    condition_id = fields.IntField(description="关联的预警条件ID")
    sort_order = fields.IntField(default=0, description="排序")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "group_condition_items"
        indexes = [("group_id",), ("condition_id",)]
```

### 2.3 修改表：WarningStockPool（预警股票池表）

新增字段：

```python
# 新增字段
group_key = fields.CharField(max_length=50, null=True, description="触发组合KEY")
is_group = fields.BooleanField(default=False, description="是否组合预警")
triggered_conditions = fields.JSONField(null=True, description="满足的条件列表")
```

### 2.4 扩展表：IndicatorLibrary（指标库表）

新增字段和参数化指标定义：

```python
class IndicatorLibrary(Model):
    """指标库表"""
    id = fields.IntField(pk=True)
    indicator_key = fields.CharField(max_length=50, unique=True, description="指标KEY")
    indicator_name = fields.CharField(max_length=100, description="指标名称")
    category = fields.CharField(max_length=50, description="分类: technical/quote/fundamental")
    indicator_type = fields.CharField(max_length=20, description="类型: calculated/threshold")
    parameters = fields.JSONField(description="参数定义(JSON Schema格式)")
    output_fields = fields.JSONField(description="输出字段定义")
    description = fields.TextField(null=True, description="指标说明")
    is_builtin = fields.BooleanField(default=True, description="是否内置")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

---

## 3. 指标库扩展设计

### 3.1 技术指标类（保持现有）

| indicator_key | indicator_name | category | indicator_type | parameters |
|---------------|----------------|----------|----------------|------------|
| MA | 均线 | technical | calculated | `{"period": {"type": "number", "label": "周期", "default": 5}}` |
| MACD | MACD指标 | technical | calculated | `{"fast_period": 12, "slow_period": 26, "signal_period": 9}` |
| KDJ | KDJ指标 | technical | calculated | `{"n": 9, "m1": 3, "m2": 3}` |
| RSI | RSI指标 | technical | calculated | `{"period": 14}` |
| EXPMA | EXPMA指标 | technical | calculated | `{"period": 12}` |
| BOLL | 布林带 | technical | calculated | `{"period": 20, "std_dev": 2}` |

### 3.2 行情阈值类（新增）

| indicator_key | indicator_name | category | indicator_type | parameters |
|---------------|----------------|----------|----------------|------------|
| THRESHOLD_CHANGE | 涨跌幅阈值 | quote | threshold | `{"start_date": {"type": "date", "required": true}, "threshold_percent": {"type": "number", "default": 5}, "compare_op": {"type": "select", "options": ["gt", "lt", "ge", "le"]}}` |
| THRESHOLD_TURNOVER | 换手率阈值 | quote | threshold | `{"date": {"type": "date", "required": true}, "threshold": {"type": "number", "default": 10}, "compare_op": {"type": "select"}}` |
| THRESHOLD_VOLUME_RATIO | 量比阈值 | quote | threshold | `{"date": {"type": "date", "required": true}, "threshold": {"type": "number", "default": 2}, "compare_op": {"type": "select"}}` |
| THRESHOLD_AMOUNT | 成交额阈值 | quote | threshold | `{"date": {"type": "date"}, "threshold": {"type": "number"}, "unit": {"type": "select", "options": ["亿", "万"]}, "compare_op": {"type": "select"}}` |

### 3.3 基本面阈值类（新增）

| indicator_key | indicator_name | category | indicator_type | parameters |
|---------------|----------------|----------|----------------|------------|
| THRESHOLD_MARKET_VALUE | 市值阈值 | fundamental | threshold | `{"date": {"type": "date"}, "threshold": {"type": "number"}, "unit": {"type": "select", "options": ["亿", "万"]}, "compare_op": {"type": "select"}}` |
| THRESHOLD_PE | 市盈率阈值 | fundamental | threshold | `{"date": {"type": "date"}, "threshold": {"type": "number"}, "compare_op": {"type": "select"}}` |
| THRESHOLD_PB | 市净率阈值 | fundamental | threshold | `{"date": {"type": "date"}, "threshold": {"type": "number"}, "compare_op": {"type": "select"}}` |

### 3.4 参数化指标输出字段示例

```json
// THRESHOLD_CHANGE 输出
{
  "triggered": {"type": "boolean"},
  "actual_change_percent": {"type": "number"},
  "threshold_percent": {"type": "number"},
  "start_price": {"type": "number"},
  "current_price": {"type": "number"},
  "start_date": {"type": "string"}
}

// THRESHOLD_MARKET_VALUE 输出
{
  "triggered": {"type": "boolean"},
  "actual_value": {"type": "number"},
  "threshold": {"type": "number"},
  "unit": {"type": "string"}
}
```

---

## 4. 后端 API 设计

### 4.1 组合条件管理 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/warning/groups` | GET | 获取组合条件列表（树形结构） |
| `/api/warning/groups` | POST | 创建组合条件组 |
| `/api/warning/groups/{id}` | PUT | 更新组合条件组 |
| `/api/warning/groups/{id}` | DELETE | 删除组合条件组（及其子项） |
| `/api/warning/groups/{id}/items` | POST | 向分组添加条件项 |
| `/api/warning/groups/{id}/items/{item_id}` | DELETE | 移除条件项 |
| `/api/warning/groups/{id}/subgroups` | POST | 创建子分组 |

### 4.2 Schema 定义

```python
class ConditionGroupCreate(BaseModel):
    """创建组合条件组"""
    group_name: str
    logic_type: str  # 'AND' | 'OR'
    parent_id: Optional[int] = None
    priority: str = "warning"
    description: Optional[str] = None
    condition_ids: List[int] = []  # 创建时直接关联条件

class ConditionGroupTree(BaseModel):
    """组合条件树形结构"""
    id: int
    group_key: str
    group_name: str
    logic_type: str
    priority: str
    is_enabled: bool
    conditions: List[dict]  # 包含的条件列表
    subgroups: List[ConditionGroupTree]  # 子分组（递归）
```

---

## 5. 预警评估器扩展

### 5.1 评估器主方法扩展

```python
class WarningEvaluator:
    def evaluate(self, klines: List[Dict], condition: Dict, quote: Dict = None) -> Tuple[bool, Dict]:
        """
        评估预警条件
        
        Args:
            klines: K线数据列表（技术指标计算用）
            condition: 预警条件配置
            quote: 实时行情数据（阈值指标判断用）
        """
        rule = json.loads(condition['condition_rule'])
        rule_type = rule.get('rule_type')
        
        # 技术指标类
        if rule_type in ['cross', 'break', 'threshold']:
            return self._evaluate_technical(klines, condition, rule)
        
        # 行情/基本面阈值类
        elif rule_type == 'quote_threshold':
            return self._evaluate_quote_threshold(quote or {}, condition, rule)
        
        return False, {}
```

### 5.2 阈值评估方法

```python
def _evaluate_quote_threshold(self, quote: Dict, condition: Dict, rule: Dict) -> Tuple[bool, Dict]:
    """评估行情/基本面阈值类条件"""
    indicator_key = rule.get('indicator_key')
    params = rule.get('params', {})
    
    if indicator_key == 'THRESHOLD_CHANGE':
        return self._eval_change_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_TURNOVER':
        return self._eval_turnover_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_VOLUME_RATIO':
        return self._eval_volume_ratio_threshold(quote, params)
    elif indicator_key == 'THRESHOLD_MARKET_VALUE':
        return self._eval_market_value_threshold(quote, params)
    # ... 其他阈值指标
    
    return False, {}

def _eval_change_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
    """评估涨跌幅阈值"""
    start_date = params.get('start_date')
    threshold_percent = params.get('threshold_percent')
    compare_op = params.get('compare_op', 'gt')
    
    start_price = quote.get('history_prices', {}).get(start_date)
    current_price = quote.get('price')
    
    if start_price is None or current_price is None:
        return False, {}
    
    actual_change = (current_price - start_price) / start_price * 100
    
    ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
           'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}
    
    triggered = ops[compare_op](actual_change, threshold_percent)
    
    return triggered, {
        'triggered': triggered,
        'actual_change_percent': round(actual_change, 4),
        'threshold_percent': threshold_percent,
        'start_price': round(start_price, 4),
        'current_price': round(current_price, 4),
        'start_date': start_date
    }
```

### 5.3 组合条件递归评估

```python
def evaluate_group(self, klines: List[Dict], quote: Dict, group: Dict) -> Tuple[bool, Dict]:
    """
    评估组合条件组（支持嵌套）
    
    Args:
        klines: K线数据
        quote: 实时行情数据
        group: 组合条件组（包含 conditions 和 subgroups）
    
    Returns:
        (是否触发, 触发详情)
    """
    logic_type = group.get('logic_type', 'AND')
    
    # 评估当前组的所有条件项
    condition_results = []
    for item in group.get('conditions', []):
        condition = item.get('condition')
        triggered, value = self.evaluate(klines, condition, quote)
        condition_results.append({
            'condition_key': condition['condition_key'],
            'condition_name': condition['condition_name'],
            'triggered': triggered,
            'trigger_value': value
        })
    
    # 递归评估子分组
    subgroup_results = []
    for subgroup in group.get('subgroups', []):
        triggered, sub_detail = self.evaluate_group(klines, quote, subgroup)
        subgroup_results.append({
            'group_key': subgroup['group_key'],
            'group_name': subgroup['group_name'],
            'triggered': triggered,
            'details': sub_detail
        })
    
    # 合并结果，按逻辑类型判断
    all_results = condition_results + subgroup_results
    triggered_flags = [r['triggered'] for r in all_results]
    
    if logic_type == 'AND':
        group_triggered = all(triggered_flags)
    else:
        group_triggered = any(triggered_flags)
    
    return group_triggered, {
        'group_name': group['group_name'],
        'logic_type': logic_type,
        'condition_results': condition_results,
        'subgroup_results': subgroup_results,
        'triggered_count': sum(triggered_flags),
        'total_count': len(all_results)
    }
```

---

## 6. 预警检测任务集成

### 6.1 扩展行情数据获取

```python
async def get_extended_quote(stock_code: str, params: Dict = None) -> Dict:
    """
    获取扩展行情数据（支持阈值指标判断）
    
    Returns:
        包含实时行情、历史价格、换手率、市值、量比等数据
    """
    realtime = await get_realtime_quote(stock_code)
    
    history_prices = {}
    if params and 'start_date' in params:
        kline = await get_kline_by_date(stock_code, params['start_date'])
        history_prices[params['start_date']] = kline.get('close')
    
    extended_data = await get_quote_extended(stock_code)  # 换手率、市值等
    
    return {
        **realtime,
        'history_prices': history_prices,
        'turnover_rate': extended_data.get('turnover_rate'),
        'volume_ratio': extended_data.get('volume_ratio'),
        'market_value': extended_data.get('market_value'),
        'amount': extended_data.get('amount'),
        'pe': extended_data.get('pe'),
        'pb': extended_data.get('pb'),
    }
```

### 6.2 检测任务主流程

```python
async def detect_warnings():
    monitor_stocks = await MonitorStock.filter(is_active=True).all()
    conditions = await WarningCondition.filter(is_enabled=True).all()
    groups = await WarningConditionGroup.filter(is_enabled=True).all()
    
    for stock in monitor_stocks:
        klines = await get_kline_from_stock_service(stock.stock_code)
        quote = await get_extended_quote(stock.stock_code)
        
        # 检查普通条件
        for condition in conditions:
            triggered, value = warning_evaluator.evaluate(klines, condition, quote)
            if triggered:
                await WarningStockPool.create(
                    stock_code=stock.stock_code,
                    condition_key=condition.condition_key,
                    condition_name=condition.condition_name,
                    warning_level=condition.priority,
                    trigger_value=value,
                    is_group=False
                )
        
        # 检查组合条件
        for group in groups:
            group_dict = await build_group_tree(group)
            triggered, detail = warning_evaluator.evaluate_group(klines, quote, group_dict)
            
            if triggered:
                triggered_conditions = extract_triggered_conditions(detail)
                await WarningStockPool.create(
                    stock_code=stock.stock_code,
                    condition_key=group.group_key,
                    condition_name=group.group_name,
                    warning_level=group.priority,
                    trigger_value=detail,
                    triggered_conditions=triggered_conditions,
                    is_group=True
                )
```

---

## 7. 前端 UI 设计

### 7.1 页面结构

新增组合条件管理页面：

```
views/warning/
├── ConditionGroup.vue          # 组合条件管理页面
├── ConditionGroupTree.vue      # 左侧树形组件
├── ConditionGroupEditor.vue    # 右侧编辑面板
├── components/
│   ├── ConditionSelector.vue   # 条件选择下拉框
│   ├── ParamInput.vue          # 动态参数输入组件
│   └── LogicTypeSelector.vue   # AND/OR选择器
├── signal/index.vue            # 预警列表页面（修改）
```

### 7.2 页面布局

```
┌─────────────────────────────────────────────────────────┐
│  组合条件管理                    [新增组合] [刷新]        │
├──────────────────┬──────────────────────────────────────┤
│  组合列表（树形） │  配置面板                             │
│                  │                                      │
│  📁 MA+MACD组合   │  组合名称: [MA+MACD组合]              │
│   ├─ 📁 死叉组    │  逻辑类型: [AND ▼]                    │
│   │   ├─ MA死叉   │  优先级:   [warning ▼]               │
│   │   ├─ MACD死叉 │                                      │
│   │   └─ KDJ死叉  │  条件列表:                            │
│   └─ 📁 突破组    │  ┌──────────────────────┐           │
│       ├─ 跌破EXPMA│  │ [MA死叉]     [移除]   │           │
│       └─ RSI超买  │  │ [MACD死叉]   [移除]   │           │
│                  │  │ [+ 添加条件]          │           │
│                  │  └──────────────────────┘           │
│                  │                                      │
│                  │  子分组:                              │
│                  │  ┌──────────────────────┐           │
│                  │  │ 📁 死叉组 (OR) [编辑] │           │
│                  │  │ [+ 新增子分组]        │           │
│                  │  └──────────────────────┘           │
│                  │                                      │
│                  │  [保存] [取消] [删除组合]             │
└──────────────────┴──────────────────────────────────────┘
```

### 7.3 预警列表触发条件展示

组合预警显示格式：`组合名称（条件1✓ 条件2✓ 条件3✗）`

```vue
{
  title: '触发条件',
  render: (row: SignalRecord) => {
    if (row.is_group) {
      const tags = row.triggered_conditions?.map(c => 
        h(NTag, { 
          type: c.triggered ? 'success' : 'default', 
          size: 'small'
        }, { default: () => c.condition_name })
      ) || []
      
      return h(NSpace, {}, {
        default: () => [
          h(NText, { strong: true }, { default: () => row.condition_name }),
          h(NText, {}, { default: () => '(' }),
          ...tags,
          h(NText, {}, { default: () => ')' })
        ]
      })
    }
    // 普通条件原有渲染...
  }
}
```

### 7.4 triggered_conditions 数据结构

```json
[
  {"condition_key": "MA_DEAD_CROSS", "condition_name": "MA死叉", "triggered": true},
  {"condition_key": "MACD_DEAD_CROSS", "condition_name": "MACD死叉", "triggered": true},
  {"condition_key": "RSI_OVERSOLD", "condition_name": "RSI超卖", "triggered": false}
]
```

---

## 8. 实施要点

### 8.1 数据库迁移顺序

1. 修改 `IndicatorLibrary` 表结构（新增 `indicator_type` 字段）
2. 初始化新增的参数化指标数据
3. 创建 `warning_condition_groups` 表
4. 创建 `group_condition_items` 表
5. 修改 `WarningStockPool` 表（新增字段）

### 8.2 qmt-service 接口扩展

需要确认或扩展以下接口：
- 获取指定日期的K线/收盘价
- 获取换手率、量比、市值、成交额数据
- 获取 PE、PB 等基本面数据

### 8.3 前端动态参数组件

根据指标库的 `parameters` JSON Schema 动态渲染参数输入表单，支持：
- `type: "date"` → 日期选择器
- `type: "number"` → 数字输入框
- `type: "select"` → 下拉选择框

---

## 9. 后续优化方向

- 支持拖拽调整条件项顺序
- 组合条件模板功能（预设常用组合）
- 组合条件的回测验证
- 预警触发历史统计（按组合维度）