"""
因子选股服务测试
"""
import pytest
import numpy as np
from app.services.factor_service import FactorService, factor_service
from app.models.factor_models import FactorCondition, ScoreWeight


class TestFactorService:
    """FactorService 测试类"""

    @pytest.mark.asyncio
    async def test_screen_stocks_basic(self, factor_service, sample_kline_data):
        """测试基本因子选股"""
        # 构造筛选条件
        conditions = [
            FactorCondition(factor_id="RSI14", operator="lt", value=70)
        ]

        # 构造股票池和数据
        stock_pool = ["000001", "000002", "000003"]
        stock_data_map = {
            "000001": sample_kline_data,
            "000002": sample_kline_data,
            "000003": sample_kline_data
        }

        result = await factor_service.screen_stocks(
            conditions=conditions,
            stock_pool=stock_pool,
            stock_data_map=stock_data_map,
            limit=10
        )

        assert result.date is not None
        assert result.count >= 0
        assert len(result.stocks) <= 10

    @pytest.mark.asyncio
    async def test_screen_stocks_multiple_conditions(self, factor_service, sample_kline_data):
        """测试多条件选股"""
        conditions = [
            FactorCondition(factor_id="RSI14", operator="lt", value=80),
            FactorCondition(factor_id="MA5", operator="gt", value=0)
        ]

        stock_pool = ["000001"]
        stock_data_map = {"000001": sample_kline_data}

        result = await factor_service.screen_stocks(
            conditions=conditions,
            stock_pool=stock_pool,
            stock_data_map=stock_data_map
        )

        assert result.date is not None

    @pytest.mark.asyncio
    async def test_screen_stocks_between_operator(self, factor_service, sample_kline_data):
        """测试 between 操作符"""
        conditions = [
            FactorCondition(factor_id="RSI14", operator="between", value=20, value2=80)
        ]

        stock_pool = ["000001"]
        stock_data_map = {"000001": sample_kline_data}

        result = await factor_service.screen_stocks(
            conditions=conditions,
            stock_pool=stock_pool,
            stock_data_map=stock_data_map
        )

        assert result.date is not None

    @pytest.mark.asyncio
    async def test_screen_stocks_empty_data(self, factor_service):
        """测试空数据处理"""
        conditions = [
            FactorCondition(factor_id="RSI14", operator="lt", value=70)
        ]

        result = await factor_service.screen_stocks(
            conditions=conditions,
            stock_pool=None,
            stock_data_map=None
        )

        assert result.count == 0
        assert len(result.stocks) == 0

    @pytest.mark.asyncio
    async def test_calculate_score_basic(self, factor_service, sample_kline_data):
        """测试基本评分计算"""
        weights = [
            ScoreWeight(factor_id="RSI14", weight=0.5, direction="high"),
            ScoreWeight(factor_id="MA5", weight=0.5, direction="high")
        ]

        stock_codes = ["000001", "000002"]
        stock_data_map = {
            "000001": sample_kline_data,
            "000002": sample_kline_data
        }

        result = await factor_service.calculate_score(
            stock_codes=stock_codes,
            weights=weights,
            stock_data_map=stock_data_map
        )

        assert result.date is not None
        assert len(result.stocks) > 0

        # 验证评分结果
        for stock in result.stocks:
            assert stock.score >= 0
            assert stock.rank >= 1

    @pytest.mark.asyncio
    async def test_calculate_score_direction_low(self, factor_service, sample_kline_data):
        """测试低值更好的评分方向"""
        weights = [
            ScoreWeight(factor_id="RSI14", weight=1.0, direction="low")
        ]

        stock_codes = ["000001"]
        stock_data_map = {"000001": sample_kline_data}

        result = await factor_service.calculate_score(
            stock_codes=stock_codes,
            weights=weights,
            stock_data_map=stock_data_map
        )

        assert len(result.stocks) > 0

    @pytest.mark.asyncio
    async def test_calculate_score_ranking(self, factor_service, sample_kline_data):
        """测试评分排名"""
        # 创建不同的K线数据（模拟不同表现）
        data1 = sample_kline_data.copy()
        data2 = []
        np.random.seed(123)
        base_price = 15.0  # 更高的基准价
        for i in range(30):
            change = np.random.uniform(-0.5, 0.5)
            close = base_price + change + i * 0.1  # 更强上升趋势
            data2.append({
                "date": f"202401{i+1:02d}",
                "open": close - 0.1,
                "high": close + 0.2,
                "low": close - 0.2,
                "close": close,
                "volume": 100000 + i * 1000
            })

        weights = [
            ScoreWeight(factor_id="MA5", weight=1.0, direction="high")
        ]

        stock_data_map = {
            "000001": data1,
            "000002": data2
        }

        result = await factor_service.calculate_score(
            stock_codes=["000001", "000002"],
            weights=weights,
            stock_data_map=stock_data_map
        )

        # 验证排名正确
        assert len(result.stocks) == 2
        assert result.stocks[0].rank == 1
        assert result.stocks[1].rank == 2
        assert result.stocks[0].score >= result.stocks[1].score

    @pytest.mark.asyncio
    async def test_get_factor_value(self, factor_service, sample_kline_data):
        """测试获取因子值"""
        result = await factor_service.get_factor_value(
            stock_code="000001",
            factor_id="RSI14",
            kline_data=sample_kline_data
        )

        assert result.stock_code == "000001"
        assert result.factor_id == "RSI14"
        assert 0 <= result.value <= 100

    @pytest.mark.asyncio
    async def test_get_factor_value_custom_factor(self, factor_service, sample_kline_data):
        """测试获取组合因子值"""
        result = await factor_service.get_factor_value(
            stock_code="000001",
            factor_id="MA5_MA10",
            kline_data=sample_kline_data
        )

        assert result.stock_code == "000001"
        assert result.factor_id == "MA5_MA10"

    @pytest.mark.asyncio
    async def test_get_available_factors(self, factor_service):
        """测试获取因子列表"""
        result = factor_service.get_available_factors()

        assert result.count > 0
        assert len(result.factors) > 0

        # 验证包含基本因子
        factor_ids = [f.factor_id for f in result.factors]
        assert "RSI14" in factor_ids
        assert "MA5" in factor_ids

    def test_check_condition_operators(self, factor_service):
        """测试条件检查操作符"""
        # gt
        assert factor_service._check_condition(15, FactorCondition(factor_id="test", operator="gt", value=10))
        assert not factor_service._check_condition(5, FactorCondition(factor_id="test", operator="gt", value=10))

        # lt
        assert factor_service._check_condition(5, FactorCondition(factor_id="test", operator="lt", value=10))
        assert not factor_service._check_condition(15, FactorCondition(factor_id="test", operator="lt", value=10))

        # ge
        assert factor_service._check_condition(10, FactorCondition(factor_id="test", operator="ge", value=10))
        assert factor_service._check_condition(15, FactorCondition(factor_id="test", operator="ge", value=10))

        # le
        assert factor_service._check_condition(10, FactorCondition(factor_id="test", operator="le", value=10))
        assert factor_service._check_condition(5, FactorCondition(factor_id="test", operator="le", value=10))

        # eq
        assert factor_service._check_condition(10, FactorCondition(factor_id="test", operator="eq", value=10))

        # between
        assert factor_service._check_condition(15, FactorCondition(factor_id="test", operator="between", value=10, value2=20))
        assert not factor_service._check_condition(25, FactorCondition(factor_id="test", operator="between", value=10, value2=20))