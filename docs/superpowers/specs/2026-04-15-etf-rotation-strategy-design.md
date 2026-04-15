# 行业ETF轮动策略设计文档

**文档版本**: v1.0
**创建日期**: 2026-04-15
**作者**: Claude (Brainstorming Session)

---

## 1. 需求分析

### 1.1 业务背景

基于知乎文章《开发100个量化策略：行业ETF轮动策略（五年10倍）》实现行业ETF轮动策略。该策略通过量化方法捕捉不同行业板块的轮动机会，实现超额收益。

核心方法论：
- **斜率动量评分**: 用线性回归斜率 × R² 量化趋势稳定性，避免单纯追涨杀跌
- **RSRS择时系统**: 阻力支撑相对强度指标，解决"何时买卖"问题
- **MA过滤**: 20日均线作为二次确认，过滤假信号

### 1.2 核心需求

| 需求项 | 说明 |
|--------|------|
| **ETF池** | 9只行业ETF：科技、消费、医药、金融、军工、新能源、半导体、有色金属、基建 |
| **运行模式** | 模拟运行 + 信号提醒（不自动交易） |
| **回测功能** | 支持历史数据回测，计算收益率、最大回撤、胜率、夏普比率等指标 |
| **择时系统** | RSRS指标 + MA20过滤，判断买卖时机 |
| **评分系统** | 斜率动量评分，对ETF池进行排名选择 |
| **轮动逻辑** | 每周/每月调仓，持有评分最高的1-2只ETF |
| **信号通知** | 生成调仓信号时推送通知 |

### 1.3 策略参数配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 斜率计算周期 | 20日 | 线性回归窗口 |
| RSRS窗口 | 18日 | 最高价/最低价回归窗口 |
| RSRS买入阈值 | 0.7 | Z-score > 0.7 触发买入信号 |
| RSRS卖出阈值 | -0.7 | Z-score < -0.7 触发卖出信号 |
| MA周期 | 20日 | 均线过滤周期 |
| 持仓数量 | 1-2只 | 同时持有的ETF数量 |
| 调仓频率 | 每周一 | 定期评估调仓 |

---

## 2. 算法原理

### 2.1 斜率动量评分

**目的**: 量化趋势的稳定性和强度

**计算方法**:
```
1. 取N日收盘价序列 [p1, p2, ..., pN]
2. 对时间序列做线性回归: y = ax + b
3. 计算斜率 a 和 R² (拟合优度)
4. 动量评分 = a × R² × 10000
```

**意义**:
- 斜率 a 反映趋势方向和强度（正为上涨，负为下跌）
- R² 反映趋势的稳定性和可信度（越接近1越稳定）
- 乘积放大稳定上涨趋势的得分，过滤不稳定波动

### 2.2 RSRS择时指标

**目的**: 判断当前价格相对于阻力支撑的位置

**计算方法**:
```
1. 取N日最高价序列 [h1, h2, ..., hN] 和最低价序列 [l1, l2, ..., lN]
2. 对 (low, high) 做线性回归: high = β × low + α
3. 计算斜率 β（阻力支撑相对强度）
4. 对 β 做M日Z-score标准化:
   Z = (β - mean(β_M)) / std(β_M)
```

**信号判断**:
- Z > 0.7: 当前价格突破阻力区，买入信号
- Z < -0.7: 当前价格跌破支撑区，卖出信号
- -0.7 ≤ Z ≤ 0.7: 中性区间，不操作

### 2.3 MA过滤

**目的**: 二次确认，避免假突破

**规则**:
- 买入确认: 收盘价 > MA20
- 卖出确认: 收盘价 < MA20

### 2.4 轮动决策流程

```
每周一执行:
1. 对ETF池中所有ETF计算斜率动量评分
2. 按评分降序排名
3. 检查RSRS信号：
   - 若持仓ETF的RSRS Z < -0.7 且 收盘价 < MA20 → 卖出
   - 若候选ETF的RSRS Z > 0.7 且 收盘价 > MA20 → 可买入
4. 选择评分最高且满足买入条件的ETF
5. 生成调仓信号（信号提醒模式）
```

---

## 3. 数据库设计

### 3.1 表结构设计

#### 3.1.1 ETF池配置表 (t_etf_pool)

```sql
CREATE TABLE t_etf_pool (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT 'ETF名称',
    code VARCHAR(20) NOT NULL COMMENT 'ETF代码',
    sector VARCHAR(50) NOT NULL COMMENT '所属行业板块',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_code (code),
    INDEX idx_sector (sector)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF池配置表';
```

**预设ETF池数据**:
| 名称 | 代码 | 行业板块 |
|------|------|----------|
| 科技ETF | 515000 | 科技 |
| 消费ETF | 159928 | 消费 |
| 医药ETF | 159929 | 医药 |
| 金融ETF | 159931 | 金融 |
| 军工ETF | 512660 | 军工 |
| 新能源ETF | 516160 | 新能源 |
| 半导体ETF | 512480 | 半导体 |
| 有色ETF | 512400 | 有色金属 |
| 基建ETF | 159766 | 基建 |

#### 3.1.2 轮动策略配置表 (t_rotation_strategy)

```sql
CREATE TABLE t_rotation_strategy (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT '策略名称',
    description VARCHAR(500) COMMENT '策略描述',
    slope_period INT DEFAULT 20 COMMENT '斜率计算周期',
    rsrs_period INT DEFAULT 18 COMMENT 'RSRS窗口周期',
    rsrs_z_window INT DEFAULT 100 COMMENT 'Z-score标准化窗口',
    rsrs_buy_threshold DECIMAL(10,4) DEFAULT 0.7 COMMENT 'RSRS买入阈值',
    rsrs_sell_threshold DECIMAL(10,4) DEFAULT -0.7 COMMENT 'RSRS卖出阈值',
    ma_period INT DEFAULT 20 COMMENT 'MA过滤周期',
    hold_count INT DEFAULT 2 COMMENT '持仓数量',
    rebalance_freq VARCHAR(20) DEFAULT 'weekly' COMMENT '调仓频率: daily/weekly/monthly',
    execute_mode VARCHAR(20) DEFAULT 'simulate' COMMENT '执行模式: simulate/alert',
    status VARCHAR(20) DEFAULT 'paused' COMMENT '状态: running/paused/stopped',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮动策略配置表';
```

#### 3.1.3 ETF评分记录表 (t_etf_score)

```sql
CREATE TABLE t_etf_score (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    etf_code VARCHAR(20) NOT NULL COMMENT 'ETF代码',
    trade_date DATE NOT NULL COMMENT '交易日期',
    slope_value DECIMAL(10,6) COMMENT '斜率值',
    r_squared DECIMAL(10,6) COMMENT 'R²值',
    momentum_score DECIMAL(10,4) COMMENT '动量评分',
    rsrs_beta DECIMAL(10,6) COMMENT 'RSRS斜率β',
    rsrs_z_score DECIMAL(10,6) COMMENT 'RSRS Z-score',
    ma_value DECIMAL(10,4) COMMENT 'MA值',
    close_price DECIMAL(10,4) COMMENT '收盘价',
    rank_position INT COMMENT '排名位置',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_rotation_strategy(id) ON DELETE CASCADE,
    UNIQUE KEY uk_strategy_date_code (strategy_id, trade_date, etf_code),
    INDEX idx_trade_date (trade_date),
    INDEX idx_etf_code (etf_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ETF评分记录表';
```

#### 3.1.4 轮动信号记录表 (t_rotation_signal)

```sql
CREATE TABLE t_rotation_signal (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    signal_date DATE NOT NULL COMMENT '信号日期',
    signal_type VARCHAR(20) NOT NULL COMMENT '信号类型: buy/sell/rebalance',
    etf_code VARCHAR(20) NOT NULL COMMENT 'ETF代码',
    etf_name VARCHAR(100) COMMENT 'ETF名称',
    action VARCHAR(20) NOT NULL COMMENT '操作动作: buy/sell/hold',
    score DECIMAL(10,4) COMMENT '动量评分',
    rsrs_z DECIMAL(10,6) COMMENT 'RSRS Z-score',
    price DECIMAL(10,4) COMMENT '参考价格',
    reason VARCHAR(500) COMMENT '信号原因',
    is_executed TINYINT(1) DEFAULT 0 COMMENT '是否已执行',
    executed_at DATETIME COMMENT '执行时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_rotation_strategy(id) ON DELETE CASCADE,
    INDEX idx_signal_date (signal_date),
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮动信号记录表';
```

#### 3.1.5 轮动持仓记录表 (t_rotation_position)

```sql
CREATE TABLE t_rotation_position (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    etf_code VARCHAR(20) NOT NULL COMMENT 'ETF代码',
    etf_name VARCHAR(100) COMMENT 'ETF名称',
    buy_date DATE NOT NULL COMMENT '买入日期',
    buy_price DECIMAL(10,4) COMMENT '买入价格',
    buy_score DECIMAL(10,4) COMMENT '买入时评分',
    quantity INT COMMENT '持仓数量（股）',
    cost_amount DECIMAL(12,2) COMMENT '成本金额',
    current_price DECIMAL(10,4) COMMENT '当前价格',
    current_value DECIMAL(12,2) COMMENT '当前市值',
    profit_pct DECIMAL(10,4) COMMENT '盈亏百分比',
    hold_days INT COMMENT '持有天数',
    status VARCHAR(20) DEFAULT 'holding' COMMENT '状态: holding/sold',
    sell_date DATE COMMENT '卖出日期',
    sell_price DECIMAL(10,4) COMMENT '卖出价格',
    sell_reason VARCHAR(200) COMMENT '卖出原因',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (strategy_id) REFERENCES t_rotation_strategy(id) ON DELETE CASCADE,
    INDEX idx_strategy_id (strategy_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轮动持仓记录表';
```

#### 3.1.6 回测记录表 (t_rotation_backtest)

```sql
CREATE TABLE t_rotation_backtest (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    start_date DATE NOT NULL COMMENT '回测开始日期',
    end_date DATE NOT NULL COMMENT '回测结束日期',
    initial_capital DECIMAL(12,2) COMMENT '初始资金',
    final_capital DECIMAL(12,2) COMMENT '最终资金',
    total_return DECIMAL(10,4) COMMENT '总收益率',
    annual_return DECIMAL(10,4) COMMENT '年化收益率',
    max_drawdown DECIMAL(10,4) COMMENT '最大回撤',
    win_rate DECIMAL(10,4) COMMENT '胜率',
    trade_count INT COMMENT '交易次数',
    sharpe_ratio DECIMAL(10,4) COMMENT '夏普比率',
    calmar_ratio DECIMAL(10,4) COMMENT '卡尔马比率',
    benchmark_return DECIMAL(10,4) COMMENT '基准收益率',
    excess_return DECIMAL(10,4) COMMENT '超额收益',
    backtest_details JSON COMMENT '回测详细数据',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (strategy_id) REFERENCES t_rotation_strategy(id) ON DELETE CASCADE,
    INDEX idx_strategy_id (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测记录表';
```

### 3.2 ER关系图

```
t_rotation_strategy (策略配置主表)
    │
    ├── t_etf_score (1:N)
    │   每日ETF评分记录
    │
    ├── t_rotation_signal (1:N)
    │   调仓信号记录
    │
    ├── t_rotation_position (1:N)
    │   模拟持仓记录
    │
    └── t_rotation_backtest (1:N)
        多次回测记录

t_etf_pool (ETF池配置)
    │
    └── 被t_etf_score/t_rotation_signal/t_rotation_position引用
```

---

## 4. 接口设计

### 4.1 接口列表

#### 4.1.1 ETF池管理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/etf-pool` | GET | 获取ETF池列表 |
| `/api/v1/etf-pool` | POST | 添加ETF到池中 |
| `/api/v1/etf-pool/{id}` | PUT | 更新ETF配置 |
| `/api/v1/etf-pool/{id}` | DELETE | 从池中移除ETF |

#### 4.1.2 轮动策略接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/rotation-strategies` | GET | 获取轮动策略列表 |
| `/api/v1/rotation-strategies/{id}` | GET | 获取策略详情 |
| `/api/v1/rotation-strategies` | POST | 创建轮动策略 |
| `/api/v1/rotation-strategies/{id}` | PUT | 更新策略参数 |
| `/api/v1/rotation-strategies/{id}` | DELETE | 删除策略 |
| `/api/v1/rotation-strategies/{id}/status` | PUT | 启动/暂停策略 |

#### 4.1.3 评分与信号接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/rotation-strategies/{id}/scores` | GET | 获取ETF评分排名 |
| `/api/v1/rotation-strategies/{id}/scores/latest` | GET | 获取最新评分 |
| `/api/v1/rotation-strategies/{id}/signals` | GET | 获取信号记录 |
| `/api/v1/rotation-strategies/{id}/signals/generate` | POST | 手动触发信号生成 |

#### 4.1.4 模拟持仓接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/rotation-strategies/{id}/positions` | GET | 获取当前持仓 |
| `/api/v1/rotation-strategies/{id}/positions/history` | GET | 获取历史持仓 |
| `/api/v1/rotation-strategies/{id}/positions/performance` | GET | 获取持仓收益分析 |

#### 4.1.5 回测接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/rotation-strategies/{id}/backtest` | POST | 运行回测 |
| `/api/v1/rotation-strategies/{id}/backtest/results` | GET | 获取回测结果列表 |
| `/api/v1/rotation-strategies/{id}/backtest/{bid}` | GET | 获取回测详情 |
| `/api/v1/rotation-strategies/{id}/backtest/{bid}/curve` | GET | 获取收益曲线数据 |

### 4.2 接口详细定义

#### 4.2.1 创建轮动策略

**POST `/api/v1/rotation-strategies`**

Request Body:
```json
{
    "name": "行业ETF轮动策略V1",
    "description": "基于斜率动量+RSRS的行业ETF轮动策略",
    "slope_period": 20,
    "rsrs_period": 18,
    "rsrs_z_window": 100,
    "rsrs_buy_threshold": 0.7,
    "rsrs_sell_threshold": -0.7,
    "ma_period": 20,
    "hold_count": 2,
    "rebalance_freq": "weekly",
    "execute_mode": "simulate"
}
```

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "行业ETF轮动策略V1",
        "status": "paused",
        "created_at": "2026-04-15T10:00:00"
    }
}
```

#### 4.2.2 获取ETF评分排名

**GET `/api/v1/rotation-strategies/{id}/scores/latest`**

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "trade_date": "2026-04-15",
        "scores": [
            {
                "etf_code": "515000",
                "etf_name": "科技ETF",
                "momentum_score": 85.32,
                "slope_value": 0.0125,
                "r_squared": 0.92,
                "rsrs_z_score": 0.85,
                "ma_value": 1.25,
                "close_price": 1.28,
                "rank": 1,
                "signal": "buy_candidate"
            },
            {
                "etf_code": "512480",
                "etf_name": "半导体ETF",
                "momentum_score": 72.15,
                "slope_value": 0.0098,
                "r_squared": 0.88,
                "rsrs_z_score": 0.65,
                "ma_value": 2.10,
                "close_price": 2.15,
                "rank": 2,
                "signal": "hold"
            }
        ],
        "current_holdings": [
            {
                "etf_code": "512480",
                "etf_name": "半导体ETF",
                "rsrs_z_score": 0.65,
                "close_price": 2.15,
                "ma_value": 2.10,
                "signal": "hold"
            }
        ]
    }
}
```

#### 4.2.3 运行回测

**POST `/api/v1/rotation-strategies/{id}/backtest`**

Request Body:
```json
{
    "start_date": "2021-01-01",
    "end_date": "2025-12-31",
    "initial_capital": 100000
}
```

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "backtest_id": 1,
        "status": "running",
        "estimated_time": "约2分钟"
    }
}
```

#### 4.2.4 获取回测结果

**GET `/api/v1/rotation-strategies/{id}/backtest/{bid}`**

Response:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "start_date": "2021-01-01",
        "end_date": "2025-12-31",
        "initial_capital": 100000,
        "final_capital": 250000,
        "total_return": 150.0,
        "annual_return": 20.0,
        "max_drawdown": 15.5,
        "win_rate": 65.0,
        "trade_count": 120,
        "sharpe_ratio": 1.85,
        "calmar_ratio": 1.29,
        "benchmark_return": 50.0,
        "excess_return": 100.0,
        "created_at": "2026-04-15T10:05:00"
    }
}
```

---

## 5. 项目结构

### 5.1 后端项目结构

```
backend/
├── models/
│   ├── etf_pool.py              # ETF池模型
│   ├── rotation_strategy.py     # 轮动策略模型
│   ├── etf_score.py             # ETF评分模型
│   ├── rotation_signal.py       # 轮动信号模型
│   ├── rotation_position.py     # 持仓模型
│   └── rotation_backtest.py     # 回测模型
│
├── utils/
│   ├── rotation_calculator/
│   │   ├── __init__.py
│   │   ├── slope_momentum.py    # 斜率动量计算
│   │   ├── rsrs.py              # RSRS指标计算
│   │   └── ma_filter.py         # MA过滤
│   └── backtest_engine.py       # 通用回测引擎
│
├── services/
│   ├── kline_service.py         # K线数据服务（需实现真实数据）
│   ├── etf_rotation.py          # 轮动策略核心服务
│   └── rotation_scheduler.py    # 定时任务调度
│
├── schemas/
│   ├── etf_pool.py              # ETF池Schema
│   ├── rotation_strategy.py     # 轮动策略Schema
│   └── rotation_backtest.py     # 回测Schema
│
├── api/v1/
│   ├── etf_pool.py              # ETF池API
│   └── etf_rotation.py          # 轮动策略API
│
└── scripts/
    └── init_etf_pool.py         # ETF池初始化脚本
```

### 5.2 前端项目结构

```
frontend/src/
├── views/
│   └── etf-rotation/
│       ├── index.vue            # 轮动策略主页面
│       ├── etf-pool.vue         # ETF池配置
│       ├── signals.vue          # 信号记录
│       ├── positions.vue        # 持仓监控
│       └── backtest.vue         # 回测配置与结果
│
├── components/
│   ├── etf-rotation/
│   │   ├── ScoreRanking.vue     # 评分排名组件
│   │   ├── SignalCard.vue       # 信号卡片
│   │   ├── PositionTable.vue    # 持仓表格
│   │   ├── BacktestResult.vue   # 回测结果展示
│   │   └── ReturnCurve.vue      # 收益曲线图
│   └── RotationStrategyForm.vue # 策略配置表单
│
├── api/
│   ├── etfPool.ts               # ETF池API
│   ├── etfRotation.ts           # 轮动策略API
│   └── rotationBacktest.ts      # 回测API
│
├── types/
│   └── etfRotation.ts           # TypeScript类型定义
│
└── stores/
    └── etfRotation.ts           # Pinia状态管理
```

---

## 6. 页面设计

### 6.1 主页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  ETF轮动策略监控                                              │
│  [新建策略] [ETF池配置]                  [策略选择下拉]       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────┐  ┌─────────────────────────────┐│
│  │ 当前持仓              │  │ 今日评分排名                  ││
│  │                       │  │                              ││
│  │ 半导体ETF 512480      │  │ 排名  ETF      评分   信号    ││
│  │ 持有5天  +3.2%        │  │ 1    科技ETF   85.32  买入候选 ││
│  │ 收盘: 2.15            │  │ 2    半导体ETF 72.15  持有     ││
│  │                       │  │ 3    新能源ETF 68.50  观察     ││
│  │ 新能源ETF 516160      │  │ ...                          ││
│  │ 持有3天  +1.5%        │  │                              ││
│  └───────────────────────┘  └─────────────────────────────┘│
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 策略表现                                               │ │
│  │ 总收益: +15.2%  最大回撤: -8.5%  夏普: 1.2  交易: 45次 │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 最新信号                                               │ │
│  │ 2026-04-15  建议: 半导体ETF → 科技ETF                   │ │
│  │ 原因: 科技ETF评分升至第1,RSRS=0.85>0.7,突破MA20        │ │
│  │ [执行调仓] [忽略]                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  [回测分析] [信号历史] [持仓历史]                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 回测页面布局

```
┌─────────────────────────────────────────────────────────────┐
│  回测配置                                                     │
│  开始日期: [2021-01-01]  结束日期: [2025-12-31]              │
│  初始资金: [100000]    [运行回测]                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 收益曲线                                               │ │
│  │ [ECharts图表: 策略收益 vs 基准收益]                      │ │
│  │                                                        │ │
│  │                                                        │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 回测指标                                               │ │
│  │ 总收益    年化收益   最大回撤  胜率   夏普   卡尔马     │ │
│  │ +150%    +20%      -15.5%   65%   1.85   1.29        │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 交易记录                                               │ │
│  │ 日期      操作   ETF      价格    收益   原因           │ │
│  │ 2021-02-01 买入   科技ETF  1.20    -     RSRS突破      │ │
│  │ 2021-03-15 卖出   科技ETF  1.35    +12.5% RSRS跌破    │ │
│  │ ...                                                    │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 核心算法实现

### 7.1 斜率动量计算 (slope_momentum.py)

```python
"""
斜率动量评分计算
"""
import numpy as np
from typing import List, Dict
from scipy import stats


class SlopeMomentumCalculator:
    """斜率动量评分计算器"""

    def __init__(self, period: int = 20):
        self.period = period

    def calculate(self, closes: List[float]) -> Dict:
        """
        计算斜率动量评分

        Args:
            closes: 收盘价序列

        Returns:
            {
                'slope': 斜率值,
                'r_squared': R²拟合优度,
                'score': 动量评分 = slope * r_squared * 10000
            }
        """
        if len(closes) < self.period:
            return {'slope': None, 'r_squared': None, 'score': None}

        # 取最近N日收盘价
        y = np.array(closes[-self.period:])
        x = np.arange(self.period)

        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared = r_value ** 2

        # 动量评分
        score = slope * r_squared * 10000

        return {
            'slope': round(slope, 6),
            'r_squared': round(r_squared, 6),
            'score': round(score, 4)
        }
```

### 7.2 RSRS指标计算 (rsrs.py)

```python
"""
RSRS择时指标计算
"""
import numpy as np
from typing import List, Dict
from scipy import stats


class RSRSCalculator:
    """RSRS择时指标计算器"""

    def __init__(self, period: int = 18, z_window: int = 100):
        self.period = period      # 回归窗口
        self.z_window = z_window  # Z-score标准化窗口

    def calculate(
        self,
        highs: List[float],
        lows: List[float],
        beta_history: List[float] = None
    ) -> Dict:
        """
        计算RSRS指标

        Args:
            highs: 最高价序列
            lows: 最低价序列
            beta_history: 历史beta序列（用于Z-score计算）

        Returns:
            {
                'beta': 当期斜率β,
                'z_score': Z-score标准化值,
                'signal': buy/sell/neutral
            }
        """
        if len(highs) < self.period or len(lows) < self.period:
            return {'beta': None, 'z_score': None, 'signal': 'neutral'}

        # 取最近N日数据
        h = np.array(highs[-self.period:])
        l = np.array(lows[-self.period:])

        # 线性回归: high = beta * low + alpha
        beta, alpha, r_value, p_value, std_err = stats.linregress(l, h)

        # Z-score标准化
        if beta_history and len(beta_history) >= self.z_window:
            recent_betas = beta_history[-self.z_window:]
            mean_beta = np.mean(recent_betas)
            std_beta = np.std(recent_betas)
            z_score = (beta - mean_beta) / std_beta if std_beta > 0 else 0
        else:
            z_score = 0  # 数据不足时为中性

        # 信号判断
        if z_score > 0.7:
            signal = 'buy'
        elif z_score < -0.7:
            signal = 'sell'
        else:
            signal = 'neutral'

        return {
            'beta': round(beta, 6),
            'z_score': round(z_score, 6),
            'signal': signal
        }
```

### 7.3 轮动服务核心逻辑 (etf_rotation.py)

```python
"""
ETF轮动策略核心服务
"""
from typing import List, Dict, Optional
from datetime import datetime, date
from loguru import logger

from services.kline_service import kline_service
from utils.rotation_calculator.slope_momentum import SlopeMomentumCalculator
from utils.rotation_calculator.rsrs import RSRSCalculator
from utils.rotation_calculator.ma_filter import MAFilter
from models.rotation_strategy import RotationStrategy
from models.etf_pool import EtfPool
from models.etf_score import EtfScore
from models.rotation_signal import RotationSignal
from models.rotation_position import RotationPosition


class EtfRotationService:
    """ETF轮动策略服务"""

    async def calculate_scores(
        self,
        strategy: RotationStrategy,
        trade_date: date
    ) -> List[EtfScore]:
        """
        计算ETF池所有ETF的评分

        Returns:
            按评分降序排列的ETF评分列表
        """
        # 获取ETF池
        etf_pool = await EtfPool.filter(is_active=True).all()

        scores = []
        slope_calc = SlopeMomentumCalculator(strategy.slope_period)
        rsrs_calc = RSRSCalculator(strategy.rsrs_period, strategy.rsrs_z_window)
        ma_filter = MAFilter(strategy.ma_period)

        for etf in etf_pool:
            # 获取K线数据
            klines = await kline_service.get_klines(
                etf.code,
                limit=max(strategy.slope_period, strategy.rsrs_period, strategy.rsrs_z_window) + 10
            )

            closes = klines['close']
            highs = klines['high']
            lows = klines['low']

            # 计算各指标
            momentum = slope_calc.calculate(closes)
            rsrs = rsrs_calc.calculate(highs, lows)
            ma_val = ma_filter.calculate(closes)

            score = EtfScore(
                strategy_id=strategy.id,
                etf_code=etf.code,
                trade_date=trade_date,
                slope_value=momentum['slope'],
                r_squared=momentum['r_squared'],
                momentum_score=momentum['score'],
                rsrs_beta=rsrs['beta'],
                rsrs_z_score=rsrs['z_score'],
                ma_value=ma_val,
                close_price=closes[-1]
            )
            scores.append(score)

        # 按评分排序
        scores.sort(key=lambda x: x.momentum_score or 0, reverse=True)

        # 设置排名
        for i, score in enumerate(scores):
            score.rank_position = i + 1

        return scores

    async def generate_signals(
        self,
        strategy: RotationStrategy,
        scores: List[EtfScore]
    ) -> List[RotationSignal]:
        """
        根据评分和RSRS信号生成调仓建议
        """
        signals = []
        trade_date = scores[0].trade_date if scores else date.today()

        # 获取当前持仓
        holdings = await RotationPosition.filter(
            strategy_id=strategy.id,
            status='holding'
        ).all()

        # 检查卖出信号
        for holding in holdings:
            score = next((s for s in scores if s.etf_code == holding.etf_code), None)
            if score:
                # RSRS跌破阈值 + MA过滤确认
                if score.rsrs_z_score < strategy.rsrs_sell_threshold and \
                   score.close_price < score.ma_value:
                    signal = RotationSignal(
                        strategy_id=strategy.id,
                        signal_date=trade_date,
                        signal_type='sell',
                        etf_code=holding.etf_code,
                        etf_name=holding.etf_name,
                        action='sell',
                        score=score.momentum_score,
                        rsrs_z=score.rsrs_z_score,
                        price=score.close_price,
                        reason=f"RSRS Z={score.rsrs_z_score:.2f}<{strategy.rsrs_sell_threshold}, "
                               f"收盘{score.close_price}<MA{strategy.ma_period}={score.ma_value:.2f}"
                    )
                    signals.append(signal)

        # 检查买入信号
        buy_candidates = []
        for score in scores[:strategy.hold_count + 2]:  # 多看几个候选
            # RSRS突破阈值 + MA过滤确认
            if score.rsrs_z_score > strategy.rsrs_buy_threshold and \
               score.close_price > score.ma_value:
                # 不在持仓中
                if not any(h.etf_code == score.etf_code for h in holdings):
                    buy_candidates.append(score)

        # 按评分选择买入候选
        for score in buy_candidates[:strategy.hold_count - len(holdings) + len([s for s in signals if s.action == 'sell'])]:
            etf = await EtfPool.filter(code=score.etf_code).first()
            signal = RotationSignal(
                strategy_id=strategy.id,
                signal_date=trade_date,
                signal_type='buy',
                etf_code=score.etf_code,
                etf_name=etf.name if etf else '',
                action='buy',
                score=score.momentum_score,
                rsrs_z=score.rsrs_z_score,
                price=score.close_price,
                reason=f"评分排名#{score.rank_position}, "
                       f"RSRS Z={score.rsrs_z_score:.2f}>{strategy.rsrs_buy_threshold}, "
                       f"收盘{score.close_price}>MA{strategy.ma_period}={score.ma_value:.2f}"
            )
            signals.append(signal)

        return signals
```

---

## 8. 开发计划

### 8.1 实施阶段

| 阶段 | 任务 | 输出物 |
|------|------|--------|
| **Phase 1** | 核心算法实现 | |
| Day 1-2 | 数据库表创建 | 6张核心表 |
| | ORM模型编写 | models/*.py |
| | ETF池初始化 | 预设9只ETF |
| Day 3-4 | 指标计算器开发 | rotation_calculator/*.py |
| | K线服务对接 | kline_service.py改造 |
| Day 5-6 | 轮动服务开发 | etf_rotation.py |
| | 信号生成逻辑 | generate_signals() |
| | 后端API开发 | api/v1/etf_rotation.py |
| **Phase 2** | 前端页面开发 | |
| Day 7-8 | 轮动监控页面 | views/etf-rotation/index.vue |
| | ETF池配置页面 | views/etf-rotation/etf-pool.vue |
| | 评分排名组件 | ScoreRanking.vue |
| Day 9-10 | 回测页面 | views/etf-rotation/backtest.vue |
| | 收益曲线图 | ReturnCurve.vue |
| **Phase 3** | 回测引擎开发 | |
| Day 11-12 | 回测引擎核心 | backtest_engine.py |
| | 指标计算优化 | 性能优化 |
| Day 13-14 | 历史数据导入 | K线数据准备 |
| | 回测验证 | 验证结果准确性 |
| **Phase 4** | 联调与测试 | |
| Day 15 | 前后端联调 | - |
| Day 16 | 功能测试 | - |
| Day 17 | Bug修复 | - |

---

## 9. 验收标准

### 9.1 功能验收

| 功能点 | 验收标准 |
|--------|----------|
| ETF池管理 | 可添加/删除/启用/禁用ETF |
| 策略配置 | 参数可配置，保存后生效 |
| 评分计算 | 斜率、R²、RSRS计算准确 |
| 信号生成 | 符合策略规则的信号正确生成 |
| 模拟持仓 | 持仓记录准确，收益计算正确 |
| 回测引擎 | 回测结果可复现，指标计算准确 |
| 收益曲线 | 曲线展示清晰，对比基准 |

### 9.2 技术验收

| 项目 | 验收标准 |
|------|----------|
| 算法正确性 | 斜率/R²/RSRS计算结果与Python scipy一致 |
| 数据完整性 | K线数据无缺失，评分记录完整 |
| API规范 | 统一响应格式，错误处理友好 |
| 前端ESLint | 无校验错误 |
| 性能 | 评分计算<1秒，回测<5分钟（5年数据） |

---

## 10. 风险与限制

### 10.1 数据依赖

- **K线数据源**: 当前kline_service返回模拟数据，需对接真实行情API（如东方财富、AKShare）
- **历史数据完整性**: 回测需要完整的历史K线数据

### 10.2 算法限制

- **RSRS参数敏感性**: 不同参数组合效果差异较大，需要调优
- **趋势行情适用性**: 斜率动量在震荡市可能表现不佳
- **轮动频率**: 过高频调仓增加交易成本

### 10.3 模拟模式限制

- **交易成本**: 模拟未考虑佣金、滑点
- **流动性**: 模拟未考虑ETF流动性限制
- **执行时效**: 实际执行可能无法按信号价格成交

---

**文档结束**