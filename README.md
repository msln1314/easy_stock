# 策略中心系统 (Stock Policy Center)

股票监控与策略管理系统，支持实时监控、预警通知、策略配置等功能。

## 功能模块

### 核心功能
- **股票监控池** - 添加股票到监控池，设置监控类型（持有/观察）
- **预警条件管理** - 创建和管理自定义预警条件，支持多指标组合
- **预警股票池** - 实时监控触发预警的股票
- **通知系统** - 多渠道通知推送（邮件、钉钉、Telegram、企业微信、Webhook）

### 系统管理
- **用户权限管理** - 用户、角色、菜单权限配置
- **系统配置** - 支持加密存储敏感配置
- **字典管理** - 系统字典类型和字典项管理
- **定时任务** - 任务调度与执行日志

### 数据分析
- **因子选股** - 因子定义、因子筛选、选股策略
- **策略跟踪** - 策略执行跟踪与日志记录
- **交易红线** - 交易纪律规则配置
- **交易日志** - 交易记录与统计分析

## 技术栈

### 后端
- Python 3.11+
- FastAPI - Web框架
- Tortoise-ORM - 异步ORM
- SQLite - 数据库
- Pydantic - 数据验证
- PyJWT - JWT认证
- httpx - 异步HTTP客户端

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
├── backend/                # 后端服务
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
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # Pinia状态
│   │   ├── api/           # API请求
│   │   ├── router/        # 路由配置
│   │   └── types/         # TypeScript类型
│   └── package.json
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

### 前端规范
- 使用TypeScript
- 组件使用Composition API (setup语法)
- 状态管理使用Pinia
- 样式使用UnoCSS原子化CSS

## License

MIT