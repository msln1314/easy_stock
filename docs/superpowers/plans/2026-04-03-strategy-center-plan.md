# 策略中心系统实施计划

**文档版本**: v1.0
**创建日期**: 2026-04-03
**关联设计**: [2026-04-03-strategy-center-design.md](specs/2026-04-03-strategy-center-design.md)
**实施阶段**: Phase 1 核心模块

---

## 1. 计划概述

### 1.1 目标
完成策略中心核心模块的开发，实现策略的完整生命周期管理（CRUD）、配置管理、分类筛选和分步向导创建流程。

### 1.2 时间规划
| 阶段 | 时间 | 主要任务 |
|------|------|----------|
| 数据库初始化 | Day 1-2 | 数据库创建、表结构建立、ORM模型开发 |
| 后端API开发 | Day 3-4 | RESTful接口实现、Schema定义、Service层 |
| 前端页面开发 | Day 5-7 | 策略列表页面、分步向导组件、状态管理 |
| 联调测试 | Day 8 | 前后端接口联调、功能验证、Bug修复 |
| 优化交付 | Day 9 | UI优化、ESLint校验、文档编写 |

### 1.3 技术栈确认
- **前端**: Vue3 + TypeScript + Vite + NaiveUI + Pinia + UnoCSS
- **后端**: FastAPI + Python 3.11+ + Tortoise-ORM + MySQL 8.0
- **图表**: ECharts + vue-echarts

---

## 2. 任务分解

### 2.1 数据库初始化 (Day 1-2)

#### Task 1.1: 创建MySQL数据库
- **优先级**: P0 (最高)
- **依赖**: 无
- **输出**: `stock_policy` 数据库
- **验收**: 数据库创建成功，字符集 utf8mb4
- **SQL**: `CREATE DATABASE stock_policy DEFAULT CHARSET utf8mb4;`

#### Task 1.2: 执行建表SQL
- **优先级**: P0
- **依赖**: Task 1.1
- **输出**: 5张核心表
  - `t_strategy` (策略主表)
  - `t_strategy_indicator` (技术指标配置表)
  - `t_strategy_signal` (买卖信号规则表)
  - `t_strategy_risk` (止盈止损配置表)
  - `t_strategy_backtest` (回测记录表 - Phase 2 预留)
- **验收**: 所有表创建成功，索引建立正确，外键约束有效

#### Task 1.3: 编写Tortoise-ORM模型
- **优先级**: P0
- **依赖**: Task 1.2
- **输出**: `backend/models/` 目录下4个模型文件
  - `strategy.py` - Strategy模型
  - `indicator.py` - StrategyIndicator模型
  - `signal.py` - StrategySignal模型
  - `risk.py` - StrategyRisk模型
- **验收**: ORM模型与数据库表结构一致，关系映射正确

#### Task 1.4: 数据库初始化脚本
- **优先级**: P1
- **依赖**: Task 1.3
- **输出**: `backend/scripts/init_db.py`
- **验收**: 脚本可执行，能完成数据库连接测试和表结构验证

---

### 2.2 后端API开发 (Day 3-4)

#### Task 2.1: 项目基础架构搭建
- **优先级**: P0
- **依赖**: Task 1.3
- **输出**:
  - `backend/main.py` - 应用入口
  - `backend/config/database.py` - 数据库配置
  - `backend/config/settings.py` - 应用配置
  - `backend/core/response.py` - 统一响应封装
  - `backend/core/exceptions.py` - 异常处理
  - `backend/core/middleware.py` - 中间件
- **验收**: FastAPI应用可启动，数据库连接正常

#### Task 2.2: Schema定义
- **优先级**: P0
- **依赖**: Task 2.1
- **输出**: `backend/schemas/` 目录
  - `strategy.py` - 策略请求/响应Schema
  - `indicator.py` - 指标Schema
  - `signal.py` - 信号Schema
  - `risk.py` - 风控Schema
- **验收**: Schema定义完整，包含字段验证规则

#### Task 2.3: 策略CRUD接口
- **优先级**: P0
- **依赖**: Task 2.2
- **输出**: `backend/api/v1/strategy.py`
- **接口**:
  - `GET /api/v1/strategies` - 策略列表（分页、筛选）
  - `GET /api/v1/strategies/{id}` - 策略详情
  - `POST /api/v1/strategies` - 创建策略
  - `PUT /api/v1/strategies/{id}` - 更新策略
  - `DELETE /api/v1/strategies/{id}` - 删除策略
- **验收**: 接口功能正常，响应格式统一

#### Task 2.4: 指标/信号/风控接口
- **优先级**: P0
- **依赖**: Task 2.3
- **输出**:
  - `backend/api/v1/strategy_indicator.py`
  - `backend/api/v1/strategy_signal.py`
  - `backend/api/v1/strategy_risk.py`
- **验收**: 子资源CRUD接口正常，级联操作正确

#### Task 2.5: 状态更新和统计接口
- **优先级**: P1
- **依赖**: Task 2.3
- **输出**:
  - `PUT /api/v1/strategies/{id}/status` - 状态更新
  - `GET /api/v1/strategies/stats` - 统计信息
- **验收**: 状态切换正常，统计数据计算准确

#### Task 2.6: Service层实现
- **优先级**: P0
- **依赖**: Task 2.2
- **输出**: `backend/services/` 目录
  - `strategy.py` - 策略业务逻辑
  - `indicator.py` - 指标业务逻辑
  - `signal.py` - 信号业务逻辑
  - `risk.py` - 风控业务逻辑
- **验收**: 业务逻辑封装正确，事务处理合理

---

### 2.3 前端页面开发 (Day 5-7)

#### Task 3.1: 项目结构搭建
- **优先级**: P0
- **依赖**: Task 2.3
- **输出**:
  - 路由配置 `frontend/src/router/index.ts`
  - API封装 `frontend/src/api/strategy.ts`
  - 类型定义 `frontend/src/types/strategy.ts`
- **验收**: 项目结构清晰，路由可访问

#### Task 3.2: TypeScript类型定义
- **优先级**: P0
- **依赖**: 无
- **输出**: `frontend/src/types/strategy.ts`
- **类型定义**:
  - `Strategy` - 策略主类型
  - `Indicator` - 指标类型
  - `Signal` - 信号类型
  - `RiskConfig` - 风控配置类型
  - `StrategyStats` - 统计类型
  - `CreateStrategyRequest` - 创建请求类型
  - `UpdateStrategyRequest` - 更新请求类型
- **验收**: 类型与后端Schema一致

#### Task 3.3: API封装
- **优先级**: P0
- **依赖**: Task 3.2
- **输出**: `frontend/src/api/strategy.ts`
- **API函数**:
  - `getStrategies(params)` - 获取列表
  - `getStrategy(id)` - 获取详情
  - `createStrategy(data)` - 创建策略
  - `updateStrategy(id, data)` - 更新策略
  - `deleteStrategy(id)` - 删除策略
  - `updateStrategyStatus(id, status)` - 更新状态
  - `getStrategyStats()` - 获取统计
- **验收**: Axios请求封装正确，响应处理规范

#### Task 3.4: Pinia状态管理
- **优先级**: P0
- **依赖**: Task 3.3
- **输出**:
  - `frontend/src/stores/strategy.ts` - 策略列表状态
  - `frontend/src/stores/wizard.ts` - 向导表单状态
- **验收**: 状态管理逻辑正确，响应式更新正常

#### Task 3.5: 策略列表主页面
- **优先级**: P0
- **依赖**: Task 3.4
- **输出**: `frontend/src/views/strategy/index.vue`
- **功能**:
  - 左右布局结构
  - 操作栏（新增、搜索）
  - 分页组件
- **验收**: 页面布局符合设计稿

#### Task 3.6: 左侧筛选导航组件
- **优先级**: P1
- **依赖**: Task 3.5
- **输出**: `frontend/src/components/StrategyFilter.vue`
- **功能**:
  - 全部策略统计
  - 执行模式分类筛选（自动交易/信号提醒/模拟运行）
  - 运行状态分类筛选（运行中/已暂停/已停止）
  - 统计数据展示
- **验收**: 筛选功能正常，统计数据准确

#### Task 3.7: 策略卡片组件
- **优先级**: P0
- **依赖**: Task 3.5
- **输出**: `frontend/src/components/StrategyCard.vue`
- **功能**:
  - 策略名称、描述展示
  - 执行模式、状态标签（颜色区分）
  - 收益率、胜率等指标展示
  - 操作按钮（编辑/暂停/启动/删除/详情）
- **验收**: 卡片展示正确，操作按钮响应正常

#### Task 3.8: 分步向导容器组件
- **优先级**: P0
- **依赖**: Task 3.5
- **输出**: `frontend/src/components/StrategyWizard.vue`
- **功能**:
  - 步骤条展示（NaiveUI Steps组件）
  - 步骤切换控制
  - 上一步/下一步/提交按钮
  - 弹窗容器（Modal）
- **验收**: 步骤切换流畅，状态管理正确

#### Task 3.9: Step1 基础信息表单
- **优先级**: P0
- **依赖**: Task 3.8
- **输出**: `frontend/src/components/StepBasic.vue`
- **字段**:
  - 策略名称（必填）
  - 策略描述（可选）
  - 执行模式（单选）
  - 关联股票（多选）
- **验收**: 表单验证正确，数据绑定正常

#### Task 3.10: Step2 技术指标表单
- **优先级**: P0
- **依赖**: Task 3.8
- **输出**: `frontend/src/components/StepIndicator.vue`
- **功能**:
  - 添加指标按钮
  - 指标类型选择（MA/MACD/RSI/KDJ/BOLL）
  - 参数动态配置表单
  - 指标列表展示与删除
- **验收**: 指标添加/删除正常，参数配置正确

#### Task 3.11: Step3 买卖信号表单
- **优先级**: P0
- **依赖**: Task 3.8
- **输出**: `frontend/src/components/StepSignal.vue`
- **功能**:
  - 信号类型选择（buy/sell）
  - 条件类型选择（indicator_cross/threshold/custom）
  - 条件配置动态表单
  - 优先级设置
  - 信号列表展示与删除
- **验收**: 信号配置完整，条件表单动态响应

#### Task 3.12: Step4 止盈止损表单
- **优先级**: P0
- **依赖**: Task 3.8
- **输出**: `frontend/src/components/StepRisk.vue`
- **字段**:
  - 止盈类型（单选：固定百分比/动态/移动止盈）
  - 止盈值
  - 止损类型（单选：固定百分比/动态）
  - 止损值
  - 最大仓位比例
- **验收**: 风控参数配置正确

#### Task 3.13: Step5 回测验证页面
- **优先级**: P2 (Phase 2 完整实现，Phase 1 仅预留)
- **依赖**: Task 3.8
- **输出**: `frontend/src/components/StepBacktest.vue`
- **功能**:
  - 回测日期范围选择
  - 运行回测按钮（预留）
  - 收益曲线图表（预留）
  - 关键指标展示（预留）
- **验收**: 页面结构搭建完成，Phase 1 仅展示占位信息

---

### 2.4 联调测试 (Day 8)

#### Task 4.1: 前后端接口联调
- **优先级**: P0
- **依赖**: Task 2.5, Task 3.13
- **测试范围**:
  - 策略列表获取与筛选
  - 策略详情展示
  - 策略创建流程（完整5步）
  - 策略编辑流程
  - 策略删除操作
  - 状态切换操作
- **验收**: 所有接口响应正常，数据一致性验证通过

#### Task 4.2: 功能测试验证
- **优先级**: P0
- **依赖**: Task 4.1
- **测试用例**:
  - TC01: 创建完整策略（包含指标、信号、风控）
  - TC02: 编辑已有策略，修改各配置项
  - TC03: 删除策略，验证级联删除
  - TC04: 状态切换（暂停→运行→停止）
  - TC05: 筛选功能（按执行模式、状态）
  - TC06: 分页功能
  - TC07: 统计数据计算准确性
- **验收**: 所有测试用例通过

#### Task 4.3: Bug修复
- **优先级**: P0
- **依赖**: Task 4.2
- **输出**: Bug修复记录
- **验收**: 无阻塞性Bug，无功能缺陷

---

### 2.5 优化交付 (Day 9)

#### Task 5.1: UI细节优化
- **优先级**: P1
- **依赖**: Task 4.3
- **优化项**:
  - 状态/模式标签颜色优化
  - 按钮样式统一
  - 加载状态展示
  - 错误提示友好化
  - 响应式布局适配
- **验收**: UI视觉效果符合设计要求

#### Task 5.2: ESLint校验
- **优先级**: P1
- **依赖**: Task 5.1
- **输出**: ESLint配置文件，校验报告
- **验收**: 前端代码无ESLint错误

#### Task 5.3: 使用文档编写
- **优先级**: P2
- **依赖**: Task 5.2
- **输出**: README更新，使用说明
- **验收**: 文档清晰，覆盖核心功能

---

## 3. 任务依赖图

```
Task 1.1 ──→ Task 1.2 ──→ Task 1.3 ──→ Task 1.4
                              │
                              ↓
                         Task 2.1 ──→ Task 2.2 ──→ Task 2.6
                              │              │
                              ↓              ↓
                         Task 2.3 ──→ Task 2.4
                              │
                              ↓
                         Task 2.5
                              │
                              ↓
                    ┌─────────────────────┐
                    │   Task 3.1          │
                    │   Task 3.2 (独立)   │
                    └──┬───────────────┬──┘
                       ↓               ↓
                    Task 3.3        Task 3.8
                       ↓               │
                    Task 3.4           ↓
                       ↓         ┌─────────────────────┐
                    Task 3.5     │ Task 3.9 - 3.13    │
                       │         │   (并行开发)        │
                       ↓         └─────────────────────┘
              ┌────────────────┐              │
              │ Task 3.6       │              │
              │ Task 3.7       │              │
              │   (并行)       │              │
              └────────────────┘              │
                       │                      │
                       ↓                      ↓
                    ┌─────────────────────────────┐
                    │        Task 4.1              │
                    └─────────────────────────────┘
                              │
                              ↓
                         Task 4.2 ──→ Task 4.3
                                        │
                                        ↓
                              ┌─────────────────────┐
                              │ Task 5.1            │
                              │ Task 5.2 (并行)     │
                              │ Task 5.3            │
                              └─────────────────────┘
```

---

## 4. 开发资源分配

### 4.1 人员分工建议

| 任务组 | 建议人员 | 技能要求 |
|--------|----------|----------|
| 数据库初始化 | 后端开发 | MySQL、Tortoise-ORM |
| 后端API开发 | 后端开发 | FastAPI、Pydantic、RESTful |
| 前端页面开发 | 前端开发 | Vue3、NaiveUI、Pinia、TypeScript |
| 联调测试 | 前后端协作 | 全栈理解、测试能力 |
| 优化交付 | 前后端协作 | UI设计、代码规范 |

### 4.2 环境准备

| 环境 | 配置 | 用途 |
|------|------|------|
| 开发环境 | MySQL 8.0 + Python 3.11 + Node 18 | 本地开发 |
| 数据库 | localhost:3306, stock_policy | 数据存储 |
| API服务 | http://localhost:8000 | 后端服务 |
| 前端服务 | http://localhost:5173 | 前端开发服务器 |

---

## 5. 风险与应对

| 风险项 | 可能影响 | 应对措施 |
|--------|----------|----------|
| 数据库连接问题 | 阻塞ORM开发 | 提前验证数据库配置，准备备用连接方案 |
| NaiveUI组件熟悉度 | 前端进度延迟 | 提前阅读组件文档，使用官方示例 |
| 步骤向导状态管理复杂 | 数据流转错误 | 设计清晰的状态流转图，单元测试覆盖 |
| 接口响应格式不一致 | 前后端对接困难 | 统一响应封装，提前约定Schema |
| Phase 1 功能范围蔓延 | 时间超期 | 严格按计划执行，Phase 2+ 功能延期 |

---

## 6. 里程碑检查点

| 检查点 | 时间 | 验收标准 |
|--------|------|----------|
| M1: 数据库完成 | Day 2 | 5张表创建成功，ORM模型验证通过 |
| M2: 后端API完成 | Day 4 | 所有接口可调用，响应格式正确 |
| M3: 前端页面完成 | Day 7 | 策略列表展示，向导流程完整 |
| M4: 功能验证通过 | Day 8 | 7个测试用例全部通过 |
| M5: 交付完成 | Day 9 | ESLint无错误，文档更新 |

---

## 7. 附录

### 7.1 文件清单

**后端文件 (预计)**:
- `backend/main.py`
- `backend/config/database.py`
- `backend/config/settings.py`
- `backend/core/response.py`
- `backend/core/exceptions.py`
- `backend/core/middleware.py`
- `backend/models/strategy.py`
- `backend/models/indicator.py`
- `backend/models/signal.py`
- `backend/models/risk.py`
- `backend/schemas/strategy.py`
- `backend/schemas/indicator.py`
- `backend/schemas/signal.py`
- `backend/schemas/risk.py`
- `backend/services/strategy.py`
- `backend/services/indicator.py`
- `backend/services/signal.py`
- `backend/services/risk.py`
- `backend/api/v1/strategy.py`
- `backend/api/v1/strategy_indicator.py`
- `backend/api/v1/strategy_signal.py`
- `backend/api/v1/strategy_risk.py`
- `backend/api/v1/strategy_stats.py`
- `backend/routes/strategy.py`
- `backend/scripts/init_db.py`

**前端文件 (预计)**:
- `frontend/src/views/strategy/index.vue`
- `frontend/src/components/StrategyFilter.vue`
- `frontend/src/components/StrategyCard.vue`
- `frontend/src/components/StrategyWizard.vue`
- `frontend/src/components/StepBasic.vue`
- `frontend/src/components/StepIndicator.vue`
- `frontend/src/components/StepSignal.vue`
- `frontend/src/components/StepRisk.vue`
- `frontend/src/components/StepBacktest.vue`
- `frontend/src/api/strategy.ts`
- `frontend/src/types/strategy.ts`
- `frontend/src/stores/strategy.ts`
- `frontend/src/stores/wizard.ts`
- `frontend/src/router/index.ts`
- `frontend/src/composables/useStrategy.ts`

### 7.2 接口清单汇总

| 接口路径 | 方法 | 功能 | 优先级 |
|----------|------|------|--------|
| `/api/v1/strategies` | GET | 策略列表 | P0 |
| `/api/v1/strategies/{id}` | GET | 策略详情 | P0 |
| `/api/v1/strategies` | POST | 创建策略 | P0 |
| `/api/v1/strategies/{id}` | PUT | 更新策略 | P0 |
| `/api/v1/strategies/{id}` | DELETE | 删除策略 | P0 |
| `/api/v1/strategies/{id}/status` | PUT | 更新状态 | P1 |
| `/api/v1/strategies/stats` | GET | 统计信息 | P1 |
| `/api/v1/strategies/{id}/indicators` | GET | 指标列表 | P0 |
| `/api/v1/strategies/{id}/indicators` | POST | 添加指标 | P0 |
| `/api/v1/strategies/{id}/indicators/{iid}` | PUT | 更新指标 | P0 |
| `/api/v1/strategies/{id}/indicators/{iid}` | DELETE | 删除指标 | P0 |
| `/api/v1/strategies/{id}/signals` | GET | 信号列表 | P0 |
| `/api/v1/strategies/{id}/signals` | POST | 添加信号 | P0 |
| `/api/v1/strategies/{id}/signals/{sid}` | PUT | 更新信号 | P0 |
| `/api/v1/strategies/{id}/signals/{sid}` | DELETE | 删除信号 | P0 |
| `/api/v1/strategies/{id}/risk` | GET | 风控配置 | P0 |
| `/api/v1/strategies/{id}/risk` | POST | 创建风控 | P0 |
| `/api/v1/strategies/{id}/risk` | PUT | 更新风控 | P0 |

---

**文档结束**