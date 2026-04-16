# factor-service 设计文档

## 概述

新建独立的因子分析服务，提供因子选股、技术指标计算、评分权重配置、综合评分计算和回测验证能力。

**服务定位**：
- 专注因子分析与评分计算的计算服务
- 数据来源：MCP 调用 stock-service 获取行情数据
- 数据持久化：无（由 backend/stock_policy 存储）
- 服务端口：8010

**职责边界**：
- 接收外部传入的因子/指标配置参数
- 执行计算，返回结果
- 不存储任何配置数据（配置由 backend/stock_policy 管理）

## 服务关系

```
ai-analyzer-service → factor-service → stock-service → AKShare
        │                    │
        │                    │
        ▼                    ▼
backend/stock_policy   backend/stock_policy
（存储评分配置、回测记录）  （存储技术指标定义）
```

## 目录结构

```
factor-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI + FastMCP 入口
│   ├── mcp_server.py              # FastMCP 工具注册
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理
│   │   ├── mcp_client.py          # MCP 客户端（调用 stock-service）
│   │   └── logging.py             # 日志配置
│   ├── services/
│   │   ├── __init__.py
│   │   ├── indicator_service.py   # 技术指标计算引擎
│   │   ├── factor_service.py      # 因子选股 + 评分计算
│   │   └── backtest_service.py    # 回测引擎
│   ├── models/
│   │   ├── __init__.py
│   │   ├── indicator_models.py    # 技术指标数据模型
│   │   ├── factor_models.py       # 因子选股/评分数据模型
│   │   └── backtest_models.py     # 回测数据模型
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── indicator_mcp.py       # 指标 MCP 类
│   │   ├── factor_mcp.py          # 因子 MCP 类
│   │   └── backtest_mcp.py        # 回测 MCP 类
│   └── api/
│       ├── __init__.py
│       ├── router.py              # API 路由聚合
│       └── endpoints/
│           ├── __init__.py
│           ├── indicator_routes.py # 指标 REST API
│           ├── factor_routes.py    # 因子 REST API
│           └── backtest_routes.py  # 回测 REST API
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_indicator_service.py
│   ├── test_factor_service.py
│   └── test_backtest_service.py
├── .env.example
├── README.md
├── pyproject.toml                 # 项目配置（使用 uv）
└── run.py                         # 启动脚本
```

## 核心模块设计

### 模块一：技术指标计算引擎（indicator_service.py）

**功能定位**：自建技术指标计算引擎，使用 pandas/numpy 计算。

**支持的指标类别**：

| 类别 | 指标列表 |
|------|----------|
| 趋势指标 | MA、EMA、MACD、BOLL（布林带） |
| 动量指标 | RSI、KDJ、MOM（动量）、ROC（变动率） |
| 波动指标 | ATR、STD（标准差）、VOLATILITY |
| 成交量指标 | VOL_MA、OBV、VOL_RATIO、VWAP |
| 价格指标 | HIGH/LOW、AMP（振幅）、PRICE_POSITION |

**核心方法**：

```python
class IndicatorService:
    async def calculate_indicators(
        stock_code: str,
        indicators: List[str],  # 如 ["MA5", "MA10", "RSI14", "MACD"]
        period: str = "1d",     # 周期：1d/1w/1m/5m/15m/30m/60m
        start_date: str = None,
        end_date: str = None
    ) -> Dict

    async def get_indicator_value(
        stock_code: str,
        indicator_name: str,
        date: str = None
    ) -> float

    async def batch_calculate(
        stock_codes: List[str],
        indicators: List[str],
        date: str = None
    ) -> Dict
```

**数据获取流程**：
1. 通过 MCP 调用 stock-service 获取 K 线历史数据
2. 使用 pandas/numpy 在本地计算指标值
3. 返回计算结果（不缓存，每次实时计算）

### 模块二：因子选股 + 评分计算（factor_service.py）

**功能定位**：接收用户传入的因子配置，进行选股和综合评分。

**因子类型定义**：

| 因子类型 | 说明 | 示例 |
|----------|------|------|
| 技术因子 | 基于技术指标 | MA5 > MA10、RSI14 < 30 |
| 基本因子 | 基于财务数据 | PE < 20、ROE > 15% |
| 量价因子 | 基于量价关系 | VOL_RATIO > 2、AMP > 5% |
| 组合因子 | 多指标组合 | MA5_MA10（差值）、MACD_SIGNAL |

**筛选条件格式**：

```python
factor_conditions = [
    {
        "factor_id": "RSI14",
        "operator": "lt",      # 操作符：gt/lt/ge/le/eq/between
        "value": 30            # 阈值
    },
    {
        "factor_id": "MA5_MA10",
        "operator": "gt",
        "value": 0
    }
]
```

**评分权重配置格式**：

```python
score_weights = [
    {
        "factor_id": "RSI14",
        "weight": 0.3,         # 权重 30%
        "direction": "low"     # 低值更好（逆向）
    },
    {
        "factor_id": "MA5_MA10",
        "weight": 0.2,
        "direction": "high"    # 高值更好（正向）
    },
    {
        "factor_id": "VOL_RATIO",
        "weight": 0.5,
        "direction": "high"
    }
]
```

**核心方法**：

```python
class FactorService:
    async def screen_stocks(
        conditions: List[Dict],       # 筛选条件
        stock_pool: List[str] = None, # 股票池，默认全A股
        date: str = None,
        limit: int = 50
    ) -> Dict

    async def calculate_score(
        stock_codes: List[str],
        weights: List[Dict],          # 评分权重配置
        date: str = None
    ) -> Dict

    async def get_factor_value(
        stock_code: str,
        factor_id: str,
        date: str = None
    ) -> float

    async def get_available_factors() -> List[Dict]
```

**评分计算逻辑**：
1. 计算每只股票的各因子值
2. 对每个因子进行百分位排名（0-100）
3. 根据权重和方向加权求和
4. 输出综合评分和排名列表

### 模块三：回测引擎（backtest_service.py）

**功能定位**：验证因子组合的历史表现，提供完整回测报告。

**回测类型**：

| 类型 | 说明 | 输出指标 |
|------|------|----------|
| 基础回测 | 给定因子组合和时间段的历史选股收益 | 累计收益、最大回撤、胜率、夏普比率 |
| IC 分析 | 因子值与未来收益的相关性分析 | IC 均值、ICIR、IC 显著性 |
| 分组收益 | 按因子值分组对比各组收益 | 各组收益曲线、分组差异 |
| 敏感性测试 | 不同参数组合的回测对比 | 参数敏感性矩阵 |

**核心方法**：

```python
class BacktestService:
    async def run_backtest(
        conditions: List[Dict],       # 筛选条件
        weights: List[Dict],          # 评分权重（可选）
        start_date: str,
        end_date: str,
        rebalance_freq: str = "daily", # 调仓频率：daily/weekly/monthly
        top_n: int = 10,              # 持仓数量
        benchmark: str = "000300.SH"  # 基准指数
    ) -> Dict

    async def calculate_ic(
        factor_id: str,
        start_date: str,
        end_date: str,
        forward_period: int = 5       # 预测周期（天）
    ) -> Dict

    async def group_returns(
        factor_id: str,
        start_date: str,
        end_date: str,
        num_groups: int = 5           # 分组数量
    ) -> Dict

    async def sensitivity_test(
        conditions: List[Dict],
        param_ranges: Dict,           # 参数变化范围
        start_date: str,
        end_date: str
    ) -> Dict
```

**回测报告输出格式**：

```python
{
    "summary": {
        "total_return": 25.5,        # 累计收益率 %
        "annual_return": 15.2,       # 年化收益率 %
        "max_drawdown": -8.3,        # 最大回撤 %
        "win_rate": 62.5,            # 胜率 %
        "sharpe_ratio": 1.85,        # 夏普比率
        "sortino_ratio": 2.1,        # 索提诺比率
        "benchmark_return": 10.2,    # 基准收益 %
        "excess_return": 5.0         # 超额收益 %
    },
    "daily_returns": [...],
    "positions_history": [...],
    "trade_log": [...]
}
```

**IC 分析输出格式**：

```python
{
    "factor_id": "RSI14",
    "period": "20240101-20241231",
    "ic_mean": 0.05,
    "ic_std": 0.15,
    "icir": 0.33,
    "ic_positive_ratio": 0.55,
    "ic_series": [...]
}
```

## MCP 工具定义

**indicator 模块工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `indicator_calculate` | 计算单只股票技术指标 | `stock_code`, `indicators`, `period`, `start_date`, `end_date` |
| `indicator_batch` | 批量计算多只股票指标 | `stock_codes`, `indicators`, `date` |
| `indicator_list` | 获取支持的指标列表 | 无 |

**factor 模块工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `factor_screen` | 因子选股 | `conditions`, `stock_pool`, `date`, `limit` |
| `factor_score` | 综合评分计算 | `stock_codes`, `weights`, `date` |
| `factor_value` | 获取单只股票因子值 | `stock_code`, `factor_id`, `date` |

**backtest 模块工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `backtest_run` | 执行完整回测 | `conditions`, `weights`, `start_date`, `end_date`, `rebalance_freq`, `top_n`, `benchmark` |
| `backtest_ic` | IC 分析 | `factor_id`, `start_date`, `end_date`, `forward_period` |
| `backtest_group` | 分组收益对比 | `factor_id`, `start_date`, `end_date`, `num_groups` |
| `backtest_sensitivity` | 敏感性测试 | `conditions`, `param_ranges`, `start_date`, `end_date` |

## REST API 定义

所有接口前缀 `/api/v1`。

**指标接口** `/api/v1/indicator`：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/indicator/calculate` | 计算单只股票指标 |
| POST | `/indicator/batch` | 批量计算指标 |
| GET | `/indicator/list` | 获取支持的指标列表 |

**因子接口** `/api/v1/factor`：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/factor/screen` | 因子选股 |
| POST | `/factor/score` | 综合评分计算 |
| GET | `/factor/value/{stock_code}` | 获取因子值 |

**回测接口** `/api/v1/backtest`：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/backtest/run` | 执行回测 |
| POST | `/backtest/ic` | IC 分析 |
| POST | `/backtest/group` | 分组收益对比 |
| POST | `/backtest/sensitivity` | 敏感性测试 |

## 依赖配置

**pyproject.toml**：

```toml
[project]
name = "factor-service"
version = "0.1.0"
description = "因子分析与评分计算服务"

dependencies = [
    "fastapi>=0.115.0",
    "fastmcp>=3.2.0",
    "uvicorn>=0.30.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scipy>=1.11.0",          # 用于统计计算
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.27.0",          # HTTP 客户端
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

**.env.example**：

```env
# 服务配置
SERVICE_PORT=8010
SERVICE_HOST=0.0.0.0
DEBUG=false

# stock-service MCP 地址
STOCK_SERVICE_URL=http://localhost:8008

# 日志配置
LOG_LEVEL=INFO
```

## 运行方式

1. **FastAPI + MCP 集成模式**（默认）：
   ```bash
   python run.py
   ```
   - REST API: `http://localhost:8010/api/v1/...`
   - MCP SSE: `http://localhost:8010/mcp`

2. **MCP 独立模式**（可选）：
   ```bash
   python run_mcp.py
   ```
   - MCP SSE: `http://localhost:8010/mcp`

## 测试策略

1. **指标计算测试**：验证各指标计算公式正确性
2. **因子选股测试**：验证筛选逻辑和评分计算
3. **回测测试**：使用历史数据验证回测结果准确性
4. **MCP 接口测试**：验证 MCP 工具调用正确性

## 与现有服务集成

**调用 stock-service**：
- 通过 MCP 客户端连接 stock-service
- 获取 K 线历史数据用于指标计算
- 获取实时行情数据用于评分计算

**被 backend/stock_policy 调用**：
- backend 存储评分配置后调用 factor-service 执行计算
- backend 存储回测记录后调用 factor-service 执行回测
- 计算结果返回给 backend 用于前端展示