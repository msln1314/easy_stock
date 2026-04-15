# QMT Service MCP 重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 qmt-service 使用 FastMCP 提供标准 MCP 协议支持，实现 FastAPI + MCP 双接口模式。

**Architecture:** 创建 mcp_server.py 作为 FastMCP 主实例，导入现有 MCP 单例类注册工具，修改 main.py 集成 MCP lifespan。服务层保持不变。

**Tech Stack:** FastAPI, FastMCP (>=3.2.0), Pydantic, SSE

---

## File Structure

```
qmt-service/
├── pyproject.toml                # 修改：添加 fastmcp 依赖
├── app/
│   ├── main.py                   # 修改：集成 MCP lifespan
│   ├── mcp_server.py             # 新建：FastMCP 主实例 + 20个工具注册
│   ├── mcp/
│   │   ├── factor_mcp.py         # 新建：因子选股 MCP 类
│   │   └── router.py             # 保留但不使用（可后续删除）
│   └── services/                 # 不变
│   └── api/                      # 不变
├── run_mcp.py                    # 新建：MCP 独立启动入口（可选）
└── tests/
    └── test_mcp_tools.py         # 新建：MCP 工具测试
```

---

### Task 1: 添加 fastmcp 依赖

**Files:**
- Modify: `qmt-service/pyproject.toml:7-14`

- [ ] **Step 1: 修改 pyproject.toml 添加 fastmcp 依赖**

```python
# 文件: qmt-service/pyproject.toml
# 修改 dependencies 数组，添加 fastmcp

[project]
name = "qmt-service"
version = "1.0.0"
description = "QMT量化交易服务"
requires-python = ">=3.10"

dependencies = [
    "fastapi>=0.101.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "redis>=4.5.0",
    "python-dotenv>=1.0.0",
    "fastmcp>=3.2.0",  # 新增
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "httpx>=0.24.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 2: Commit**

```bash
cd qmt-service && git add pyproject.toml && git commit -m "chore: add fastmcp dependency"
```

---

### Task 2: 创建因子选股 MCP 类

**Files:**
- Create: `qmt-service/app/mcp/factor_mcp.py`

- [ ] **Step 1: 创建 factor_mcp.py 文件**

```python
# 文件: qmt-service/app/mcp/factor_mcp.py
"""
因子选股MCP接口

提供因子列表、因子选股等功能的MCP封装
"""
import logging
from typing import Dict, List, Optional

from app.services.factor_service import factor_service

logger = logging.getLogger(__name__)


class FactorMCP:
    """
    因子选股MCP接口

    提供因子查询和选股功能。

    使用示例:
        factor_mcp = FactorMCP()
        factors = await factor_mcp.get_factor_list()
    """

    async def get_factor_list(
        self,
        category: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict:
        """
        获取因子列表

        Args:
            category: 因子类别筛选，如 "trend", "momentum", "volatility" 等
            keyword: 关键词搜索

        Returns:
            Dict: 因子列表
                - factors: 因子定义列表，每个包含:
                    - factor_id: 因子ID
                    - factor_name: 因子名称
                    - category: 类别
                    - description: 描述
                    - formula: 公式
                    - unit: 单位
                - total: 总数量

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取因子列表, category={category}, keyword={keyword}")
        try:
            result = await factor_service.get_factor_definitions(
                category=category,
                keyword=keyword
            )
            return {
                "factors": [f.model_dump() for f in result.factors],
                "total": result.total
            }
        except Exception as e:
            logger.error(f"获取因子列表失败: {str(e)}")
            raise Exception(f"获取因子列表失败: {str(e)}")

    async def get_factor_info(self, factor_id: str) -> Optional[Dict]:
        """
        获取单个因子详情

        Args:
            factor_id: 因子ID，如 "MA5", "PE", "RSI6" 等

        Returns:
            Dict: 因子详情，不存在则返回None

        Raises:
            Exception: 当查询失败时抛出
        """
        logger.info(f"MCP获取因子详情: {factor_id}")
        try:
            factor = await factor_service.get_factor_definition(factor_id)
            if factor:
                return factor.model_dump()
            return None
        except Exception as e:
            logger.error(f"获取因子详情失败: {str(e)}")
            raise Exception(f"获取因子详情失败: {str(e)}")

    async def screen_stocks(
        self,
        factors: List[Dict],
        date: Optional[str] = None,
        limit: int = 50
    ) -> Dict:
        """
        因子选股

        Args:
            factors: 筛选条件列表，每个条件包含:
                - factor_id: 因子ID
                - op: 操作符，可选 gt(大于), lt(小于), ge(大于等于), le(小于等于), eq(等于)
                - value: 阈值
            date: 日期，格式YYYYMMDD，不传则使用今日
            limit: 返回数量限制

        Returns:
            Dict: 选股结果
                - date: 日期
                - stocks: 股票列表，每个包含:
                    - stock_code: 股票代码
                    - stock_name: 股票名称
                    - score: 综合得分
                    - factor_values: 各因子值
                - count: 数量

        Raises:
            Exception: 当选股失败时抛出
        """
        logger.info(f"MCP因子选股, factors={len(factors)}, date={date}")
        try:
            from app.models.factor_models import FactorScreenRequest
            request = FactorScreenRequest(
                factors=factors,
                date=date,
                limit=limit
            )
            result = await factor_service.screen_stocks(request)
            return {
                "date": result.date,
                "stocks": [s.model_dump() for s in result.stocks],
                "count": result.count
            }
        except Exception as e:
            logger.error(f"因子选股失败: {str(e)}")
            raise Exception(f"因子选股失败: {str(e)}")


# 单例
factor_mcp = FactorMCP()
```

- [ ] **Step 2: Commit**

```bash
cd qmt-service && git add app/mcp/factor_mcp.py && git commit -m "feat: add factor_mcp class for MCP tools"
```

---

### Task 3: 创建 FastMCP 主实例 (mcp_server.py)

**Files:**
- Create: `qmt-service/app/mcp_server.py`

- [ ] **Step 1: 创建 mcp_server.py - 导入部分和 MCP 实例**

```python
# 文件: qmt-service/app/mcp_server.py
"""
MCP Server - FastMCP implementation for qmt-service

提供真正的 MCP 协议支持，使用 SSE (Server-Sent Events) 传输。
"""

from fastmcp import FastMCP

# 导入现有 MCP 单例实例
from app.mcp.trade_mcp import trade_mcp
from app.mcp.position_mcp import position_mcp
from app.mcp.quote_mcp import quote_mcp
from app.mcp.factor_mcp import factor_mcp

# Create FastMCP server
mcp = FastMCP("qmt-service")


# ==================== Trade Tools ====================
```

- [ ] **Step 2: 添加交易工具注册**

```python
# 继续文件: qmt-service/app/mcp_server.py
# 在 "# ==================== Trade Tools ====================" 后添加

@mcp.tool()
async def trade_buy(
    stock_code: str,
    price: float,
    quantity: int,
    order_type: str = "limit"
) -> dict:
    """买入股票

    Args:
        stock_code: 股票代码，如 "000001.SZ"
        price: 委托价格（市价单可传0）
        quantity: 委托数量，必须为100的整数倍
        order_type: 委托类型，"limit"为限价单，"market"为市价单

    Returns:
        包含订单信息的结果字典，包括order_id、stock_code、status等
    """
    return await trade_mcp.buy_stock(stock_code, price, quantity, order_type)


@mcp.tool()
async def trade_sell(
    stock_code: str,
    price: float,
    quantity: int,
    order_type: str = "limit"
) -> dict:
    """卖出股票

    Args:
        stock_code: 股票代码
        price: 委托价格（市价单可传0）
        quantity: 委托数量，必须为100的整数倍
        order_type: 委托类型，"limit"或"market"

    Returns:
        包含订单信息的结果字典
    """
    return await trade_mcp.sell_stock(stock_code, price, quantity, order_type)


@mcp.tool()
async def trade_cancel(order_id: str) -> dict:
    """撤销委托订单

    Args:
        order_id: 订单ID

    Returns:
        撤单结果，包含order_id、success、message
    """
    return await trade_mcp.cancel_order(order_id)


@mcp.tool()
async def trade_get_orders(status: str = None) -> list:
    """查询委托订单列表

    Args:
        status: 可选的状态筛选，如 "pending", "filled", "cancelled"

    Returns:
        委托订单列表
    """
    return await trade_mcp.get_orders(status)


@mcp.tool()
async def trade_get_order(order_id: str) -> dict:
    """查询单个委托订单

    Args:
        order_id: 订单ID

    Returns:
        订单详情，不存在则返回null
    """
    result = await trade_mcp.get_order(order_id)
    return result if result else None
```

- [ ] **Step 3: 添加持仓工具注册**

```python
# 继续文件: qmt-service/app/mcp_server.py
# 在交易工具后添加

# ==================== Position Tools ====================

@mcp.tool()
async def position_list() -> dict:
    """查询持仓列表

    Returns:
        持仓信息，包含positions列表、total_market_value、total_profit等
    """
    return await position_mcp.get_positions()


@mcp.tool()
async def position_balance() -> dict:
    """查询资金余额

    Returns:
        资金信息，包含total_asset、available_cash、market_value等
    """
    return await position_mcp.get_balance()


@mcp.tool()
async def position_trades(
    date: str = None,
    stock_code: str = None
) -> dict:
    """查询成交记录

    Args:
        date: 日期筛选，格式YYYYMMDD
        stock_code: 股票代码筛选

    Returns:
        成交记录列表
    """
    return await position_mcp.get_trades(date, stock_code)


@mcp.tool()
async def position_today_trades() -> dict:
    """查询今日成交记录

    Returns:
        今日成交记录列表
    """
    return await position_mcp.get_today_trades()


@mcp.tool()
async def position_today_entrusts() -> dict:
    """查询今日委托

    Returns:
        今日委托记录列表
    """
    return await position_mcp.get_today_entrusts()
```

- [ ] **Step 4: 添加行情工具注册**

```python
# 继续文件: qmt-service/app/mcp_server.py
# 在持仓工具后添加

# ==================== Quote Tools ====================

@mcp.tool()
async def quote_get(stock_code: str) -> dict:
    """获取单只股票实时行情

    Args:
        stock_code: 股票代码，如 "000001.SZ"

    Returns:
        实时行情数据，包含price、open、high、low、volume等
    """
    result = await quote_mcp.get_quote(stock_code)
    return result if result else {"error": "未找到行情数据"}


@mcp.tool()
async def quote_batch(stock_codes: list) -> dict:
    """批量获取实时行情

    Args:
        stock_codes: 股票代码列表

    Returns:
        批量行情数据，包含quotes列表和count
    """
    return await quote_mcp.get_quotes(stock_codes)


@mcp.tool()
async def quote_kline(
    stock_code: str,
    period: str = "1d",
    count: int = 100,
    start_time: str = None,
    end_time: str = None
) -> dict:
    """获取K线数据

    Args:
        stock_code: 股票代码
        period: 周期，可选 1d/1w/1m/5m/15m/30m/60m
        count: 返回条数
        start_time: 开始时间
        end_time: 结束时间

    Returns:
        K线数据，包含klines列表
    """
    return await quote_mcp.get_kline(stock_code, period, count, start_time, end_time)


@mcp.tool()
async def quote_minute(
    stock_code: str,
    date: str = None
) -> dict:
    """获取分时数据

    Args:
        stock_code: 股票代码
        date: 日期，格式YYYYMMDD，不传则获取今日

    Returns:
        分时数据列表
    """
    return await quote_mcp.get_minute_bars(stock_code, date)


@mcp.tool()
async def quote_depth(stock_code: str) -> dict:
    """获取订单簿深度

    Args:
        stock_code: 股票代码

    Returns:
        订单簿深度数据，包含bid_levels和ask_levels
    """
    return await quote_mcp.get_depth(stock_code)


@mcp.tool()
async def quote_ticks(
    stock_code: str,
    start_time: str = None,
    end_time: str = None,
    count: int = 100
) -> dict:
    """获取逐笔成交数据

    Args:
        stock_code: 股票代码
        start_time: 开始时间
        end_time: 结束时间
        count: 返回条数

    Returns:
        逐笔成交数据列表
    """
    return await quote_mcp.get_ticks(stock_code, start_time, end_time, count)


@mcp.tool()
async def quote_indexes(index_codes: list = None) -> dict:
    """获取主要指数行情

    Args:
        index_codes: 指数代码列表，如 ['sh', 'sz', 'cy', 'hs300']，不传则获取所有主要指数

    Returns:
        指数行情数据列表
    """
    return await quote_mcp.get_index_quotes(index_codes)
```

- [ ] **Step 5: 添加因子工具注册和导出**

```python
# 继续文件: qmt-service/app/mcp_server.py
# 在行情工具后添加

# ==================== Factor Tools ====================

@mcp.tool()
async def factor_list(
    category: str = None,
    keyword: str = None
) -> dict:
    """获取因子列表

    Args:
        category: 因子类别筛选，如 "trend", "momentum", "volatility"
        keyword: 关键词搜索

    Returns:
        因子列表，包含factors和total
    """
    return await factor_mcp.get_factor_list(category, keyword)


@mcp.tool()
async def factor_screen(
    factors: list,
    date: str = None,
    limit: int = 50
) -> dict:
    """因子选股

    Args:
        factors: 筛选条件列表，每个包含factor_id、op、value
        date: 日期，格式YYYYMMDD，不传则使用今日
        limit: 返回数量限制

    Returns:
        选股结果，包含stocks列表
    """
    return await factor_mcp.screen_stocks(factors, date, limit)


@mcp.tool()
async def factor_get_info(factor_id: str) -> dict:
    """获取因子详情

    Args:
        factor_id: 因子ID，如 "MA5", "PE", "RSI6"

    Returns:
        因子详情字典，不存在则返回null
    """
    result = await factor_mcp.get_factor_info(factor_id)
    return result if result else None


# Export for use in main.py
mcp_server = mcp
```

- [ ] **Step 6: Commit**

```bash
cd qmt-service && git add app/mcp_server.py && git commit -m "feat: create FastMCP server with 20 MCP tools"
```

---

### Task 4: 修改 main.py 集成 MCP

**Files:**
- Modify: `qmt-service/app/main.py`

- [ ] **Step 1: 添加 MCP 导入和获取 HTTP app**

在文件开头导入部分添加：

```python
# 文件: qmt-service/app/main.py
# 在现有导入后添加（约第10行）

from app.mcp_server import mcp_server

# Get MCP HTTP app with its lifespan
mcp_http_app = mcp_server.http_app()
```

- [ ] **Step 2: 修改 lifespan 函数集成 MCP**

替换整个 lifespan 函数：

```python
# 文件: qmt-service/app/main.py
# 替换 lifespan 函数（约第19-42行）

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - combines MCP lifespan"""
    # 启动时
    logger.info(f"正在启动 {settings.PROJECT_NAME}...")

    # 初始化因子库
    from app.services.factor_service import factor_service
    await factor_service.init_factors()
    logger.info(f"因子库加载完成，共 {len(factor_service._factor_cache)} 个因子")

    # 连接 QMT
    connected = await QMTClientManager.initialize()
    if connected:
        logger.info("QMT客户端连接成功")
    else:
        logger.warning("QMT客户端未连接，使用模拟模式")

    # Start MCP lifespan
    async with mcp_http_app.lifespan(app):
        logger.info("MCP Server started")
        yield
        logger.info("MCP Server stopped")

    # 关闭时
    logger.info("正在关闭服务...")
    await QMTClientManager.close()
    logger.info("服务已关闭")
```

- [ ] **Step 3: 更新 root 路径返回 MCP 信息**

```python
# 文件: qmt-service/app/main.py
# 修改 root 函数（约第77-84行）

@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "message": settings.PROJECT_NAME,
        "docs": "/docs",
        "mcp_endpoint": "/mcp",
        "qmt_status": "connected" if QMTClientManager.is_connected() else "mock"
    }
```

- [ ] **Step 4: Commit**

```bash
cd qmt-service && git add app/main.py && git commit -m "feat: integrate FastMCP into FastAPI lifespan"
```

---

### Task 5: 创建 MCP 独立启动入口（可选）

**Files:**
- Create: `qmt-service/run_mcp.py`

- [ ] **Step 1: 创建 run_mcp.py**

```python
# 文件: qmt-service/run_mcp.py
"""
MCP Server 独立启动入口

仅启动 MCP 服务，不启动 FastAPI REST API。
"""
import asyncio
import logging

from app.core.config import settings
from app.core.qmt_client import QMTClientManager
from app.services.factor_service import factor_service
from app.mcp_server import mcp_server

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """启动 MCP Server"""
    logger.info("正在启动 MCP Server...")

    # 初始化因子库
    await factor_service.init_factors()
    logger.info(f"因子库加载完成，共 {len(factor_service._factor_cache)} 个因子")

    # 连接 QMT
    connected = await QMTClientManager.initialize()
    if connected:
        logger.info("QMT客户端连接成功")
    else:
        logger.warning("QMT客户端未连接，使用模拟模式")

    # 运行 MCP HTTP server
    logger.info(f"MCP Server 运行在 http://{settings.SERVICE_HOST}:{settings.SERVICE_PORT}/mcp")
    await mcp_server.run_http_async(
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT
    )

    # 关闭
    await QMTClientManager.close()
    logger.info("服务已关闭")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Commit**

```bash
cd qmt-service && git add run_mcp.py && git commit -m "feat: add MCP standalone entry point"
```

---

### Task 6: 创建 MCP 工具测试

**Files:**
- Create: `qmt-service/tests/test_mcp_tools.py`

- [ ] **Step 1: 创建测试文件**

```python
# 文件: qmt-service/tests/test_mcp_tools.py
"""
MCP 工具测试

验证 MCP 工具函数的返回格式正确。
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.mcp_server import mcp


class TestMCPToolsRegistration:
    """测试 MCP 工具是否正确注册"""

    def test_mcp_server_created(self):
        """验证 MCP server 实例创建成功"""
        assert mcp is not None
        assert mcp.name == "qmt-service"

    def test_trade_tools_registered(self):
        """验证交易工具注册"""
        # FastMCP 内部存储工具信息
        # 通过检查工具是否可调用来验证
        tools = mcp._tool_manager._tools
        expected_trade_tools = [
            "trade_buy", "trade_sell", "trade_cancel",
            "trade_get_orders", "trade_get_order"
        ]
        for tool_name in expected_trade_tools:
            assert tool_name in tools, f"工具 {tool_name} 未注册"

    def test_position_tools_registered(self):
        """验证持仓工具注册"""
        tools = mcp._tool_manager._tools
        expected_position_tools = [
            "position_list", "position_balance", "position_trades",
            "position_today_trades", "position_today_entrusts"
        ]
        for tool_name in expected_position_tools:
            assert tool_name in tools, f"工具 {tool_name} 未注册"

    def test_quote_tools_registered(self):
        """验证行情工具注册"""
        tools = mcp._tool_manager._tools
        expected_quote_tools = [
            "quote_get", "quote_batch", "quote_kline",
            "quote_minute", "quote_depth", "quote_ticks", "quote_indexes"
        ]
        for tool_name in expected_quote_tools:
            assert tool_name in tools, f"工具 {tool_name} 未注册"

    def test_factor_tools_registered(self):
        """验证因子工具注册"""
        tools = mcp._tool_manager._tools
        expected_factor_tools = [
            "factor_list", "factor_screen", "factor_get_info"
        ]
        for tool_name in expected_factor_tools:
            assert tool_name in tools, f"工具 {tool_name} 未注册"


class TestFactorMCPTools:
    """测试因子 MCP 工具"""

    @pytest.mark.asyncio
    async def test_factor_list(self):
        """测试获取因子列表"""
        # 需要先初始化因子库
        from app.services.factor_service import factor_service
        await factor_service.init_factors()

        result = await factor_mcp.get_factor_list()
        assert "factors" in result
        assert "total" in result
        assert result["total"] > 0

    @pytest.mark.asyncio
    async def test_factor_get_info(self):
        """测试获取因子详情"""
        from app.services.factor_service import factor_service
        await factor_service.init_factors()

        result = await factor_mcp.get_factor_info("MA5")
        assert result is not None
        assert result["factor_id"] == "MA5"
        assert result["factor_name"] == "5日均线"


# 导入用于测试
from app.mcp.factor_mcp import factor_mcp
```

- [ ] **Step 2: Commit**

```bash
cd qmt-service && git add tests/test_mcp_tools.py && git commit -m "test: add MCP tools registration tests"
```

---

### Task 7: 运行测试验证

- [ ] **Step 1: 安装依赖**

```bash
cd qmt-service && pip install -e . && pip install pytest pytest-asyncio
```

- [ ] **Step 2: 运行测试**

```bash
cd qmt-service && pytest tests/test_mcp_tools.py -v
```

Expected output:
```
test_mcp_server_created PASSED
test_trade_tools_registered PASSED
test_position_tools_registered PASSED
test_quote_tools_registered PASSED
test_factor_tools_registered PASSED
```

---

### Task 8: 最终提交

- [ ] **Step 1: 创建最终提交**

```bash
cd qmt-service && git add -A && git commit -m "$(cat <<'EOF'
feat: 完成 QMT Service MCP 重构

- 添加 fastmcp>=3.2.0 依赖
- 创建 factor_mcp.py 因子选股 MCP 类
- 创建 mcp_server.py FastMCP 主实例（20个工具）
- 修改 main.py 集成 MCP lifespan
- 创建 run_mcp.py MCP 独立启动入口
- 添加 MCP 工具注册测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Checklist

**1. Spec coverage:**
- ✅ Task 1: 添加 fastmcp 依赖
- ✅ Task 2: 创建因子选股 MCP 类
- ✅ Task 3: 创建 FastMCP 主实例（20个工具）
- ✅ Task 4: 修改 main.py 集成 MCP lifespan
- ✅ Task 5: 创建 MCP 独立启动入口
- ✅ Task 6: 创建 MCP 工具测试
- ✅ Task 7: 运行测试验证

**2. Placeholder scan:**
- 无 TBD、TODO、implement later
- 所有代码步骤都有完整代码

**3. Type consistency:**
- 所有工具函数返回 dict 或 list
- 参数命名与设计文档一致