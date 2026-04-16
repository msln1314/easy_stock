# 策略中心系统 (Stock Policy Center)

股票监控与策略管理系统，支持实时监控、预警通知、策略配置、因子选股、AI智能分析等功能。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Stock Policy 系统架构                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   frontend (Vue) ← 用户交互界面 (端口 3000)                            │
│         │                                                            │
│         ▼                                                            │
│   backend (FastAPI) ← 主服务，数据持久化 (端口 5000)                   │
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
│   │  factor-service (8010)    ai-analyzer-service (8011)          │  │
│   │  - 因子选股               - AI 智能分析                        │  │
│   │  - 指标计算               - 趋势分析                           │  │
│   │  - 评分计算               - 风险评估                           │  │
│   │  - 回测验证               - 投资建议                           │  │
│   │                                                                │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

调用链: ai-analyzer-service → factor-service → stock-service
```

## 功能模块详解

### 监控大屏 (`/dashboard`)
数据可视化展示页面，包含：
- **指标卡片** - 关键数据概览（持仓数量、预警数量、今日信号等）
- **持仓表格** - 当前持仓股票列表与状态
- **行情表格** - 实时股票行情数据
- **预警滚动条** - 最新预警滚动展示
- **预警列表** - 预警详情列表
- **卖出预警面板** - 卖出预警信号汇总
- **策略状态面板** - 策略运行状态监控
- **系统监控面板** - 系统运行状态（任务执行、API调用）
- **收益曲线图** - 策略收益走势图表

### 策略管理 (`/strategy`)
多步骤策略创建与配置：
- **基本信息** - 策略名称、描述、类型设置
- **指标配置** - 选择和配置技术指标
- **回测设置** - 回测参数配置
- **风控规则** - 止损止盈、仓位控制
- **信号配置** - 买入卖出信号规则
- **策略向导** - 分步创建流程引导
- **策略卡片** - 策略概览卡片展示
- **策略筛选** - 按条件筛选策略

### 指标库管理 (`/indicator`)
技术指标定义与管理：
- 指标列表管理（名称、类型、参数配置）
- 指标添加弹窗
- 指标详情弹窗（参数配置、计算逻辑）
- 指标启用/禁用控制

### 因子筛选 (`/factor-screen`)
基于因子的股票筛选：
- 因子选择与配置
- 筛选条件设置
- 筛选结果展示
- 导出筛选结果

### 因子库管理 (`/factor-library`)
因子定义与管理：
- 因子分类管理
- 因子定义详情
- 因子计算逻辑配置

### 监控股票池 (`/monitor`)
股票监控池管理：
- 添加股票到监控池
- 设置监控类型（持有/观察）
- 股票信息展示（代码、名称、价格、涨跌幅）
- 批量导入功能
- 监控状态切换

### 卖出预警 (`/warning`)
预警条件与预警股票管理：
- **条件分组树** - 预警条件分组树形展示
- **条件组编辑器** - 创建/编辑预警条件组
- **预警列表** - 触发预警的股票列表
- 支持多指标组合条件
- 预警级别设置（critical/warning/info）

### 卖出策略配置 (`/strategy-config`)
卖出策略参数配置：
- 策略参数设置
- 策略启用/禁用

### 卖出信号明细 (`/signal`)
卖出信号记录与跟踪：
- 信号触发时间
- 信号类型（买入/卖出）
- 关联股票信息
- 信号状态跟踪

### 交易管理 (`/trade`)
交易记录与分析：
- 交易日志录入
- 交易记录查询
- 交易统计分析
- 收益计算

### AI股票分析 (`/stock-analysis`)
AI辅助股票分析：
- AI对话分析界面
- 股票分析报告生成
- 多轮对话交互
- 分析历史记录

### 计划任务 (`/scheduler`)
定时任务调度管理：
- 任务列表管理（名称、状态、执行时间）
- Cron表达式构建器
- 任务启用/禁用
- 执行日志查看
- 手动触发执行

### 通知配置 (`/notification`)
多渠道通知系统配置：
- **通知渠道** - 创建/管理通知渠道（邮件、钉钉、Telegram、企业微信、Webhook）
- **通知模板** - 消息模板管理，支持变量替换
- **通知对象** - 收件人信息管理（邮箱、手机号、微信、钉钉等）
- **通知对象组** - 按渠道类型创建收件人组（邮件组、钉钉组等）
- **发送记录** - 通知发送日志查询
- 渠道测试发送功能

### 系统配置 (`/config`)
系统参数配置管理：
- 配置项列表（键名、值、类型、描述）
- 配置值编辑
- 加密配置支持（密码、密钥等敏感信息）
- 配置分组管理

### 字典管理 (`/dict`)
系统字典数据管理：
- 字典类型管理（类型编码、名称）
- 字典项管理（项值、标签、排序）
- 字典启用/禁用

### 菜单管理 (`/system/menu`)
系统菜单配置：
- 菜单树形结构管理
- 菜单类型（目录、菜单、按钮）
- 外部链接菜单支持
- iframe嵌入模式
- 菜单图标配置

### 角色管理 (`/system/role`)
角色与权限管理：
- 角色列表（角色名、编码、状态）
- 角色权限配置（菜单权限分配）
- 角色启用/禁用

### 用户管理 (`/system/user`)
用户账号管理：
- 用户列表（用户名、姓名、状态）
- 用户创建/编辑
- 密码重置
- 角色分配
- 用户启用/禁用

### 用户信息 (`/profile`)
个人信息管理：
- 用户信息展示
- 密码修改
- 个人偏好设置

## 微服务详解

### factor-service (端口 8010)

因子分析与评分计算微服务，提供技术指标计算、因子选股、评分计算、回测验证功能。

**核心功能：**
- **技术指标计算** - 支持25种预设指标
  - MA/EMA 均线系列
  - RSI 相对强弱指标
  - MACD 指数平滑异同移动平均线
  - KDJ 随机指标
  - BOLL 布林带
  - ATR 平均真实波动幅度
  - VOL_MA/VOL_RATIO/OBV 成交量指标
  - AMP/MOM 振幅/动量指标

- **因子选股筛选** - 支持多种操作符
  - gt (大于) / lt (小于)
  - ge (大于等于) / le (小于等于)
  - eq (等于)
  - between (区间)

- **综合评分计算** - 百分位排名 + 加权求和算法
  - 支持正向/逆向因子方向
  - 自定义权重配置
  - 实时排名计算

- **回测验证** - 因子有效性验证
  - IC分析 (Information Coefficient)
  - 分组收益对比
  - 敏感性测试

**接口：**
- REST API: `http://localhost:8010/api/v1/...`
- MCP SSE: `http://localhost:8010/mcp`
- API文档: `http://localhost:8010/docs`

### ai-analyzer-service (端口 8011)

AI智能分析微服务，提供趋势分析、风险评估、投资建议等AI驱动的分析能力。

**核心功能：**
- **趋势分析** - 结合评分和指标数据
  - 趋势方向判断 (上升/下降/横盘)
  - 趋势强度评估 (0-1)
  - 分析置信度
  - 关键支撑/压力位分析
  - 技术形态解读

- **风险评估** - 多维度风险分析
  - 波动率指标 (日波动率/年化波动率)
  - 回撤指标 (最大回撤/平均回撤)
  - 尾部风险 (VaR/CVaR)
  - 风险等级评分 (低/中/高/极高)

- **投资建议** - 综合分析生成建议
  - 投资建议 (买入/卖出/持有/观望)
  - 建议置信度
  - 仓位建议
  - 入场/出场策略
  - 目标价位和止损位

- **模型管理** - 多AI Provider支持
  - Claude (claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5)
  - OpenAI (gpt-4o, gpt-4o-mini, gpt-4-turbo)
  - Ollama (本地模型，如 llama3, qwen2)

**接口：**
- REST API: `http://localhost:8011/api/v1/...`
- MCP SSE: `http://localhost:8011/mcp`
- API文档: `http://localhost:8011/docs`

## 技术栈

### 主服务 (backend)
- Python 3.11+
- FastAPI - Web框架
- Tortoise-ORM - 异步ORM
- SQLite - 数据库
- Pydantic - 数据验证
- PyJWT - JWT认证
- httpx - 异步HTTP客户端

### 微服务层
- Python 3.11+
- FastAPI - REST API框架
- FastMCP - MCP协议支持 (SSE传输)
- pandas/numpy - 数据计算
- anthropic - Claude API SDK
- openai - OpenAI API SDK
- httpx - MCP客户端

### 前端
- Vue 3 + TypeScript
- Vite - 构建工具
- Naive UI - UI组件库
- Pinia - 状态管理
- Vue Router - 路由管理
- ECharts - 图表库
- UnoCSS - CSS工具

## 项目结构

```
stock_policy/
├── backend/                # 主后端服务 (端口 5000)
│   ├── api/               # API路由
│   │   └── v1/            # v1版本API
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   ├── schemas/           # Pydantic模型
│   ├── core/              # 核心模块(认证、配置等)
│   ├── utils/             # 工具函数
│   ├── jobs/              # 定时任务
│   ├── scripts/           # 脚本文件
│   └── main.py            # 入口文件
│
├── frontend/              # 前端应用 (端口 3000)
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # Pinia状态
│   │   ├── api/           # API请求
│   │   ├── router/        # 路由配置
│   │   └── types/         # TypeScript类型
│   └── package.json
│
├── factor-service/        # 因子服务 (端口 8010)
│   ├── app/
│   │   ├── services/      # 指标/因子/回测服务
│   │   ├── models/        # 数据模型
│   │   ├── mcp/           # MCP类封装
│   │   ├── api/           # REST API路由
│   │   └── main.py        # FastAPI入口
│   └── pyproject.toml
│
├── ai-analyzer-service/   # AI分析服务 (端口 8011)
│   ├── app/
│   │   ├── services/      # 趋势/风险/建议/模型服务
│   │   ├── models/        # 数据模型
│   │   ├── mcp/           # MCP类封装
│   │   ├── api/           # REST API路由
│   │   ├── core/          # 核心模块
│   │   │   └ providers/   # AI Provider实现
│   │   └── main.py        # FastAPI入口
│   └── pyproject.toml
│
└── docs/                  # 文档目录
```

## 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（首次运行）
python scripts/init_db.py

# 初始化系统配置
python scripts/init_sys_config.py

# 启动服务
python main.py
# 或使用uvicorn
uvicorn main:app --reload --port 5000
```

后端服务地址: http://localhost:5000
API文档: http://localhost:5000/docs

### 前端启动

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务
pnpm dev

# 构建生产版本
pnpm build
```

前端服务地址: http://localhost:3000

### 微服务启动

**factor-service:**
```bash
cd factor-service

# 安装依赖
pip install -e .

# 启动服务
python run.py
```

服务地址: http://localhost:8010
API文档: http://localhost:8010/docs
健康检查: http://localhost:8010/health

**ai-analyzer-service:**
```bash
cd ai-analyzer-service

# 安装依赖
pip install -e .

# 配置AI Provider (编辑 .env)
cp .env.example .env

# 启动服务
python run.py
```

服务地址: http://localhost:8011
API文档: http://localhost:8011/docs
健康检查: http://localhost:8011/health

## 环境配置

### factor-service 配置

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

### ai-analyzer-service 配置

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

## 通知系统配置

系统支持多种通知渠道，配置优先级：渠道配置 > 系统配置

### 渠道类型
- **邮件 (email)** - SMTP配置
- **钉钉 (dingtalk)** - Webhook机器人
- **Telegram (telegram)** - Bot API
- **企业微信 (wechat_work)** - Webhook机器人
- **自定义Webhook (webhook)** - 自定义HTTP接口

### 配置方式
1. 系统配置：在系统配置页面设置全局通知账号
2. 渠道配置：在通知渠道页面创建渠道，可使用自定义配置或继承系统配置
3. 通知对象组：按渠道类型创建收件人组（如邮件组、钉钉组）

## 默认账号

首次初始化后默认管理员账号：
- 用户名: admin
- 密码: admin123

请登录后及时修改密码。

## 开发说明

### 数据库模型
所有模型定义在 `backend/models/` 目录，使用Tortoise-ORM的异步模型。

### API规范
- RESTful风格
- 统一响应格式: `{ "code": 0, "data": {}, "message": "success" }`
- 认证方式: JWT Token (Header: Authorization: Bearer <token>)

### 微服务规范
- FastAPI + FastMCP 双接口模式
- 三层架构：services → MCP classes → MCP server → main.py
- 无数据持久化，数据通过 MCP 从上游服务获取
- 健康检查接口: `/health`
- MCP接口: `/mcp` (SSE传输)

### 前端规范
- 使用TypeScript
- 组件使用Composition API (setup语法)
- 状态管理使用Pinia
- 样式使用UnoCSS原子化CSS

## MCP工具列表

### factor-service MCP工具

| 工具名称 | 描述 |
|----------|------|
| `indicator_calculate` | 计算单只股票技术指标 |
| `indicator_batch` | 批量计算多只股票指标 |
| `indicator_list` | 获取支持的指标列表 |
| `factor_screen` | 因子选股筛选 |
| `factor_score` | 综合评分计算 |
| `factor_value` | 获取单只股票因子值 |
| `backtest_run` | 执行完整回测 |
| `backtest_ic` | IC分析 |
| `backtest_group` | 分组收益对比 |
| `backtest_sensitivity` | 敏感性测试 |

### ai-analyzer-service MCP工具

| 工具名称 | 描述 |
|----------|------|
| `ai_trend_analyze` | 单只股票趋势分析 |
| `ai_trend_batch` | 批量趋势分析 |
| `ai_risk_assess` | 单只股票风险评估 |
| `ai_risk_portfolio` | 组合风险评估 |
| `ai_risk_compare` | 多股风险对比 |
| `ai_advice_generate` | 生成投资建议 |
| `ai_advice_batch` | 批量投资建议 |
| `ai_advice_report` | 生成分析报告 |
| `ai_model_list` | 获取支持的模型列表 |
| `ai_model_current` | 获取当前使用的模型 |
| `ai_model_switch` | 切换模型 |
| `ai_model_status` | 检查各Provider状态 |

## License

MIT