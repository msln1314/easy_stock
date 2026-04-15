# QMT Service MCP 重构设计文档

## 概述

重构 qmt-service，使用 FastMCP 提供标准的 MCP 协议支持，实现 FastAPI + MCP 双接口模式。

**目标**：
- 提供真正的 MCP 协议支持（通过 SSE 传输）
- 保持现有 REST API 功能不变
- 服务层保持不变，MCP 工具直接调用服务
- 与 stock-service 实现风格保持一致

## 架构设计

### 目录结构

```
qmt-service/
├── app/
│   ├── main.py                    # FastAPI 主应用 + MCP lifespan
│   ├── mcp_server.py              # FastMCP 主实例 + 工具注册（新建）
│   ├── mcp/                       # 现有 MCP 类（保留，但不再用于路由）
│   │   ├── trade_mcp.py           # 交易 MCP 类
│   │   ├── position_mcp.py        # 持仓 MCP 类
│   │   ├── quote_mcp.py           # 行情 MCP 类
│   │   ├── factor_mcp.py          # 因子选股 MCP 类（新建）
│   │   └── router.py              # 旧路由（废弃或保留作为备用）
│   ├── services/                  # 服务层（保持不变）
│   │   ├── trade_service.py
│   │   ├── position_service.py
│   │   ├── quote_service.py
│   │   └── factor_service.py
│   ├── api/endpoints/             # REST API（保持不变）
│   └── models/                    # 数据模型（保持不变）
├── run_mcp.py                     # MCP 独立启动入口（可选，新建）
└── requirements.txt               # 添加 fastmcp 依赖
```

### 集成方式

参考 stock-service 的实现：

1. **创建 `app/mcp_server.py`**：FastMCP 主实例
2. **修改 `app/main.py`**：集成 MCP lifespan
3. **工具命名**：按模块分组，如 `trade_buy`, `position_list`

## MCP 工具定义

### 交易模块工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `trade_buy` | 买入股票 | `stock_code: str`, `price: float`, `quantity: int`, `order_type: str = "limit"` |
| `trade_sell` | 卖出股票 | `stock_code: str`, `price: float`, `quantity: int`, `order_type: str = "limit"` |
| `trade_cancel` | 撤销委托 | `order_id: str` |
| `trade_get_orders` | 查询委托列表 | `status: str = None` |
| `trade_get_order` | 查询单个委托 | `order_id: str` |

### 持仓模块工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `position_list` | 查询持仓列表 | 无 |
| `position_balance` | 查询资金余额 | 无 |
| `position_trades` | 查询成交记录 | `date: str = None`, `stock_code: str = None` |
| `position_today_trades` | 查询今日成交 | 无 |
| `position_today_entrusts` | 查询今日委托 | 无 |

### 行情模块工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `quote_get` | 获取实时行情 | `stock_code: str` |
| `quote_batch` | 批量获取行情 | `stock_codes: list` |
| `quote_kline` | 获取K线数据 | `stock_code: str`, `period: str = "1d"`, `count: int = 100`, `start_time: str = None`, `end_time: str = None` |
| `quote_minute` | 获取分时数据 | `stock_code: str`, `date: str = None` |
| `quote_depth` | 获取订单簿深度 | `stock_code: str` |
| `quote_ticks` | 获取逐笔成交 | `stock_code: str`, `start_time: str = None`, `end_time: str = None`, `count: int = 100` |
| `quote_indexes` | 获取指数行情 | `index_codes: list = None` |

### 因子选股模块工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `factor_list` | 获取因子列表 | 无 |
| `factor_screen` | 因子选股 | `factors: list` |
| `factor_get_info` | 获取因子详情 | `factor_code: str` |

## 实现细节

### mcp_server.py 核心结构

```python
from fastmcp import FastMCP

# 导入现有 MCP 单例实例
from app.mcp.trade_mcp import trade_mcp
from app.mcp.position_mcp import position_mcp
from app.mcp.quote_mcp import quote_mcp
from app.mcp.factor_mcp import factor_mcp  # 新建

# 创建 FastMCP 服务
mcp = FastMCP("qmt-service")

# 注册工具 - 直接调用 MCP 类的方法
@mcp.tool()
async def trade_buy(stock_code: str, price: float, quantity: int, order_type: str = "limit") -> dict:
    """买入股票

    Args:
        stock_code: 股票代码，如 "000001.SZ"
        price: 委托价格（市价单可传0）
        quantity: 委托数量，必须为100的整数倍
        order_type: 委托类型，"limit"为限价单，"market"为市价单

    Returns:
        包含订单信息的结果字典
    """
    return await trade_mcp.buy_stock(stock_code, price, quantity, order_type)

# ... 其他工具按同样模式注册

mcp_server = mcp
```

### main.py 集成

```python
from app.mcp_server import mcp_server

# Get MCP HTTP app with its lifespan
mcp_http_app = mcp_server.http_app()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # 初始化因子库
    from app.services.factor_service import factor_service
    await factor_service.init_factors()

    # 连接 QMT
    connected = await QMTClientManager.initialize()

    # Start MCP lifespan
    async with mcp_http_app.lifespan(app):
        yield

    # 关闭 QMT
    await QMTClientManager.close()
```

### 运行方式

1. **FastAPI + MCP 集成模式**（默认）：
   ```bash
   python run.py
   ```
   - REST API: `http://localhost:8009/api/v1/...`
   - MCP SSE: `http://localhost:8009/mcp`

2. **MCP 独立模式**（可选）：
   ```bash
   python run_mcp.py
   ```
   - MCP SSE: `http://localhost:8009/mcp`

## 依赖变更

需要在 `requirements.txt` 添加：
```
fastmcp>=3.2.0
```

## 测试策略

1. **MCP 工具测试**：验证每个工具返回格式正确
2. **集成测试**：验证 FastAPI + MCP 同时工作
3. **服务层测试**：保持现有测试不变

## 文件变更清单

| 文件 | 操作 | 说明 |
|-----|------|------|
| `app/mcp_server.py` | 新建 | FastMCP 主实例和工具注册 |
| `app/mcp/factor_mcp.py` | 新建 | 因子选股 MCP 类 |
| `app/main.py` | 修改 | 集成 MCP lifespan |
| `requirements.txt` | 修改 | 添加 fastmcp 依赖 |
| `run_mcp.py` | 新建 | MCP 独立启动入口（可选）|
| `app/mcp/router.py` | 废弃 | 旧 MCP 路由，可删除或保留备用 |

## 兼容性说明

- REST API 完全保持不变，前端无需修改
- 现有 MCP 类（`TradeMCP` 等）保留，仅修改调用方式
- 服务层完全不变，保持现有业务逻辑