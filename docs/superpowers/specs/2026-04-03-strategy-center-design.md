# 策略中心系统设计文档

**文档版本**: v1.0
**创建日期**: 2026-04-03
**作者**: Claude (Brainstorming Session)

---

## 1. 需求分析

### 1.1 业务背景

策略中心是一个股票交易策略管理系统，用于管理、配置和监控不同的交易策略。系统需要支持策略的完整生命周期管理，包括创建、编辑、回测验证、实时运行和效果监控。

### 1.2 核心需求

| 需求项 | 说明 |
|--------|------|
| **策略类型** | 股票交易策略，包含技术指标配置、买卖信号规则、止盈止损设置三大部分 |
| **执行模式** | 支持三种模式：自动交易（对接券商）、信号提醒（推送通知）、模拟运行（虚拟环境） |
| **回测功能** | 使用历史数据验证策略表现，计算收益率、最大回撤、胜率等指标 |
| **实时对比** | 策略运行过程中持续对比实际表现与回测预期 |
| **页面布局** | 左侧导航分类筛选 + 右侧策略列表展示 |
| **编辑方式** | 分步向导表单，5步完成策略创建/编辑 |

### 1.3 模块化架构

系统采用模块化设计，分阶段实现：

- **Phase 1 (核心模块)**: 策略CRUD、配置管理、分类筛选、分步向导
- **Phase 2 (回测模块)**: 历史数据回测、收益曲线、性能指标
- **Phase 3 (实时模块)**: 行情订阅、实时监控、信号推送
- **Phase 4 (交易模块)**: 券商对接、自动下单

本文档聚焦 **Phase 1 核心模块** 的详细设计。

---

## 2. 技术栈

### 2.1 前端技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| 核心框架 | Vue3 + TypeScript + Vite | 基础架构 |
| UI组件库 | NaiveUI | 表格、表单、弹窗、步骤条、按钮等 |
| 状态管理 | Pinia | 策略列表、筛选状态、向导表单数据 |
| 路由 | Vue Router | 页面导航 |
| 样式 | UnoCSS + SCSS | 布局、主题样式 |
| 图表 | ECharts + vue-echarts | 回测收益曲线展示 |
| HTTP | Axios | API请求封装 |

### 2.2 后端技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| 核心框架 | FastAPI + Python 3.11+ | RESTful API服务 |
| 数据库 | MySQL 8.0 | 数据持久化存储 |
| ORM | Tortoise-ORM | 数据库操作 |
| 数据验证 | Pydantic | Schema验证、序列化 |
| 日志 | Loguru | 日志记录与管理 |
| 数据处理 | Pandas (Phase 2) | 回测计算与数据分析 |

### 2.3 数据库配置

| 配置项 | 值 |
|--------|-----|
| 主机 | localhost |
| 端口 | 3306 |
| 用户名 | root |
| 密码 | 1qaz2wsx |
| 数据库名 | stock_policy |
| 字符集 | utf8mb4 |

---

## 3. 数据库设计

### 3.1 表结构设计

#### 3.1.1 策略主表 (t_strategy)

```sql
CREATE TABLE t_strategy (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT '策略名称',
    description VARCHAR(500) COMMENT '策略描述',
    execute_mode VARCHAR(20) NOT NULL DEFAULT 'simulate' COMMENT '执行模式: auto/alert/simulate',
    status VARCHAR(20) NOT NULL DEFAULT 'paused' COMMENT '状态: running/paused/stopped',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by INT COMMENT '创建用户ID',
    INDEX idx_status (status),
    INDEX idx_execute_mode (execute_mode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略主表';
```

**字段说明**:
- `execute_mode`: 执行模式枚举值
  - `auto`: 自动交易，系统自动执行买卖操作
  - `alert`: 信号提醒，推送通知用户手动决策
  - `simulate`: 模拟运行，虚拟环境测试
- `status`: 运行状态枚举值
  - `running`: 运行中
  - `paused`: 已暂停
  - `stopped`: 已停止

#### 3.1.2 技术指标配置表 (t_strategy_indicator)

```sql
CREATE TABLE t_strategy_indicator (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    indicator_type VARCHAR(50) NOT NULL COMMENT '指标类型: MA/MACD/RSI/KDJ/BOLL等',
    parameters JSON NOT NULL COMMENT '指标参数JSON',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_strategy(id) ON DELETE CASCADE,
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标配置表';
```

**参数JSON示例**:
```json
{
    "period": 20,
    "type": "EMA"
}
```

#### 3.1.3 买卖信号规则表 (t_strategy_signal)

```sql
CREATE TABLE t_strategy_signal (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    signal_type VARCHAR(20) NOT NULL COMMENT '信号类型: buy/sell',
    condition_type VARCHAR(50) NOT NULL COMMENT '条件类型: indicator_cross/threshold/custom',
    condition_config JSON NOT NULL COMMENT '条件配置JSON',
    priority INT DEFAULT 0 COMMENT '优先级',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_strategy(id) ON DELETE CASCADE,
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='买卖信号规则表';
```

**条件配置JSON示例**:
```json
{
    "indicator1": "MA5",
    "indicator2": "MA20",
    "direction": "up"
}
```

#### 3.1.4 止盈止损配置表 (t_strategy_risk)

```sql
CREATE TABLE t_strategy_risk (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    stop_profit_type VARCHAR(20) COMMENT '止盈类型: fixed_percent/dynamic/trailing',
    stop_profit_value DECIMAL(10,4) COMMENT '止盈值',
    stop_loss_type VARCHAR(20) COMMENT '止损类型: fixed_percent/dynamic',
    stop_loss_value DECIMAL(10,4) COMMENT '止损值',
    max_position DECIMAL(10,4) COMMENT '最大仓位比例',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_strategy(id) ON DELETE CASCADE,
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='止盈止损配置表';
```

#### 3.1.5 回测记录表 (t_strategy_backtest) - Phase 2

```sql
CREATE TABLE t_strategy_backtest (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    start_date DATE NOT NULL COMMENT '回测开始日期',
    end_date DATE NOT NULL COMMENT '回测结束日期',
    total_return DECIMAL(10,4) COMMENT '总收益率',
    max_drawdown DECIMAL(10,4) COMMENT '最大回撤',
    win_rate DECIMAL(10,4) COMMENT '胜率',
    trade_count INT COMMENT '交易次数',
    sharpe_ratio DECIMAL(10,4) COMMENT '夏普比率',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_strategy(id) ON DELETE CASCADE,
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测记录表';
```

### 3.2 ER关系图

```
t_strategy (主表)
    │
    ├── t_strategy_indicator (1:N)
    │   每个策略可配置多个技术指标
    │
    ├── t_strategy_signal (1:N)
    │   每个策略可有多条买入/卖出规则
    │
    ├── t_strategy_risk (1:1)
    │   每个策略一套止盈止损配置
    │
    └── t_strategy_backtest (1:N) [Phase 2]
        每个策略多次回测记录
```

---

## 4. 接口设计

### 4.1 接口规范

遵循 AGENTS.md 中定义的响应风格：

**统一响应格式**:
```json
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

**RESTful风格**: 使用标准HTTP方法（GET/POST/PUT/DELETE）

### 4.2 接口列表

#### 4.2.1 策略管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/strategies` | GET | 获取策略列表（支持筛选、分页） |
| `/api/v1/strategies/{id}` | GET | 获取策略详情 |
| `/api/v1/strategies` | POST | 创建策略（完整配置） |
| `/api/v1/strategies/{id}` | PUT | 更新策略（完整配置） |
| `/api/v1/strategies/{id}` | DELETE | 删除策略 |
| `/api/v1/strategies/{id}/status` | PUT | 更新策略状态 |
| `/api/v1/strategies/stats` | GET | 获取策略统计信息 |

#### 4.2.2 技术指标接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/strategies/{id}/indicators` | GET | 获取策略指标配置 |
| `/api/v1/strategies/{id}/indicators` | POST | 添加指标配置 |
| `/api/v1/strategies/{id}/indicators/{iid}` | PUT | 更新指标配置 |
| `/api/v1/strategies/{id}/indicators/{iid}` | DELETE | 删除指标配置 |

#### 4.2.3 买卖信号接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/strategies/{id}/signals` | GET | 获取策略信号规则 |
| `/api/v1/strategies/{id}/signals` | POST | 添加信号规则 |
| `/api/v1/strategies/{id}/signals/{sid}` | PUT | 更新信号规则 |
| `/api/v1/strategies/{id}/signals/{sid}` | DELETE | 删除信号规则 |

#### 4.2.4 止盈止损接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/strategies/{id}/risk` | GET | 获取止盈止损配置 |
| `/api/v1/strategies/{id}/risk` | POST | 创建止盈止损配置 |
| `/api/v1/strategies/{id}/risk` | PUT | 更新止盈止损配置 |

#### 4.2.5 回测接口 (Phase 2)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/strategies/{id}/backtest` | POST | 运行回测 |
| `/api/v1/strategies/{id}/backtest/results` | GET | 获取回测结果 |

### 4.3 接口详细定义

#### 4.3.1 创建策略（完整配置）

**POST `/api/v1/strategies`**

Request Body:
```json
{
    "name": "均线交叉策略",
    "description": "基于MA5和MA20交叉的经典策略",
    "execute_mode": "simulate",
    "status": "paused",
    "indicators": [
        {
            "indicator_type": "MA",
            "parameters": {
                "period": 5,
                "type": "EMA"
            }
        },
        {
            "indicator_type": "MA",
            "parameters": {
                "period": 20,
                "type": "EMA"
            }
        }
    ],
    "signals": [
        {
            "signal_type": "buy",
            "condition_type": "indicator_cross",
            "condition_config": {
                "indicator1": "MA5",
                "indicator2": "MA20",
                "direction": "up"
            },
            "priority": 1
        },
        {
            "signal_type": "sell",
            "condition_type": "indicator_cross",
            "condition_config": {
                "indicator1": "MA5",
                "indicator2": "MA20",
                "direction": "down"
            },
            "priority": 1
        }
    ],
    "risk": {
        "stop_profit_type": "fixed_percent",
        "stop_profit_value": 10.0,
        "stop_loss_type": "fixed_percent",
        "stop_loss_value": 5.0,
        "max_position": 80.0
    }
}
```

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "均线交叉策略",
        "status": "paused",
        "created_at": "2026-04-03T10:00:00"
    }
}
```

#### 4.3.2 获取策略列表

**GET `/api/v1/strategies`**

Query Parameters:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execute_mode | string | 否 | 执行模式筛选 |
| status | string | 否 | 状态筛选 |
| keyword | string | 否 | 关键词搜索 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页条数，默认10 |

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 12,
        "page": 1,
        "page_size": 10,
        "items": [
            {
                "id": 1,
                "name": "均线交叉策略",
                "description": "基于MA5和MA20交叉",
                "execute_mode": "simulate",
                "status": "running",
                "total_return": 12.5,
                "win_rate": 68.0,
                "trade_count": 15,
                "created_at": "2026-04-03T10:00:00",
                "updated_at": "2026-04-03T12:00:00"
            }
        ]
    }
}
```

#### 4.3.3 获取策略详情

**GET `/api/v1/strategies/{id}`**

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "均线交叉策略",
        "description": "基于MA5和MA20交叉的经典策略",
        "execute_mode": "simulate",
        "status": "running",
        "indicators": [
            {
                "id": 1,
                "indicator_type": "MA",
                "parameters": {"period": 5, "type": "EMA"}
            },
            {
                "id": 2,
                "indicator_type": "MA",
                "parameters": {"period": 20, "type": "EMA"}
            }
        ],
        "signals": [
            {
                "id": 1,
                "signal_type": "buy",
                "condition_type": "indicator_cross",
                "condition_config": {"indicator1": "MA5", "indicator2": "MA20", "direction": "up"},
                "priority": 1
            }
        ],
        "risk": {
            "id": 1,
            "stop_profit_type": "fixed_percent",
            "stop_profit_value": 10.0,
            "stop_loss_type": "fixed_percent",
            "stop_loss_value": 5.0,
            "max_position": 80.0
        },
        "created_at": "2026-04-03T10:00:00",
        "updated_at": "2026-04-03T12:00:00"
    }
}
```

#### 4.3.4 更新策略状态

**PUT `/api/v1/strategies/{id}/status`**

Request Body:
```json
{
    "status": "running"
}
```

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "status": "running",
        "updated_at": "2026-04-03T14:00:00"
    }
}
```

#### 4.3.5 获取策略统计信息

**GET `/api/v1/strategies/stats`**

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 12,
        "by_execute_mode": {
            "auto": 3,
            "alert": 4,
            "simulate": 5
        },
        "by_status": {
            "running": 8,
            "paused": 4,
            "stopped": 0
        },
        "avg_return": 8.3,
        "avg_win_rate": 55.2
    }
}
```

---

## 5. 页面设计

### 5.1 页面结构

```
/policy/strategy
├── index.vue                    # 策略列表主页面
├── components/
│   ├── StrategyList.vue         # 策略列表组件
│   ├── StrategyFilter.vue       # 左侧筛选导航
│   ├── StrategyCard.vue         # 策略信息卡片（列表项）
│   ├── StrategyWizard.vue       # 分步向导表单容器
│   ├── StepBasic.vue            # Step1: 基础信息
│   ├── StepIndicator.vue        # Step2: 技术指标
│   ├── StepSignal.vue           # Step3: 买卖信号
│   ├── StepRisk.vue             # Step4: 止盈止损
│   └── StepBacktest.vue         # Step5: 回测验证
└── types/
    └── strategy.ts              # TypeScript类型定义
```

### 5.2 主页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  顶部操作栏                                                  │
│  [新增策略] [批量操作]                         [搜索框]      │
├───────────────┬─────────────────────────────────────────────┤
│               │                                             │
│  左侧导航      │  右侧策略列表                                │
│               │                                             │
│  全部策略(12)  │  ┌──────────────────────────────────────┐ │
│  ───────────  │  │ 策略卡片                              │ │
│  执行模式      │  │ 均线交叉策略        [运行中] [模拟]    │ │
│  ├ 自动交易(3)│  │ 收益: +12.5%  胜率: 68%               │ │
│  ├ 信号提醒(4)│  │ [编辑] [暂停] [删除] [查看详情]        │ │
│  └ 模拟运行(5)│  └──────────────────────────────────────┘ │
│               │                                             │
│  ───────────  │  ┌──────────────────────────────────────┐ │
│  运行状态      │  │ 策略卡片                              │ │
│  ├ 运行中(8)  │  │ MACD动量策略        [已暂停] [自动]    │ │
│  ├ 已暂停(4)  │  │ 收益: -2.3%   胜率: 45%               │ │
│  └ 已停止(0)  │  │ [编辑] [启动] [删除] [查看详情]        │ │
│               │  └──────────────────────────────────────┘ │
│               │                                             │
│               │  分页: [上一页] 1/2 [下一页]                 │
└───────────────┴─────────────────────────────────────────────┘
```

### 5.3 分步向导设计

#### Step 1: 基础信息

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 策略名称 | Input | 是 | 策略唯一名称，最多100字符 |
| 策略描述 | TextArea | 否 | 策略说明，最多500字符 |
| 执行模式 | Radio | 是 | 自动交易/信号提醒/模拟运行 |
| 关联股票 | Select | 是 | 选择策略适用的股票列表 |

#### Step 2: 技术指标

| 操作 | 说明 |
|------|------|
| 添加指标 | 从预定义列表选择指标类型 |
| 配置参数 | 根据指标类型配置具体参数 |
| 删除指标 | 移除已添加的指标配置 |

**预定义指标类型**:
- MA（均线）：period, type (SMA/EMA)
- MACD：fast_period, slow_period, signal_period
- RSI：period
- KDJ：n, m1, m2
- BOLL（布林带）：period, std_dev

#### Step 3: 买卖信号

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 信号类型 | Select | 是 | buy（买入）/ sell（卖出） |
| 条件类型 | Select | 是 | indicator_cross（指标交叉）/ threshold（阈值触发）/ custom（自定义） |
| 条件配置 | DynamicForm | 是 | 根据条件类型动态生成配置项 |
| 优先级 | InputNumber | 否 | 信号执行优先级，默认0 |

#### Step 4: 止盈止损

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 止盈类型 | Radio | 否 | fixed_percent（固定百分比）/ dynamic（动态）/ trailing（移动止盈） |
| 止盈值 | InputNumber | 条件必填 | 止盈触发阈值，单位% |
| 止损类型 | Radio | 否 | fixed_percent（固定百分比）/ dynamic（动态） |
| 止损值 | InputNumber | 条件必填 | 止损触发阈值，单位% |
| 最大仓位 | InputNumber | 否 | 单策略最大仓位比例，默认100% |

#### Step 5: 回测验证

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 开始日期 | DatePicker | 是 | 回测时间范围开始 |
| 结束日期 | DatePicker | 是 | 回测时间范围结束 |
| 运行回测 | Button | - | 点击触发回测计算 |
| 收益曲线 | Chart | - | ECharts展示收益曲线 |
| 关键指标 | Statistics | - | 总收益、最大回撤、胜率、交易次数 |

---

## 6. 开发计划

### 6.1 Phase 1 开发计划（核心模块）

| 日期 | 任务 | 输出物 |
|------|------|--------|
| **Day 1-2** | 数据库设计与初始化 | |
| | 创建MySQL数据库 | stock_policy数据库 |
| | 执行建表SQL | 5张核心表 |
| | 编写Tortoise-ORM模型 | models/strategy.py等 |
| | 数据库初始化脚本 | init_db.py |
| **Day 3-4** | 后端API开发 | |
| | 策略CRUD接口 | api/v1/strategy.py |
| | 指标/信号/风控接口 | api/v1/strategy_indicators.py等 |
| | 统计接口 | api/v1/strategy_stats.py |
| | Schema定义 | schemas/strategy.py |
| | Service层实现 | services/strategy.py |
| **Day 5-7** | 前端页面开发 | |
| | 策略列表主页面 | views/strategy/index.vue |
| | 左侧筛选导航 | components/StrategyFilter.vue |
| | 策略卡片组件 | components/StrategyCard.vue |
| | 分步向导容器 | components/StrategyWizard.vue |
| | Step1-5表单组件 | components/Step*.vue |
| | API封装 | api/strategy.ts |
| | 类型定义 | types/strategy.ts |
| | Pinia状态管理 | stores/strategy.ts |
| **Day 8** | 联调与测试 | |
| | 前后端接口联调 | - |
| | 功能测试验证 | - |
| | Bug修复 | - |
| **Day 9** | 优化与文档 | |
| | UI细节优化 | - |
| | ESLint校验 | - |
| | 使用文档编写 | README更新 |

### 6.2 Phase 2+ 规划

| 阶段 | 功能模块 | 主要内容 |
|------|----------|----------|
| **Phase 2** | 回测引擎 | 历史数据导入、策略回测计算、收益曲线生成、性能指标计算、回测结果存储 |
| **Phase 3** | 实时监控 | 行情数据订阅（WebSocket/轮询）、实时收益跟踪、信号推送通知、异常预警 |
| **Phase 4** | 自动交易 | 券商接口对接、自动下单执行、交易记录、风控检查 |

---

## 7. 项目结构

### 7.1 前端项目结构

```
frontend/
├── src/
│   ├── api/
│   │   └── strategy.ts           # 策略API封装
│   ├── components/
│   │   ├── StrategyFilter.vue    # 左侧筛选导航
│   │   ├── StrategyCard.vue      # 策略卡片
│   │   ├── StrategyWizard.vue    # 向导容器
│   │   ├── StepBasic.vue         # Step1
│   │   ├── StepIndicator.vue     # Step2
│   │   ├── StepSignal.vue        # Step3
│   │   ├── StepRisk.vue          # Step4
│   │   └── StepBacktest.vue      # Step5
│   ├── composables/
│   │   └── useStrategy.ts        # 策略相关hooks
│   ├── router/
│   │   └── index.ts              # 路由配置
│   ├── stores/
│   │   ├── strategy.ts           # 策略状态管理
│   │   └── wizard.ts             # 向导表单状态
│   ├── types/
│   │   └── strategy.ts           # TypeScript类型
│   ├── utils/
│   │   └── helpers.ts            # 工具函数
│   └── views/
│       └── strategy/
│           └── index.vue         # 策略列表主页面
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
```

### 7.2 后端项目结构

```
backend/
├── main.py                       # 应用入口
├── config/
│   ├── database.py               # 数据库配置
│   └── settings.py               # 应用配置
├── core/
│   ├── response.py               # 统一响应
│   ├── exceptions.py             # 异常处理
│   └── middleware.py             # 中间件
├── models/
│   ├── strategy.py               # 策略模型
│   ├── indicator.py              # 指标模型
│   ├── signal.py                 # 信号模型
│   └── risk.py                   # 风控模型
├── schemas/
│   ├── strategy.py               # 策略Schema
│   ├── indicator.py              # 指标Schema
│   ├── signal.py                 # 信号Schema
│   └── risk.py                   # 风控Schema
├── services/
│   ├── strategy.py               # 策略服务
│   ├── indicator.py              # 指标服务
│   ├── signal.py                 # 信号服务
│   └── risk.py                   # 风控服务
├── routes/
│   └── strategy.py               # 策略路由
├── api/
│   └── v1/
│       ├── strategy.py           # 策略API
│       ├── strategy_indicator.py # 指标API
│       ├── strategy_signal.py    # 信号API
│       ├── strategy_risk.py      # 风控API
│       └── strategy_stats.py     # 统计API
├── scripts/
│   └── init_db.py                # 数据库初始化
├── logs/                         # 日志目录
└── requirements.txt              # 依赖清单
```

---

## 8. UI风格要求

遵循 AGENTS.md 中定义的UI风格：

- **表格选项颜色**: 不同选项需要有不同的颜色区分
- **按钮清晰简洁**: 操作按钮语义明确，样式简洁
- **中文显示**: 页面所有文本使用中文
- **友好报错**: 前端错误信息友好展示
- **分页排序导出**: 表格支持分页、排序、导出功能
- **筛选查询**: 支持多条件筛选和查询

---

## 9. 验收标准

### 9.1 功能验收

| 功能点 | 验收标准 |
|--------|----------|
| 策略列表 | 正确展示所有策略，支持分页、筛选、搜索 |
| 左侧导航 | 分类筛选功能正常，统计数据准确 |
| 新增策略 | 5步向导流程完整，数据正确保存 |
| 编辑策略 | 向导加载已有数据，更新保存成功 |
| 删除策略 | 删除操作正确，关联数据级联删除 |
| 状态切换 | 启动/暂停/停止状态切换正常 |
| 统计信息 | 统计数据计算准确，展示正确 |

### 9.2 技术验收

| 项目 | 验收标准 |
|------|----------|
| 前端ESLint | 无校验错误 |
| 后端Schema | 输入输出严格遵循Schema定义 |
| API响应 | 统一响应格式，错误处理友好 |
| 数据库 | 表结构正确，索引有效 |
| 联调测试 | 前后端数据一致性验证通过 |

---

## 10. 附录

### 10.1 执行模式说明

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| auto | 自动交易，系统自动执行买卖 | 已验证的成熟策略，需要对接券商API |
| alert | 信号提醒，推送通知用户决策 | 需人工判断的策略，用户手动执行 |
| simulate | 模拟运行，虚拟环境测试 | 新策略验证阶段，不执行真实交易 |

### 10.2 指标类型参数说明

| 指标 | 参数 | 默认值 | 说明 |
|------|------|--------|------|
| MA | period | 20 | 均线周期 |
| | type | EMA | 均线类型：SMA/EMA |
| MACD | fast_period | 12 | 快线周期 |
| | slow_period | 26 | 慢线周期 |
| | signal_period | 9 | 信号线周期 |
| RSI | period | 14 | RSI周期 |
| KDJ | n | 9 | KDJ周期n |
| | m1 | 3 | K值平滑周期 |
| | m2 | 3 | D值平滑周期 |
| BOLL | period | 20 | 布林带周期 |
| | std_dev | 2 | 标准差倍数 |

---

**文档结束**