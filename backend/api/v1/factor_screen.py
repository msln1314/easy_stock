"""
因子筛选API接口

从qmt_service查询数据，入库到本地数据库
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import httpx
from datetime import datetime
from tortoise.expressions import Q

from core.response import success_response
from config.settings import QMT_SERVICE_URL
from models.factor import FactorDefinition, FactorValue, FactorScreenResult, FactorCategory, PRESET_FACTORS
from core.qmt_client import qmt_client

router = APIRouter(prefix="/api/v1/factor-screen", tags=["因子筛选"])


# ==================== Schemas ====================

class FactorCondition(BaseModel):
    """因子筛选条件"""
    factor_id: str
    op: str = "gt"  # gt, lt, ge, le, eq
    value: float


class FactorScreenRequest(BaseModel):
    """因子筛选请求"""
    factors: List[FactorCondition]
    date: Optional[str] = None
    limit: int = 100


# ==================== API接口 ====================

@router.get("/factors")
async def get_factors(
    category: Optional[str] = Query(None, description="因子分类"),
    keyword: Optional[str] = Query(None, description="搜索关键词")
):
    """获取因子列表（从本地数据库）"""
    query = FactorDefinition.all()

    if category:
        query = query.filter(category=category)
    if keyword:
        query = query.filter(
            Q(factor_name__contains=keyword) | Q(factor_id__contains=keyword.upper())
        )

    factors = await query.order_by("id")

    return success_response([{
        "factor_id": f.factor_id,
        "factor_name": f.factor_name,
        "category": f.category,
        "description": f.description,
        "unit": f.unit,
        "is_active": f.is_active
    } for f in factors])


@router.get("/factors/{factor_id}")
async def get_factor(factor_id: str):
    """获取单个因子详情"""
    factor = await FactorDefinition.get_or_none(factor_id=factor_id)
    if not factor:
        raise HTTPException(status_code=404, detail="因子不存在")

    return success_response({
        "factor_id": factor.factor_id,
        "factor_name": factor.factor_name,
        "category": factor.category,
        "description": factor.description,
        "formula": factor.formula,
        "params": factor.params,
        "unit": factor.unit,
        "data_source": factor.data_source,
        "is_active": factor.is_active
    })


@router.put("/factors/{factor_id}")
async def update_factor(factor_id: str, is_active: Optional[bool] = None):
    """更新因子状态"""
    factor = await FactorDefinition.get_or_none(factor_id=factor_id)
    if not factor:
        raise HTTPException(status_code=404, detail="因子不存在")

    if is_active is not None:
        factor.is_active = is_active
        await factor.save()

    return success_response({
        "factor_id": factor.factor_id,
        "is_active": factor.is_active
    })


@router.post("/sync")
async def sync_factors():
    """从QMT同步因子库到本地数据库"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        # 先确保表存在
        from tortoise import Tortoise
        await Tortoise.generate_schemas()
        logger.info("数据库schema检查完成")

        async with httpx.AsyncClient() as client:
            # 从qmt_service获取因子列表
            logger.info(f"正在从QMT服务获取因子: {QMT_SERVICE_URL}/api/v1/factor/definitions")
            resp = await client.get(
                f"{QMT_SERVICE_URL}/api/v1/factor/definitions",
                timeout=30.0
            )
            logger.info(f"QMT服务响应状态: {resp.status_code}")

            if resp.status_code != 200:
                raise Exception(f"QMT服务返回错误: {resp.status_code}")

            data = resp.json()
            logger.info(f"QMT服务返回数据keys: {data.keys() if isinstance(data, dict) else type(data)}")

            qmt_factors = data.get("factors", [])
            logger.info(f"获取到 {len(qmt_factors)} 个因子")

        synced = 0
        for f in qmt_factors:
            try:
                factor_id = f.get("factor_id")
                factor_name = f.get("factor_name")

                if not factor_id:
                    logger.warning(f"因子缺少factor_id: {f}")
                    continue

                # 检查是否已存在
                existing = await FactorDefinition.get_or_none(factor_id=factor_id)
                if not existing:
                    # 解析分类
                    category = f.get("category", "custom")
                    if hasattr(category, 'value'):
                        category = category.value
                    try:
                        cat_enum = FactorCategory(category)
                    except ValueError:
                        cat_enum = FactorCategory.CUSTOM

                    await FactorDefinition.create(
                        factor_id=factor_id,
                        factor_name=factor_name or factor_id,
                        category=cat_enum,
                        description=f.get("description", "") or "",
                        formula=f.get("formula") or None,
                        params=f.get("params"),
                        unit=f.get("unit", "") or "",
                        data_source=f.get("data_source", "QMT"),
                        is_builtin=True,
                        is_active=True
                    )
                    synced += 1
                    logger.info(f"同步因子: {factor_id} - {factor_name}")
            except Exception as e:
                logger.error(f"同步单个因子失败: {e}")
                continue

        total = await FactorDefinition.all().count()
        return success_response({
            "synced": synced,
            "total": total,
            "message": f"同步完成，新增 {synced} 个因子，共 {total} 个"
        })

    except httpx.ConnectError as e:
        logger.error(f"QMT服务连接失败: {e}")
        return await _init_preset_factors()
    except Exception as e:
        logger.error(f"同步失败: {e}\n{traceback.format_exc()}")
        return await _init_preset_factors()


async def _init_preset_factors():
    """使用预置因子初始化"""
    import logging
    logger = logging.getLogger(__name__)

    synced = 0
    errors = []
    for f in PRESET_FACTORS:
        try:
            existing = await FactorDefinition.get_or_none(factor_id=f["factor_id"])
            if not existing:
                await FactorDefinition.create(
                    factor_id=f["factor_id"],
                    factor_name=f["factor_name"],
                    category=f["category"],
                    description=f.get("description", "") or "",
                    formula=f.get("formula") or None,
                    params=f.get("params"),
                    unit=f.get("unit", "") or "",
                    data_source=f.get("data_source", "PRESET"),
                    is_builtin=True,
                    is_active=True
                )
                synced += 1
                logger.info(f"初始化预置因子: {f['factor_id']}")
        except Exception as e:
            errors.append(f"{f.get('factor_id')}: {str(e)}")
            logger.error(f"初始化预置因子失败 {f.get('factor_id')}: {e}")
            continue

    total = await FactorDefinition.all().count()
    msg = f"使用预置数据初始化，新增 {synced} 个因子，共 {total} 个"
    if errors:
        msg += f"，部分失败: {len(errors)} 个"
    return success_response({
        "synced": synced,
        "total": total,
        "message": msg,
        "errors": errors[:5] if errors else []
    })


@router.post("/init")
async def init_factors():
    """初始化预置因子到数据库"""
    return await _init_preset_factors()


@router.get("/categories")
async def get_categories():
    """获取因子分类列表"""
    categories = [
        {"key": "trend", "name": "趋势因子", "description": "均线、趋势类指标"},
        {"key": "momentum", "name": "动量因子", "description": "RSI、KDJ、动量等"},
        {"key": "volatility", "name": "波动因子", "description": "ATR、波动率等"},
        {"key": "volume", "name": "成交量因子", "description": "量比、换手率等"},
        {"key": "value", "name": "价值因子", "description": "PE、PB、PS等"},
        {"key": "growth", "name": "成长因子", "description": "营收增长、利润增长等"},
        {"key": "quality", "name": "质量因子", "description": "ROE、ROA、毛利率等"},
        {"key": "sentiment", "name": "情绪因子", "description": "成交额、振幅等"},
        {"key": "custom", "name": "自定义因子", "description": "用户自定义因子"},
    ]
    return success_response(categories)


@router.post("/screen")
async def screen_stocks(request: FactorScreenRequest):
    """
    因子选股 - 多因子筛选

    所有条件必须全部满足（AND逻辑）
    """
    date_str = request.date or datetime.now().strftime("%Y%m%d")

    try:
        async with httpx.AsyncClient() as client:
            # 调用qmt_service进行选股
            resp = await client.post(
                f"{QMT_SERVICE_URL}/api/v1/factor/screen",
                json={
                    "factors": [f.dict() for f in request.factors],
                    "date": date_str,
                    "limit": request.limit
                },
                timeout=120.0
            )
            data = resp.json()
            stocks = data.get("stocks", [])

        # 获取股票价格
        stock_codes = [s.get("stock_code", "") for s in stocks if s.get("stock_code")]
        price_map: Dict[str, float] = {}

        if stock_codes:
            try:
                for code in stock_codes[:50]:  # 限制并发查询数量
                    try:
                        quote = await qmt_client.get_stock_quote(code)
                        price_map[code] = quote.get("lastPrice", 0) or quote.get("price", 0)
                    except Exception:
                        price_map[code] = 0
            except Exception:
                pass

        # 保存选股结果到数据库并添加价格
        for stock in stocks:
            stock_code = stock.get("stock_code", "")
            # 添加价格字段
            stock["price"] = price_map.get(stock_code, 0)

            await FactorScreenResult.create(
                screen_date=date_str,
                stock_code=stock_code,
                stock_name=stock.get("stock_name", ""),
                score=stock.get("score", 0),
                factor_values=stock.get("factor_values", {}),
                conditions=[f.dict() for f in request.factors]
            )

        return success_response({
            "date": date_str,
            "stocks": stocks,
            "count": len(stocks)
        })

    except httpx.ConnectError:
        return success_response({
            "date": date_str,
            "stocks": [],
            "count": 0,
            "message": "QMT服务不可用，请确保qmt_service正在运行"
        })


@router.get("/values/{factor_id}")
async def get_factor_values(
    factor_id: str,
    stock_codes: List[str] = Query(..., description="股票代码列表"),
    date: Optional[str] = Query(None, description="日期")
):
    """获取因子值（从qmt_service查询）"""
    date_str = date or datetime.now().strftime("%Y%m%d")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{QMT_SERVICE_URL}/api/v1/factor/values/{factor_id}",
                params={"stock_codes": stock_codes, "date": date_str},
                timeout=30.0
            )
            data = resp.json()

        return success_response(data)

    except httpx.ConnectError:
        return success_response({
            "factor_id": factor_id,
            "date": date_str,
            "values": [],
            "count": 0,
            "message": "QMT服务不可用"
        })


@router.get("/history")
async def get_screen_history(
    date: Optional[str] = Query(None, description="筛选日期"),
    limit: int = Query(20, ge=1, le=100)
):
    """获取历史选股结果"""
    query = FactorScreenResult.all()

    if date:
        query = query.filter(screen_date=date)

    results = await query.order_by("-created_at").limit(limit)

    return success_response([{
        "id": r.id,
        "screen_date": r.screen_date,
        "stock_code": r.stock_code,
        "stock_name": r.stock_name,
        "score": r.score,
        "factor_values": r.factor_values,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for r in results])