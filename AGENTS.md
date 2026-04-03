# AGENTS.md
## 0. 开发流程（必须遵循）

**开始任何代码开发前，必须按以下顺序执行：**

1. **生成方案文档** - 创建 `docs/方案文档.md`，包含：
   - 需求分析
   - 数据库设计（表结构、ER图）
   - 技术栈
   - 接口设计
   - 页面设计
   - 设计风格
   - 响应风格
   - UI风格
   - 开发计划

2. **等待用户确认** - 方案文档必须经用户确认后，方可开始编码

3. **执行开发** - 按方案文档实施

4. UI 部分优先交给视觉/交互专家，优先级最高；后端逻辑交给 backend 代理；整体架构先让 oracle 评审,优先使用并行开发(ulw/worktree)
⚠️ 违反此流程视为严重错误


## 1. 技术栈

### 前端技术栈

**核心框架**
- Vue3 + TypeScript + Vite

**状态管理与路由**
- Pinia（状态管理）
- Vue Router（路由）

**UI框架与样式**
- NaiveUI（UI组件库）
- UnoCSS（原子化CSS）
- scss（样式预处理）

**数据可视化**
- vue-echarts
- echarts
- @vueuse/motion（动画）

**工具库**
- Axios（HTTP请求）
- Day.js（日期处理）
- nprogress（进度条）
- @vicons/ionicons5（图标库）
- vue-virtual-scroller（虚拟滚动）

**开发工具**
- PNPM（包管理器）
- eslint（代码校验）

### 后端技术栈

**核心框架**
- Python 3.11+
- FastAPI
- Uvicorn（ASGI服务器）

**数据库**
- SQLite（数据库）
- ORM框架：Tortoise-ORM（简单项目推荐）

**数据验证与安全**
- Pydantic（数据验证）
- PyJWT（JWT认证）
- passlib[bcrypt]（密码哈希）
- python-multipart（文件上传）

**HTTP客户端**
- httpx（异步请求）

**配置与日志**
- python-dotenv（环境变量）
- loguru（日志管理）
- traceback

**数据处理**
- pandas
- openpyxl（Excel处理）

**测试框架**
- pytest
- pytest-asyncio

### 数据库
- SQLite

## 2. 项目结构

### 前端

```
frontend
    src/
    ├── api/              # API 接口定义
    ├── assets/           # 静态资源（图片、字体等）
    ├── components/       # 公共组件
    |   Table             # 表格封装
    ├── composables/      # 组合式函数（hooks）
    ├── layouts/          # 布局组件
    ├── router/           # 路由配置
    |     index.ts        # 路由
    |      guard.ts        # 路由守卫
    |—— directives        # 指令
    |—— styles            #公共样式
    ├── stores/           # 状态管理（Pinia）
    |     app.ts          # 应用状态
    |     user.ts         # 用户状态
    ├── types/            # TypeScript 类型定义
    ├── utils/            # 工具函数
    |      helpers.ts      # 常用工具
    |      index.ts        # 统一导出
    |      request.ts      # 请求封装
    |——types/             # 全局公共类型
    └── views/            # 页面组件
            user/
              index.vue   #主页面
              detail.vue  #子页面
              edit.vue    #子页面
    dev.env               # 开发环境变量
    prod.env              # 生成环境变量
    public/               # 静态资源（不经构建）
    dist/                 # 构建产物
```

### 后端

```
backend
    main.py                # 应用入口
    config/               # 配置模块
    docs/                 # 文件文档
    data/                 # 数据库文件
    models/               # 数据模型
        user              # 用户模型
    core/                 # 中间件
        database.py          # 数据库中间件
        auth.py              # 认证中间件
        middleware.py        # 中间件
        logger.py            # 日志中间件
        response.py          # 响应模块
        exceptions.py        # 异常处理
        dependency.py        # 依赖
    routes/               # 路由模块
    services/             # 业务逻辑
    schemas/              # 数据验证模块
    utils/                # 工具函数
    logs/                 # 日志目录
    scripts/              # 脚本文件
    static/               # 前端构建目录
    dev.env               # 开发环境变量
    prod.env              # 生成环境变量
```

## 3. 开发命令

| 命令                                         | 说明         |
| -------------------------------------------- | ------------ |
| `uv pip install -r requirements.txt`            | 安装依赖     |
| `python main.py`                              | 启动开发服务 |
| `python init_db.py`                          | 初始化数据库 |
| `uvicorn app:main --host 0.0.0.0 --port 5000` | 生产环境启动 |

| 命令            | 说明         |
| --------------- | ------------ |
| `pnpm install`   | 安装依赖     |
| `pnpm run dev`   | 启动开发服务 |
| `pnpm run build` | 构建前端     |
| `端口:3000`     | 预览前端     |

## 4. 代码风格

- Python 文件使用 UTF-8 编码
- 遵循 PEP 8 规范
- 变量命名：snake_case
- 函数命名：snake_case
- 前端使用Prettier + eslint 校验
- 前端组件风格遵循template-script-style 顺序
## 5. 设计风格
- 后端输入，输出，响应 必须使用schemas(严格遵守)
- 功能模块根据模块分文件设计
- 前端页面组件根据子页面分文件
- 前端api 根据模块分文件
- 后端返回统一返回结构 
- 通用工具统一封装为工具调用
- 公共部分提取到通用文件中，比如utils
## 6.响应风格
    调用统一的响应schemas
 
    route 响应response_model=ResponseModel
    -成功响应
   return success_response(
        data=[await BookCategoryResponse.from_tortoise_orm(cat) for cat in categories]
    )
    {"code": 200, "message": "success", "data": {...}}

    -失败响应
    return error_response(message: "错误信息", code: int = 400) 
    {"code": 400, "message": "错误信息", "data": null}

    - 后端接口RestFul 接口风格
## 7.UI风格
    - 表格选项颜色需要有不同的颜色
    - 按钮清晰简洁
## 8. 初始化数据
- 初始化生成随机jwt密钥
- 初始化导入测试数据[可选]
- 初始化生成用户基础数据
## 基础功能要求
- 前端报错友好显示输出
- 后端异常统一用异常拦截器处理
- 要求分页，排序，导出，查询筛选添加事件
- 页面中文显示



# 注意事项
- 需要支持热启动
- 项目使用封装的request工具进行API调用，位于 `/src/utils/request.ts`。
- 务必确保 UnoCSS 的样式在 Naive UI 的样式之后引入  
- @unocss/reset/tailwind-compat.css 进行修正
- 中间件统一放到core,比如常见的database,auth,middleware
- lifespan 处理器确保 Tortoise ORM 先初始化，再执行默认数据创建
- Tortoise.init() 初始化后再单独调用generate_schemas() 方法
- 图标使用必须存在，导入前请检查

**✅ 逻辑分层**
- API 层不包含复杂业务逻辑
- 不在 API 层直接写 SQL
- 业务逻辑下沉到 Service 层

**✅ 性能**
- 耗时操作（>1秒）使用异步任务
- 数据库查询使用索引
- 避免 N+1 查询问题

**✅ 安全**
- 无硬编码密码/密钥
- 敏感数据不返回前端
- SQL 使用参数化查询
- 禁止未经允许删除数据表

**✅ 代码质量**
- 核心函数有注释说明
- 变量/函数命名语义清晰
- 无重复代码

## 任务完成必要检查（单独任务执行）
- 前后端字段校验保持一致
- 检查导入是否正常
- 验证页面逻辑
- 每一个功能模块完成后端进行单元测试，并写测试脚本放置test目录下,test 收集失败案例，再针对性修复所有单元测试和集成测试，确保覆盖率 >90%。
- 前端进行eslint 格式校验
- 开发完后进行前后端联调测试,确保页面和接口一致，特别是新增功能，和页面显示
- 进行依赖包安装