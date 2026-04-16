# ai-analyzer-service 设计文档

## 概述

新建独立的 AI 智能分析服务，提供趋势分析、风险评估、投资建议等 AI 驱动的分析能力。

**服务定位**：
- 专注 AI 智能分析的计算服务
- 数据来源：MCP 调用 factor-service 获取评分和回测数据
- 数据持久化：无（由 backend/stock_policy 存储）
- 服务端口：8011

**职责边界**：
- 接收分析请求和上下文数据
- 调用 AI 模型生成分析结果
- 不存储任何配置数据（配置由 backend/stock_policy 管理）

## 服务关系

```
┌─────────────────────────────────────────────────────────────────────┐
│                        stock_policy 系统架构                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   frontend (Vue) ← 用户交互界面                                       │
│         │                                                            │
│         ▼                                                            │
│   backend (FastAPI) ← 主服务，数据持久化                               │
│         │                                                            │
│         ▼                                                            │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                    微服务层 (MCP 调用)                          │  │
│   ├──────────────────────────────────────────────────────────────┤  │
│   │                                                                │  │
│   │  stock-service (8008)     qmt-service (8009)                  │  │
│   │  - 行情数据               - 交易执行                           │  │
│   │  - 个股信息               - 持仓管理                           │  │
│   │  - 板块数据               - 实时行情(L2)                       │  │
│   │                                                                │  │
│   │  factor-service (8010)    ai-analyzer-service (8011) ← 本服务  │  │
│   │  - 因子选股               - AI 智能分析                        │  │
│   │  - 指标计算               - 趋势分析                           │  │
│   │  - 评分计算               - 风险评估                           │  │
│   │  - 回测验证               - 投资建议                           │  │
│   │                                                                │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**调用链**：
```
ai-analyzer-service → factor-service → stock-service
```

## 目录结构

```
ai-analyzer-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI + FastMCP 入口
│   ├── mcp_server.py              # FastMCP 工具注册
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理
│   │   ├── mcp_client.py          # MCP 客户端（调用 factor-service）
│   │   ├── logging.py             # 日志配置
│   │   └── ai_provider.py         # AI 模型适配器管理
│   │   └ providers/
│   │       ├── __init__.py
│   │       ├── base_provider.py   # 基础 Provider 抽象类
│   │       ├── claude_provider.py # Claude API 实现
│   │       ├── openai_provider.py # OpenAI API 实现
│   │       └── ollama_provider.py # Ollama 本地模型实现
│   ├── services/
│   │   ├── __init__.py
│   │   ├── trend_service.py       # 趋势分析
│   │   ├── risk_service.py        # 风险评估
│   │   ├── advice_service.py      # 投资建议
│   │   └── model_service.py       # 模型管理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trend_models.py        # 趋势分析数据模型
│   │   ├── risk_models.py         # 风险评估数据模型
│   │   ├── advice_models.py       # 投资建议数据模型
│   │   └── model_models.py        # 模型管理数据模型
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── trend_mcp.py           # 趋势分析 MCP 类
│   │   ├── risk_mcp.py            # 风险评估 MCP 类
│   │   ├── advice_mcp.py          # 投资建议 MCP 类
│   │   └── model_mcp.py           # 模型管理 MCP 类
│   └── api/
│       ├── __init__.py
│       ├── router.py              # API 路由聚合
│       └── endpoints/
│           ├── __init__.py
│           ├── trend_routes.py    # 趋势分析 REST API
│           ├── risk_routes.py     # 风险评估 REST API
│           ├── advice_routes.py   # 投资建议 REST API
│           └── model_routes.py    # 模型管理 REST API
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_trend_service.py
│   ├── test_risk_service.py
│   ├── test_advice_service.py
│   ├── test_model_service.py
│   └── test_providers/
│       ├── __init__.py
│       ├── test_claude_provider.py
│       ├── test_openai_provider.py
│       └── test_ollama_provider.py
├── .env.example
├── README.md
├── pyproject.toml
└── run.py
```

## 核心模块设计

### 模块一：AI 模型适配器（ai_provider.py + providers/）

**功能定位**：统一的多模型接口，支持 Claude/OpenAI/Ollama 切换。

**Provider 抽象接口**：

```python
class BaseAIProvider:
    """AI Provider 基础抽象类"""

    async def analyze(
        prompt: str,
        context: Dict,           # 分析上下文（股票数据、指标、评分等）
        model: str = None,       # 模型名称（可选，使用默认）
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str  # 返回分析结果文本

    async def stream_analyze(
        prompt: str,
        context: Dict,
        model: str = None
    ) -> AsyncGenerator[str, None]  # 流式返回

    def get_model_list(self) -> List[str]  # 获取支持的模型列表

    def is_available(self) -> bool  # 检查服务是否可用
```

**各 Provider 实现**：

| Provider | 支持的模型 | 配置项 |
|----------|-----------|--------|
| ClaudeProvider | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` |
| OpenAIProvider | gpt-4o, gpt-4o-mini, gpt-4-turbo | `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| OllamaProvider | 本地部署模型（如 llama3, qwen2） | `OLLAMA_HOST`, `OLLAMA_MODEL` |

**配置文件示例**（.env）：

```env
# 默认使用的 Provider
AI_PROVIDER=claude

# Claude 配置
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# OpenAI 配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Ollama 配置
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2:7b
```

### 模块二：趋势分析服务（trend_service.py）

**功能定位**：结合评分和指标数据，分析股票趋势。

**核心方法**：

```python
class TrendService:
    async def analyze_trend(
        stock_code: str,
        analysis_type: str = "comprehensive",  # comprehensive/short_term/mid_term/long_term
        include_indicators: List[str] = None,
        model: str = None
    ) -> Dict

    async def batch_analyze_trends(
        stock_codes: List[str],
        analysis_type: str = "comprehensive",
        model: str = None
    ) -> Dict
```

**趋势分析输出格式**：

```python
{
    "stock_code": "000001.SZ",
    "stock_name": "平安银行",
    "analysis_date": "2026-04-16",
    "trend_direction": "upward",           # 趋势方向：upward/downward/sideways
    "trend_strength": 0.75,                 # 趋势强度 0-1
    "confidence": 0.85,                     # 分析置信度

    "key_indicators": {
        "MA5": {"value": 12.5, "signal": "支撑"},
        "MA20": {"value": 11.8, "signal": "支撑"},
        "RSI14": {"value": 65, "signal": "中性"},
        "MACD": {"value": 0.15, "signal": "金叉"}
    },

    "score_summary": {
        "composite_score": 78.5,            # 综合评分（来自 factor-service）
        "rank": 15
    },

    "analysis_text": "该股当前处于上升趋势...",  # AI 生成的分析文本

    "key_points": [
        "股价站上5日均线，短期趋势向上",
        "RSI处于中性区域，未超买超卖",
        "MACD金叉确认，动能增强"
    ],

    "warnings": ["成交量有所萎缩，需关注"]
}
```

### 模块三：风险评估服务（risk_service.py）

**功能定位**：基于回测数据和波动性，评估投资风险。

**核心方法**：

```python
class RiskService:
    async def assess_risk(
        stock_code: str,
        assessment_type: str = "comprehensive",  # comprehensive/volatility/drawdown/liquidity
        model: str = None
    ) -> Dict

    async def portfolio_risk(
        stock_codes: List[str],
        weights: List[float] = None,
        model: str = None
    ) -> Dict  # 组合风险评估

    async def compare_risk(
        stock_codes: List[str],
        model: str = None
    ) -> Dict  # 多只股票风险对比
```

**风险评估输出格式**：

```python
{
    "stock_code": "000001.SZ",
    "stock_name": "平安银行",
    "assessment_date": "2026-04-16",

    "risk_level": "medium",               # 风险等级：low/medium/high/extreme
    "risk_score": 45,                      # 风险评分 0-100

    "volatility_metrics": {
        "daily_volatility": 2.5,
        "annual_volatility": 15.8,
        "atr_ratio": 3.2
    },

    "drawdown_metrics": {
        "max_drawdown": -8.5,
        "avg_drawdown": -3.2,
        "drawdown_duration": 15
    },

    "tail_risk": {
        "var_95": -5.2,
        "cvar_95": -7.1,
        "extreme_loss_prob": 0.02
    },

    "backtest_risk": {
        "win_rate": 62.5,
        "loss_streak_max": 3,
        "avg_loss": -2.1
    },

    "risk_factors": [
        {"factor": "高波动率", "impact": "high", "description": "日波动率超过2%"},
        {"factor": "回撤风险", "impact": "medium", "description": "最大回撤8.5%"}
    ],

    "analysis_text": "该股风险水平中等...",

    "risk_mitigation": [
        "建议控制仓位不超过20%",
        "设置止损线为-5%",
        "关注成交量变化"
    ]
}
```

### 模块四：投资建议服务（advice_service.py）

**功能定位**：综合趋势分析和风险评估，生成投资建议。

**核心方法**：

```python
class AdviceService:
    async def generate_advice(
        stock_code: str,
        advice_type: str = "comprehensive",  # comprehensive/buy/sell/hold
        include_backtest: bool = True,
        model: str = None
    ) -> Dict

    async def batch_generate_advice(
        stock_codes: List[str],
        advice_type: str = "comprehensive",
        model: str = None
    ) -> Dict

    async def generate_report(
        stock_codes: List[str],
        report_type: str = "portfolio",      # portfolio/watchlist/custom
        model: str = None
    ) -> Dict  # 批量分析报告
```

**投资建议输出格式**：

```python
{
    "stock_code": "000001.SZ",
    "stock_name": "平安银行",
    "advice_date": "2026-04-16",

    "recommendation": "buy",               # 建议：buy/sell/hold/watch
    "confidence": 0.75,

    "action_suggestion": {
        "action": "建议买入",
        "position_size": "中等仓位",
        "entry_strategy": "分批建仓",
        "target_price": 14.5,
        "stop_loss": 12.0
    },

    "reasoning": {
        "trend_reason": "上升趋势确立，技术面支撑明显",
        "score_reason": "综合评分78.5分，排名靠前",
        "risk_reason": "风险等级中等，回撤可控"
    },

    "time_horizon": {
        "short_term": "看涨",
        "mid_term": "看涨",
        "long_term": "中性"
    },

    "analysis_summary": "...",

    "key_catalysts": [
        "技术面突破关键支撑",
        "成交量温和放大"
    ],

    "risk_warnings": [
        "注意大盘系统性风险",
        "关注季度财报披露"
    ],

    "related_stocks": ["000002.SZ", "600000.SH"]
}
```

### 模块五：模型管理服务（model_service.py）

**功能定位**：管理 AI 模型的切换和状态检查。

**核心方法**：

```python
class ModelService:
    def get_available_models() -> List[Dict]
    # 返回：[{"provider": "claude", "models": ["claude-opus-4-6", ...]}, ...]

    def get_current_model() -> Dict
    # 返回：{"provider": "claude", "model": "claude-sonnet-4-6"}

    def switch_model(provider: str, model: str) -> Dict
    # 返回：{"success": true, "provider": "claude", "model": "claude-opus-4-6"}

    def check_status() -> Dict
    # 返回：{"claude": {"available": true}, "openai": {"available": true}, ...}
```

## MCP 工具定义

**趋势分析工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `ai_trend_analyze` | 分析单只股票趋势 | `stock_code`, `analysis_type`, `include_indicators`, `model` |
| `ai_trend_batch` | 批量趋势分析 | `stock_codes`, `analysis_type`, `model` |

**风险评估工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `ai_risk_assess` | 单只股票风险评估 | `stock_code`, `assessment_type`, `model` |
| `ai_risk_portfolio` | 组合风险评估 | `stock_codes`, `weights`, `model` |
| `ai_risk_compare` | 多股风险对比 | `stock_codes`, `model` |

**投资建议工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `ai_advice_generate` | 生成投资建议 | `stock_code`, `advice_type`, `include_backtest`, `model` |
| `ai_advice_batch` | 批量投资建议 | `stock_codes`, `advice_type`, `model` |
| `ai_advice_report` | 生成分析报告 | `stock_codes`, `report_type`, `model` |

**模型管理工具**：

| 工具名称 | 描述 | 参数 |
|----------|------|------|
| `ai_model_list` | 获取支持的模型列表 | 无 |
| `ai_model_current` | 获取当前使用的模型 | 无 |
| `ai_model_switch` | 切换模型 | `provider`, `model` |
| `ai_model_status` | 检查各 Provider 状态 | 无 |

## REST API 定义

所有接口前缀 `/api/v1`。

**趋势分析接口** `/api/v1/trend`：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/trend/analyze` | 单只股票趋势分析 |
| POST | `/trend/batch` | 批量趋势分析 |

**风险评估接口** `/api/v1/risk`：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/risk/assess` | 单只股票风险评估 |
| POST | `/risk/portfolio` | 组合风险评估 |
| POST | `/risk/compare` | 多股风险对比 |

**投资建议接口** `/api/v1/advice`：

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/advice/generate` | 生成投资建议 |
| POST | `/advice/batch` | 批量投资建议 |
| POST | `/advice/report` | 生成分析报告 |

**模型管理接口** `/api/v1/model`：

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/model/list` | 获取支持的模型列表 |
| GET | `/model/current` | 获取当前使用的模型 |
| POST | `/model/switch` | 切换模型 |
| GET | `/model/status` | 检查各 Provider 状态 |

## 依赖配置

**pyproject.toml**：

```toml
[project]
name = "ai-analyzer-service"
version = "0.1.0"
description = "AI 智能分析服务"

dependencies = [
    "fastapi>=0.115.0",
    "fastmcp>=3.2.0",
    "uvicorn>=0.30.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.27.0",
    "anthropic>=0.40.0",      # Claude API SDK
    "openai>=1.50.0",         # OpenAI API SDK
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
SERVICE_PORT=8011
SERVICE_HOST=0.0.0.0
DEBUG=false

# factor-service MCP 地址
FACTOR_SERVICE_URL=http://localhost:8010

# 默认 AI Provider
AI_PROVIDER=claude

# Claude 配置
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# OpenAI 配置
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Ollama 配置（可选）
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2:7b

# 日志配置
LOG_LEVEL=INFO
```

## 运行方式

1. **FastAPI + MCP 集成模式**（默认）：
   ```bash
   python run.py
   ```
   - REST API: `http://localhost:8011/api/v1/...`
   - MCP SSE: `http://localhost:8011/mcp`

2. **MCP 独立模式**（可选）：
   ```bash
   python run_mcp.py
   ```
   - MCP SSE: `http://localhost:8011/mcp`

## 测试策略

1. **Provider 测试**：验证各 AI Provider 的连接和分析能力
2. **分析服务测试**：验证趋势、风险、建议生成的正确性
3. **模型切换测试**：验证动态切换模型的正确性
4. **MCP 接口测试**：验证 MCP 工具调用正确性

## 与现有服务集成

**调用 factor-service**：
- 通过 MCP 客户端连接 factor-service
- 获取技术指标数据用于趋势分析
- 获取评分排名数据用于投资建议
- 获取回测数据用于风险评估

**被 backend/stock_policy 调用**：
- backend 存储分析配置后调用 ai-analyzer-service 执行分析
- 分析结果返回给 backend 用于前端展示

## AI Prompt 模板设计

### 趋势分析 Prompt

```text
你是一位专业的股票分析师。请根据以下数据分析股票趋势：

股票代码：{stock_code}
股票名称：{stock_name}
分析日期：{analysis_date}

关键指标数据：
{indicators_data}

评分数据：
{score_data}

请提供：
1. 趋势方向判断（上升/下降/横盘）
2. 趋势强度评估（0-1）
3. 关键支撑/压力位分析
4. 技术形态解读
5. 短中长期展望
6. 风险提示
```

### 风险评估 Prompt

```text
你是一位专业的风险管理专家。请根据以下数据评估股票风险：

股票代码：{stock_code}
股票名称：{stock_name}
评估日期：{assessment_date}

波动率数据：
{volatility_data}

回撤数据：
{drawdown_data}

回测数据：
{backtest_data}

请提供：
1. 风险等级判断（低/中/高/极高）
2. 风险评分（0-100）
3. 主要风险因素识别
4. 极端情况分析
5. 风险控制建议
```

### 投资建议 Prompt

```text
你是一位专业的投资顾问。请根据以下数据给出投资建议：

股票代码：{stock_code}
股票名称：{stock_name}
建议日期：{advice_date}

趋势分析：
{trend_analysis}

风险评估：
{risk_assessment}

评分排名：
{score_data}

请提供：
1. 投资建议（买入/卖出/持有/观望）
2. 建议置信度（0-1）
3. 仓位建议
4. 入场/出场策略
5. 目标价位和止损位
6. 投资理由和风险提示
```

## 流式响应支持

支持 SSE 流式返回分析结果，适用于长文本分析场景：

```python
# REST API 流式响应
POST /api/v1/trend/analyze/stream

# MCP 流式工具
ai_trend_analyze_stream
ai_risk_assess_stream
ai_advice_generate_stream
```