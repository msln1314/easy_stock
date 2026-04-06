"""
选股策略相关模型

选股策略：定义选股规则和参数
策略追踪异动池：记录策略产生的股票信息
"""
from tortoise import fields
from tortoise.models import Model
from datetime import datetime, timedelta


class StockPickStrategy(Model):
    """
    选股策略表

    定义选股规则，可定时执行生成股票池
    """
    id = fields.IntField(pk=True, description="主键ID")
    strategy_key = fields.CharField(max_length=50, unique=True, description="策略KEY")
    strategy_name = fields.CharField(max_length=100, description="策略名称")
    strategy_type = fields.CharField(
        max_length=50,
        default="technical",
        description="策略类型: technical-技术指标, factor-因子, pattern-形态, combination-组合"
    )
    description = fields.TextField(null=True, description="策略描述")

    # 策略配置
    strategy_config = fields.JSONField(description="策略配置JSON")
    # 示例: {
    #   "indicators": [{"type": "MA", "params": {"period": 5}}, {"type": "MACD", "params": {}}],
    #   "conditions": [{"field": "ma5", "op": ">", "value": "ma10"}],
    #   "filters": [{"field": "volume_ratio", "op": ">", "value": 1.5}]
    # }

    # 时间配置
    duration_days = fields.IntField(default=3, description="持续时间(天)")
    generate_time = fields.CharField(
        max_length=20,
        default="09:00",
        description="每日生成时间 HH:mm"
    )
    advance_days = fields.IntField(default=1, description="提前生成天数(0=当天,1=提前1天)")

    # 执行配置
    is_active = fields.BooleanField(default=True, description="是否启用")
    auto_generate = fields.BooleanField(default=True, description="是否自动生成")

    # 统计信息
    total_generated = fields.IntField(default=0, description="累计生成股票数")
    success_rate = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        description="策略成功率(%)"
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "stock_pick_strategies"
        indexes = [
            ("strategy_key",),
            ("is_active",),
            ("strategy_type",),
        ]

    def __str__(self):
        return f"{self.strategy_key} - {self.strategy_name}"

    @property
    def strategy_type_display(self) -> str:
        """策略类型显示文本"""
        type_map = {
            "technical": "技术指标",
            "factor": "因子选股",
            "pattern": "形态识别",
            "combination": "组合策略"
        }
        return type_map.get(self.strategy_type, self.strategy_type)


class StrategyTrackPool(Model):
    """
    策略追踪异动池

    记录选股策略产生的股票信息，支持多日股池
    """
    id = fields.IntField(pk=True, description="主键ID")

    # 关联策略
    strategy = fields.ForeignKeyField(
        "models.StockPickStrategy",
        on_delete=fields.CASCADE,
        related_name="track_records",
        description="选股策略ID"
    )
    strategy_key = fields.CharField(max_length=50, description="策略KEY(冗余)")

    # 股票信息
    stock_code = fields.CharField(max_length=20, description="股票代码")
    stock_name = fields.CharField(max_length=50, null=True, description="股票名称")

    # 生成信息
    generate_date = fields.DateField(description="生成日期")
    target_date = fields.DateField(description="目标日期(生效日期)")
    pool_type = fields.CharField(
        max_length=20,
        default="today",
        description="股池类型: today-今日股池, tomorrow-明日股池"
    )

    # 异动信息
    anomaly_type = fields.CharField(
        max_length=50,
        description="异动类型: breakout-突破, signal_buy-买入信号, pattern-形态, volume-量异动"
    )
    anomaly_data = fields.JSONField(null=True, description="异动详情数据")

    # 时间信息
    duration_days = fields.IntField(description="持续时间(天)")
    effective_time = fields.DatetimeField(description="生效时间")
    expire_time = fields.DatetimeField(description="过期时间")

    # 置信度
    confidence = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        description="置信值(0-100)"
    )
    confidence_reason = fields.TextField(null=True, description="置信度原因")

    # 状态跟踪
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="状态: pending-待观察, verified-已验证, failed-已失效, expired-已过期"
    )

    # 验证结果
    entry_price = fields.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        description="入场价格"
    )
    exit_price = fields.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        description="出场价格"
    )
    max_return = fields.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        description="期间最大收益率(%)"
    )
    actual_return = fields.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        description="实际收益率(%)"
    )
    verified_at = fields.DatetimeField(null=True, description="验证时间")
    verify_note = fields.TextField(null=True, description="验证备注")

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "strategy_track_pool"
        indexes = [
            ("strategy_key",),
            ("stock_code",),
            ("generate_date",),
            ("target_date",),
            ("status",),
            ("pool_type",),
        ]

    def __str__(self):
        return f"{self.stock_code} - {self.strategy_key} - {self.target_date}"

    @property
    def status_display(self) -> str:
        """状态显示文本"""
        status_map = {
            "pending": "待观察",
            "verified": "已验证",
            "failed": "已失效",
            "expired": "已过期"
        }
        return status_map.get(self.status, self.status)

    @property
    def anomaly_type_display(self) -> str:
        """异动类型显示文本"""
        type_map = {
            "breakout": "突破",
            "signal_buy": "买入信号",
            "pattern": "形态识别",
            "volume": "量异动",
            "turnover": "换手异动",
            "custom": "自定义"
        }
        return type_map.get(self.anomaly_type, self.anomaly_type)

    @property
    def is_active(self) -> bool:
        """是否仍在有效期内"""
        now = datetime.now()
        return self.effective_time <= now <= self.expire_time

    @classmethod
    async def create_track_record(
        cls,
        strategy: StockPickStrategy,
        stock_code: str,
        stock_name: str,
        target_date,
        pool_type: str,
        anomaly_type: str,
        confidence: float,
        anomaly_data: dict = None,
        confidence_reason: str = None
    ):
        """
        创建追踪记录的便捷方法
        """
        from datetime import datetime, timedelta

        generate_date = datetime.now().date()
        effective_time = datetime.combine(target_date, datetime.min.time())
        expire_time = effective_time + timedelta(days=strategy.duration_days)

        return await cls.create(
            strategy=strategy,
            strategy_key=strategy.strategy_key,
            stock_code=stock_code,
            stock_name=stock_name,
            generate_date=generate_date,
            target_date=target_date,
            pool_type=pool_type,
            anomaly_type=anomaly_type,
            anomaly_data=anomaly_data,
            duration_days=strategy.duration_days,
            effective_time=effective_time,
            expire_time=expire_time,
            confidence=confidence,
            confidence_reason=confidence_reason
        )


class StrategyExecutionLog(Model):
    """
    策略执行日志

    记录策略每次执行的情况
    """
    id = fields.IntField(pk=True, description="主键ID")

    strategy = fields.ForeignKeyField(
        "models.StockPickStrategy",
        on_delete=fields.CASCADE,
        related_name="execution_logs",
        description="选股策略ID"
    )
    strategy_key = fields.CharField(max_length=50, description="策略KEY")

    execution_date = fields.DateField(description="执行日期")
    pool_type = fields.CharField(max_length=20, description="股池类型")

    # 执行结果
    status = fields.CharField(
        max_length=20,
        default="running",
        description="状态: running-执行中, success-成功, failed-失败"
    )
    stocks_found = fields.IntField(default=0, description="发现的股票数")
    stocks_saved = fields.IntField(default=0, description="保存的股票数")

    # 错误信息
    error_message = fields.TextField(null=True, description="错误信息")

    started_at = fields.DatetimeField(description="开始时间")
    finished_at = fields.DatetimeField(null=True, description="结束时间")

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "strategy_execution_logs"
        indexes = [
            ("strategy_key",),
            ("execution_date",),
            ("status",),
        ]

    def __str__(self):
        return f"{self.strategy_key} - {self.execution_date}"