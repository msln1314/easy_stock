"""
策略业务逻辑服务
"""
from typing import Optional, List, Dict
from tortoise.expressions import Q
from models.strategy import Strategy
from models.indicator import StrategyIndicator
from models.signal import StrategySignal
from models.risk import StrategyRisk
from schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyResponse,
    StrategyListResponse, PaginatedResponse, StrategyStatsResponse,
    IndicatorCreate, SignalCreate, RiskCreate
)


class StrategyService:
    """策略服务"""

    async def create_strategy(self, data: StrategyCreate) -> Strategy:
        """创建策略（包含级联创建指标、信号、风控）"""
        # 创建策略主表
        strategy = await Strategy.create(
            name=data.name,
            description=data.description,
            execute_mode=data.execute_mode,
            status=data.status
        )

        # 创建指标配置
        for indicator_data in data.indicators:
            await StrategyIndicator.create(
                strategy_id=strategy.id,
                indicator_type=indicator_data.indicator_type,
                parameters=indicator_data.parameters
            )

        # 创建信号规则
        for signal_data in data.signals:
            await StrategySignal.create(
                strategy_id=strategy.id,
                signal_type=signal_data.signal_type,
                condition_type=signal_data.condition_type,
                condition_config=signal_data.condition_config,
                priority=signal_data.priority
            )

        # 创建风控配置
        if data.risk:
            await StrategyRisk.create(
                strategy_id=strategy.id,
                stop_profit_type=data.risk.stop_profit_type,
                stop_profit_value=data.risk.stop_profit_value,
                stop_loss_type=data.risk.stop_loss_type,
                stop_loss_value=data.risk.stop_loss_value,
                max_position=data.risk.max_position
            )

        return strategy

    async def get_strategy_detail(self, strategy_id: int) -> Optional[StrategyResponse]:
        """获取策略详情"""
        strategy = await Strategy.get_or_none(id=strategy_id)
        if not strategy:
            return None

        # 获取关联数据
        indicators = await StrategyIndicator.filter(strategy_id=strategy_id).all()
        signals = await StrategySignal.filter(strategy_id=strategy_id).all()
        risk = await StrategyRisk.get_or_none(strategy_id=strategy_id)

        return StrategyResponse(
            id=strategy.id,
            name=strategy.name,
            description=strategy.description,
            execute_mode=strategy.execute_mode,
            status=strategy.status,
            indicators=[{
                "id": ind.id,
                "indicator_type": ind.indicator_type,
                "parameters": ind.parameters
            } for ind in indicators],
            signals=[{
                "id": sig.id,
                "signal_type": sig.signal_type,
                "condition_type": sig.condition_type,
                "condition_config": sig.condition_config,
                "priority": sig.priority
            } for sig in signals],
            risk={
                "id": risk.id,
                "stop_profit_type": risk.stop_profit_type,
                "stop_profit_value": float(risk.stop_profit_value) if risk.stop_profit_value else None,
                "stop_loss_type": risk.stop_loss_type,
                "stop_loss_value": float(risk.stop_loss_value) if risk.stop_loss_value else None,
                "max_position": float(risk.max_position) if risk.max_position else None
            } if risk else None,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at
        )

    async def get_strategies(
        self,
        execute_mode: Optional[str] = None,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse:
        """获取策略列表"""
        # 构建查询条件
        query = Strategy.all()
        if execute_mode:
            query = query.filter(execute_mode=execute_mode)
        if status:
            query = query.filter(status=status)
        if keyword:
            query = query.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))

        # 获取总数
        total = await query.count()

        # 分页查询
        strategies = await query.offset((page - 1) * page_size).limit(page_size).all()

        return PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[StrategyListResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                execute_mode=s.execute_mode,
                status=s.status,
                created_at=s.created_at,
                updated_at=s.updated_at
            ) for s in strategies]
        )

    async def update_strategy(self, strategy_id: int, data: StrategyUpdate) -> Optional[Strategy]:
        """更新策略"""
        strategy = await Strategy.get_or_none(id=strategy_id)
        if not strategy:
            return None

        # 更新基础字段
        update_data = data.dict(exclude_unset=True, exclude={"indicators", "signals", "risk"})
        if update_data:
            await Strategy.filter(id=strategy_id).update(**update_data)

        # 更新指标（先删后增）
        if data.indicators is not None:
            await StrategyIndicator.filter(strategy_id=strategy_id).delete()
            for indicator_data in data.indicators:
                await StrategyIndicator.create(
                    strategy_id=strategy_id,
                    indicator_type=indicator_data.indicator_type,
                    parameters=indicator_data.parameters
                )

        # 更新信号（先删后增）
        if data.signals is not None:
            await StrategySignal.filter(strategy_id=strategy_id).delete()
            for signal_data in data.signals:
                await StrategySignal.create(
                    strategy_id=strategy_id,
                    signal_type=signal_data.signal_type,
                    condition_type=signal_data.condition_type,
                    condition_config=signal_data.condition_config,
                    priority=signal_data.priority
                )

        # 更新风控
        if data.risk is not None:
            await StrategyRisk.filter(strategy_id=strategy_id).delete()
            await StrategyRisk.create(
                strategy_id=strategy_id,
                stop_profit_type=data.risk.stop_profit_type,
                stop_profit_value=data.risk.stop_profit_value,
                stop_loss_type=data.risk.stop_loss_type,
                stop_loss_value=data.risk.stop_loss_value,
                max_position=data.risk.max_position
            )

        return await Strategy.get(id=strategy_id)

    async def delete_strategy(self, strategy_id: int) -> bool:
        """删除策略（级联删除关联数据）"""
        strategy = await Strategy.get_or_none(id=strategy_id)
        if not strategy:
            return False

        # Tortoise-ORM的外键ON_DELETE=CASCADE会自动级联删除
        await strategy.delete()
        return True

    async def update_status(self, strategy_id: int, status: str) -> Optional[Strategy]:
        """更新策略状态"""
        strategy = await Strategy.get_or_none(id=strategy_id)
        if not strategy:
            return None

        strategy.status = status
        await strategy.save()
        return strategy

    async def get_stats(self) -> StrategyStatsResponse:
        """获取统计信息"""
        total = await Strategy.all().count()

        # 按执行模式统计
        auto_count = await Strategy.filter(execute_mode="auto").count()
        alert_count = await Strategy.filter(execute_mode="alert").count()
        simulate_count = await Strategy.filter(execute_mode="simulate").count()

        # 按状态统计
        running_count = await Strategy.filter(status="running").count()
        paused_count = await Strategy.filter(status="paused").count()
        stopped_count = await Strategy.filter(status="stopped").count()

        return StrategyStatsResponse(
            total=total,
            by_execute_mode={
                "auto": auto_count,
                "alert": alert_count,
                "simulate": simulate_count
            },
            by_status={
                "running": running_count,
                "paused": paused_count,
                "stopped": stopped_count
            }
        )