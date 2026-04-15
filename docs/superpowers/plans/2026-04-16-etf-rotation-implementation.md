# 行业ETF轮动策略实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现基于斜率动量+RSRS择时+MA过滤的行业ETF轮动策略系统，支持模拟运行、信号提醒和回测功能。

**Architecture:** 混合架构，复用现有基础设施（Tortoise-ORM模型、FastAPI路由、统一响应格式），创建专用的指标计算引擎和轮动服务。

**Tech Stack:** 
- 后端: FastAPI + Tortoise-ORM + Python 3.11+ + scipy/numpy
- 前端: Vue3 + TypeScript + NaiveUI + ECharts
- 数据库: MySQL 8.0

---

## 文件结构

### 后端文件（创建）

| 文件 | 职责 |
|------|------|
| `backend/models/etf_pool.py` | ETF池配置模型 |
| `backend/models/rotation_strategy.py` | 轮动策略配置模型 |
| `backend/models/etf_score.py` | ETF评分记录模型 |
| `backend/models/rotation_signal.py` | 轮动信号记录模型 |
| `backend/models/rotation_position.py` | 模拟持仓记录模型 |
| `backend/models/rotation_backtest.py` | 回测记录模型 |
| `backend/utils/rotation_calculator/__init__.py` | 计算器模块入口 |
| `backend/utils/rotation_calculator/slope_momentum.py` | 斜率动量计算 |
| `backend/utils/rotation_calculator/rsrs.py` | RSRS择时指标 |
| `backend/utils/rotation_calculator/ma_filter.py` | MA均线过滤 |
| `backend/utils/backtest_engine.py` | 回测引擎 |
| `backend/schemas/etf_pool.py` | ETF池Schema |
| `backend/schemas/rotation_strategy.py` | 策略Schema |
| `backend/schemas/rotation_backtest.py` | 回测Schema |
| `backend/services/etf_rotation.py` | 轮动核心服务 |
| `backend/api/v1/etf_pool.py` | ETF池API |
| `backend/api/v1/etf_rotation.py` | 轮动策略API |
| `backend/scripts/init_etf_pool.py` | ETF池初始化 |
| `backend/tests/test_etf_rotation.py` | 单元测试 |

### 前端文件（创建）

| 文件 | 职责 |
|------|------|
| `frontend/src/types/etfRotation.ts` | TypeScript类型 |
| `frontend/src/api/etfPool.ts` | ETF池API封装 |
| `frontend/src/api/etfRotation.ts` | 轮动策略API封装 |
| `frontend/src/views/etf-rotation/index.vue` | 轮动监控主页面 |
| `frontend/src/views/etf-rotation/etf-pool.vue` | ETF池配置页面 |
| `frontend/src/views/etf-rotation/backtest.vue` | 回测页面 |

---

## Task 1: 数据库模型创建 (已完成)

**Files:**
- Create: `backend/models/etf_pool.py`
- Create: `backend/models/rotation_strategy.py`
- Create: `backend/models/etf_score.py`
- Create: `backend/models/rotation_signal.py`
- Create: `backend/models/rotation_position.py`
- Create: `backend/models/rotation_backtest.py`
- Modify: `backend/models/__init__.py`

- [x] **Step 1: 创建EtfPool模型**

```python
# backend/models/etf_pool.py
class EtfPool(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    code = fields.CharField(max_length=20)
    sector = fields.CharField(max_length=50)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "t_etf_pool"
```

- [x] **Step 2: 创建RotationStrategy模型**

```python
# backend/models/rotation_strategy.py
class RotationStrategy(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    slope_period = fields.IntField(default=20)
    rsrs_period = fields.IntField(default=18)
    rsrs_z_window = fields.IntField(default=100)
    rsrs_buy_threshold = fields.DecimalField(default=0.7)
    rsrs_sell_threshold = fields.DecimalField(default=-0.7)
    ma_period = fields.IntField(default=20)
    hold_count = fields.IntField(default=2)
    rebalance_freq = fields.CharField(default="weekly")
    execute_mode = fields.CharField(default="simulate")
    status = fields.CharField(default="paused")
    
    class Meta:
        table = "t_rotation_strategy"
```

- [x] **Step 3: 创建EtfScore模型**

```python
# backend/models/etf_score.py
class EtfScore(Model):
    strategy = fields.ForeignKeyField("models.RotationStrategy")
    etf_code = fields.CharField(max_length=20)
    trade_date = fields.DateField()
    slope_value = fields.DecimalField()
    r_squared = fields.DecimalField()
    momentum_score = fields.DecimalField()
    rsrs_beta = fields.DecimalField()
    rsrs_z_score = fields.DecimalField()
    ma_value = fields.DecimalField()
    close_price = fields.DecimalField()
    rank_position = fields.IntField()
    
    class Meta:
        table = "t_etf_score"
        unique_together = ("strategy", "trade_date", "etf_code")
```

- [x] **Step 4: 创建RotationSignal模型**

```python
# backend/models/rotation_signal.py
class RotationSignal(Model):
    strategy = fields.ForeignKeyField("models.RotationStrategy")
    signal_date = fields.DateField()
    signal_type = fields.CharField()  # buy/sell/rebalance
    etf_code = fields.CharField()
    etf_name = fields.CharField()
    action = fields.CharField()  # buy/sell/hold
    score = fields.DecimalField()
    rsrs_z = fields.DecimalField()
    price = fields.DecimalField()
    reason = fields.CharField()
    is_executed = fields.BooleanField(default=False)
    
    class Meta:
        table = "t_rotation_signal"
```

- [x] **Step 5: 创建RotationPosition模型**

```python
# backend/models/rotation_position.py
class RotationPosition(Model):
    strategy = fields.ForeignKeyField("models.RotationStrategy")
    etf_code = fields.CharField()
    etf_name = fields.CharField()
    buy_date = fields.DateField()
    buy_price = fields.DecimalField()
    buy_score = fields.DecimalField()
    quantity = fields.IntField()
    cost_amount = fields.DecimalField()
    current_price = fields.DecimalField()
    profit_pct = fields.DecimalField()
    hold_days = fields.IntField()
    status = fields.CharField(default="holding")  # holding/sold
    
    class Meta:
        table = "t_rotation_position"
```

- [x] **Step 6: 创建RotationBacktest模型**

```python
# backend/models/rotation_backtest.py
class RotationBacktest(Model):
    strategy = fields.ForeignKeyField("models.RotationStrategy")
    start_date = fields.DateField()
    end_date = fields.DateField()
    initial_capital = fields.DecimalField()
    final_capital = fields.DecimalField()
    total_return = fields.DecimalField()
    annual_return = fields.DecimalField()
    max_drawdown = fields.DecimalField()
    win_rate = fields.DecimalField()
    trade_count = fields.IntField()
    sharpe_ratio = fields.DecimalField()
    calmar_ratio = fields.DecimalField()
    benchmark_return = fields.DecimalField()
    excess_return = fields.DecimalField()
    backtest_details = fields.JSONField()
    
    class Meta:
        table = "t_rotation_backtest"
```

- [x] **Step 7: 更新models/__init__.py导入**

```python
# backend/models/__init__.py 添加
from .etf_pool import EtfPool
from .rotation_strategy import RotationStrategy
from .etf_score import EtfScore
from .rotation_signal import RotationSignal
from .rotation_position import RotationPosition
from .rotation_backtest import RotationBacktest
```

- [x] **Step 8: 验证语法**

Run: `python -m py_compile models/*.py`
Expected: "Syntax OK"

---

## Task 2: ETF池初始化脚本

**Files:**
- Create: `backend/scripts/init_etf_pool.py`

- [ ] **Step 1: 创建初始化脚本**

```python
# backend/scripts/init_etf_pool.py
"""
ETF池初始化脚本 - 预设9只行业ETF
"""
import asyncio
from tortoise import Tortoise
from config.database import DATABASE_CONFIG
from models.etf_pool import EtfPool

# 预设ETF数据
PRESET_ETFS = [
    {"name": "科技ETF", "code": "515000", "sector": "科技"},
    {"name": "消费ETF", "code": "159928", "sector": "消费"},
    {"name": "医药ETF", "code": "159929", "sector": "医药"},
    {"name": "金融ETF", "code": "159931", "sector": "金融"},
    {"name": "军工ETF", "code": "512660", "sector": "军工"},
    {"name": "新能源ETF", "code": "516160", "sector": "新能源"},
    {"name": "半导体ETF", "code": "512480", "sector": "半导体"},
    {"name": "有色ETF", "code": "512400", "sector": "有色金属"},
    {"name": "基建ETF", "code": "159766", "sector": "基建"},
]

async def init_etf_pool():
    await Tortoise.init(config=DATABASE_CONFIG)
    
    for etf_data in PRESET_ETFS:
        existing = await EtfPool.filter(code=etf_data["code"]).first()
        if not existing:
            await EtfPool.create(**etf_data)
            print(f"Created: {etf_data['name']} ({etf_data['code']})")
        else:
            print(f"Exists: {etf_data['name']} ({etf_data['code']})")
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(init_etf_pool())
```

- [ ] **Step 2: 验证语法**

Run: `python -m py_compile scripts/init_etf_pool.py`
Expected: "Syntax OK"

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/init_etf_pool.py
git commit -m "feat: 添加ETF池初始化脚本（预设9只行业ETF）"
```

---

## Task 3: 斜率动量计算器

**Files:**
- Create: `backend/utils/rotation_calculator/__init__.py`
- Create: `backend/utils/rotation_calculator/slope_momentum.py`
- Create: `backend/tests/test_slope_momentum.py`

- [ ] **Step 1: 创建模块入口**

```python
# backend/utils/rotation_calculator/__init__.py
from .slope_momentum import SlopeMomentumCalculator
from .rsrs import RSRSCalculator
from .ma_filter import MAFilter
```

- [ ] **Step 2: 写测试用例**

```python
# backend/tests/test_slope_momentum.py
import pytest
from utils.rotation_calculator.slope_momentum import SlopeMomentumCalculator

def test_slope_momentum_basic():
    """测试基本斜率计算"""
    calc = SlopeMomentumCalculator(period=5)
    # 稳定上涨序列: 10, 11, 12, 13, 14
    closes = [10.0, 11.0, 12.0, 13.0, 14.0]
    result = calc.calculate(closes)
    
    assert result['slope'] is not None
    assert result['slope'] > 0  # 上涨趋势，斜率正
    assert result['r_squared'] > 0.9  # 稳定趋势，R²接近1
    assert result['score'] > 0  # 正评分

def test_slope_momentum_insufficient_data():
    """测试数据不足时返回None"""
    calc = SlopeMomentumCalculator(period=20)
    closes = [10.0, 11.0, 12.0]  # 只有3个数据点
    result = calc.calculate(closes)
    
    assert result['slope'] is None
    assert result['r_squared'] is None
    assert result['score'] is None

def test_slope_momentum_declining():
    """测试下跌趋势"""
    calc = SlopeMomentumCalculator(period=5)
    closes = [14.0, 13.0, 12.0, 11.0, 10.0]  # 稳定下跌
    result = calc.calculate(closes)
    
    assert result['slope'] < 0  # 下跌趋势，斜率负
    assert result['r_squared'] > 0.9
    assert result['score'] < 0  # 负评分
```

- [ ] **Step 3: 运行测试验证失败**

Run: `pytest tests/test_slope_momentum.py -v`
Expected: FAIL - module not found

- [ ] **Step 4: 实现斜率动量计算器**

```python
# backend/utils/rotation_calculator/slope_momentum.py
"""
斜率动量评分计算

动量评分 = slope × R² × 10000
"""
import numpy as np
from typing import List, Dict
from scipy import stats


class SlopeMomentumCalculator:
    """斜率动量评分计算器"""

    def __init__(self, period: int = 20):
        self.period = period

    def calculate(self, closes: List[float]) -> Dict:
        """
        计算斜率动量评分

        Args:
            closes: 收盘价序列

        Returns:
            {'slope': 斜率值, 'r_squared': R²拟合优度, 'score': 动量评分}
        """
        if len(closes) < self.period:
            return {'slope': None, 'r_squared': None, 'score': None}

        # 取最近N日收盘价
        y = np.array(closes[-self.period:])
        x = np.arange(self.period)

        # 线性回归: y = slope * x + intercept
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared = r_value ** 2

        # 动量评分
        score = slope * r_squared * 10000

        return {
            'slope': round(slope, 6),
            'r_squared': round(r_squared, 6),
            'score': round(score, 4)
        }
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest tests/test_slope_momentum.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/utils/rotation_calculator/
git commit -m "feat: 实现斜率动量评分计算器"
```

---

## Task 4: RSRS择时指标计算器

**Files:**
- Create: `backend/utils/rotation_calculator/rsrs.py`
- Create: `backend/tests/test_rsrs.py`

- [ ] **Step 1: 写测试用例**

```python
# backend/tests/test_rsrs.py
import pytest
from utils.rotation_calculator.rsrs import RSRSCalculator

def test_rsrs_buy_signal():
    """测试买入信号 - Z > 0.7"""
    calc = RSRSCalculator(period=5, z_window=10)
    highs = [11.0, 12.0, 13.0, 14.0, 15.0]
    lows = [10.0, 11.0, 12.0, 13.0, 14.0]
    beta_history = [0.8] * 10  # 历史beta序列
    
    result = calc.calculate(highs, lows, beta_history)
    
    assert result['beta'] is not None
    assert result['signal'] in ['buy', 'sell', 'neutral']

def test_rsrs_insufficient_data():
    """测试数据不足"""
    calc = RSRSCalculator(period=18, z_window=100)
    highs = [10.0, 11.0]
    lows = [9.0, 10.0]
    
    result = calc.calculate(highs, lows)
    
    assert result['beta'] is None
    assert result['signal'] == 'neutral'

def test_rsrs_signal_threshold():
    """测试信号阈值判断"""
    calc = RSRSCalculator(period=5, z_window=5)
    
    # 构造Z > 0.7的场景
    result_high_z = calc.calculate(
        highs=[15.0, 16.0, 17.0, 18.0, 19.0],
        lows=[14.0, 15.0, 16.0, 17.0, 18.0],
        beta_history=[0.5, 0.6, 0.7, 0.8, 0.9]
    )
    
    # 构造Z < -0.7的场景
    result_low_z = calc.calculate(
        highs=[10.0, 9.0, 8.0, 7.0, 6.0],
        lows=[9.0, 8.0, 7.0, 6.0, 5.0],
        beta_history=[1.5, 1.4, 1.3, 1.2, 1.1]
    )
    
    # 验证信号类型正确
    assert result_high_z['signal'] in ['buy', 'sell', 'neutral']
    assert result_low_z['signal'] in ['buy', 'sell', 'neutral']
```

- [ ] **Step 2: 实现RSRS计算器**

```python
# backend/utils/rotation_calculator/rsrs.py
"""
RSRS择时指标计算

阻力支撑相对强度:
1. 对 (low, high) 做线性回归: high = β × low + α
2. 对 β 做Z-score标准化
3. Z > 0.7 买入信号, Z < -0.7 卖出信号
"""
import numpy as np
from typing import List, Dict, Optional
from scipy import stats


class RSRSCalculator:
    """RSRS择时指标计算器"""

    def __init__(self, period: int = 18, z_window: int = 100):
        self.period = period      # 回归窗口
        self.z_window = z_window  # Z-score标准化窗口

    def calculate(
        self,
        highs: List[float],
        lows: List[float],
        beta_history: Optional[List[float]] = None
    ) -> Dict:
        """
        计算RSRS指标

        Args:
            highs: 最高价序列
            lows: 最低价序列
            beta_history: 历史beta序列（用于Z-score计算）

        Returns:
            {'beta': 当期斜率β, 'z_score': Z-score值, 'signal': buy/sell/neutral}
        """
        if len(highs) < self.period or len(lows) < self.period:
            return {'beta': None, 'z_score': None, 'signal': 'neutral'}

        # 取最近N日数据
        h = np.array(highs[-self.period:])
        l = np.array(lows[-self.period:])

        # 线性回归: high = beta * low + alpha
        beta, alpha, r_value, p_value, std_err = stats.linregress(l, h)

        # Z-score标准化
        if beta_history and len(beta_history) >= self.z_window:
            recent_betas = np.array(beta_history[-self.z_window:])
            mean_beta = np.mean(recent_betas)
            std_beta = np.std(recent_betas)
            z_score = (beta - mean_beta) / std_beta if std_beta > 0 else 0
        else:
            z_score = 0  # 数据不足时为中性

        # 信号判断
        if z_score > 0.7:
            signal = 'buy'
        elif z_score < -0.7:
            signal = 'sell'
        else:
            signal = 'neutral'

        return {
            'beta': round(beta, 6),
            'z_score': round(z_score, 6),
            'signal': signal
        }
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/test_rsrs.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add backend/utils/rotation_calculator/rsrs.py backend/tests/test_rsrs.py
git commit -m "feat: 实现RSRS择时指标计算器"
```

---

## Task 5: MA过滤计算器

**Files:**
- Create: `backend/utils/rotation_calculator/ma_filter.py`
- Create: `backend/tests/test_ma_filter.py`

- [ ] **Step 1: 写测试用例**

```python
# backend/tests/test_ma_filter.py
import pytest
from utils.rotation_calculator.ma_filter import MAFilter

def test_ma_filter_basic():
    """测试MA计算"""
    calc = MAFilter(period=5)
    closes = [10.0, 11.0, 12.0, 13.0, 14.0]
    result = calc.calculate(closes)
    
    # 5日均线 = (10+11+12+13+14)/5 = 12
    assert result == 12.0

def test_ma_filter_insufficient_data():
    """测试数据不足"""
    calc = MAFilter(period=20)
    closes = [10.0, 11.0, 12.0]
    result = calc.calculate(closes)
    
    # 数据不足，返回当前数据平均值
    assert result is not None
```

- [ ] **Step 2: 实现MA过滤**

```python
# backend/utils/rotation_calculator/ma_filter.py
"""
MA均线过滤计算

用于二次确认买卖信号：
- 买入确认: 收盘价 > MA
- 卖出确认: 收盘价 < MA
"""
from typing import List


class MAFilter:
    """MA均线计算器"""

    def __init__(self, period: int = 20):
        self.period = period

    def calculate(self, closes: List[float]) -> float:
        """
        计算MA均线值

        Args:
            closes: 收盘价序列

        Returns:
            MA均线值（最近period日的平均值）
        """
        if len(closes) < self.period:
            # 数据不足时返回全部数据的平均值
            return sum(closes) / len(closes) if closes else 0

        # 取最近N日收盘价计算平均值
        recent_closes = closes[-self.period:]
        return sum(recent_closes) / self.period
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/test_ma_filter.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add backend/utils/rotation_calculator/ma_filter.py backend/tests/test_ma_filter.py
git commit -m "feat: 实现MA均线过滤计算器"
```

---

## Task 6: ETF轮动核心服务

**Files:**
- Create: `backend/services/etf_rotation.py`

- [ ] **Step 1: 实现轮动服务**

```python
# backend/services/etf_rotation.py
"""
ETF轮动策略核心服务
"""
from typing import List, Dict, Optional
from datetime import date
from loguru import logger

from services.kline_service import kline_service
from utils.rotation_calculator.slope_momentum import SlopeMomentumCalculator
from utils.rotation_calculator.rsrs import RSRSCalculator
from utils.rotation_calculator.ma_filter import MAFilter
from models.rotation_strategy import RotationStrategy
from models.etf_pool import EtfPool
from models.etf_score import EtfScore
from models.rotation_signal import RotationSignal
from models.rotation_position import RotationPosition


class EtfRotationService:
    """ETF轮动策略服务"""

    async def calculate_scores(
        self,
        strategy: RotationStrategy,
        trade_date: date
    ) -> List[EtfScore]:
        """计算ETF池所有ETF的评分并排序"""
        etf_pool = await EtfPool.filter(is_active=True).all()
        
        scores = []
        slope_calc = SlopeMomentumCalculator(strategy.slope_period)
        rsrs_calc = RSRSCalculator(strategy.rsrs_period, strategy.rsrs_z_window)
        ma_filter = MAFilter(strategy.ma_period)

        for etf in etf_pool:
            klines = await kline_service.get_klines(
                etf.code,
                limit=max(strategy.slope_period, strategy.rsrs_period, strategy.rsrs_z_window) + 10
            )

            closes = klines['close']
            highs = klines['high']
            lows = klines['low']

            momentum = slope_calc.calculate(closes)
            rsrs = rsrs_calc.calculate(highs, lows)
            ma_val = ma_filter.calculate(closes)

            score = EtfScore(
                strategy_id=strategy.id,
                etf_code=etf.code,
                trade_date=trade_date,
                slope_value=momentum['slope'],
                r_squared=momentum['r_squared'],
                momentum_score=momentum['score'],
                rsrs_beta=rsrs['beta'],
                rsrs_z_score=rsrs['z_score'],
                ma_value=ma_val,
                close_price=closes[-1]
            )
            scores.append(score)

        # 按评分降序排序
        scores.sort(key=lambda x: x.momentum_score or 0, reverse=True)
        
        for i, score in enumerate(scores):
            score.rank_position = i + 1

        return scores

    async def generate_signals(
        self,
        strategy: RotationStrategy,
        scores: List[EtfScore]
    ) -> List[RotationSignal]:
        """根据评分和RSRS信号生成调仓建议"""
        signals = []
        trade_date = scores[0].trade_date if scores else date.today()

        holdings = await RotationPosition.filter(
            strategy_id=strategy.id,
            status='holding'
        ).all()

        # 检查卖出信号
        for holding in holdings:
            score = next((s for s in scores if s.etf_code == holding.etf_code), None)
            if score and score.rsrs_z_score < strategy.rsrs_sell_threshold:
                if score.close_price < score.ma_value:
                    signals.append(RotationSignal(
                        strategy_id=strategy.id,
                        signal_date=trade_date,
                        signal_type='sell',
                        etf_code=holding.etf_code,
                        etf_name=holding.etf_name,
                        action='sell',
                        score=score.momentum_score,
                        rsrs_z=score.rsrs_z_score,
                        price=score.close_price,
                        reason=f"RSRS跌破阈值,MA确认"
                    ))

        # 检查买入信号
        for score in scores[:strategy.hold_count + 2]:
            if score.rsrs_z_score > strategy.rsrs_buy_threshold:
                if score.close_price > score.ma_value:
                    if not any(h.etf_code == score.etf_code for h in holdings):
                        etf = await EtfPool.filter(code=score.etf_code).first()
                        signals.append(RotationSignal(
                            strategy_id=strategy.id,
                            signal_date=trade_date,
                            signal_type='buy',
                            etf_code=score.etf_code,
                            etf_name=etf.name if etf else '',
                            action='buy',
                            score=score.momentum_score,
                            rsrs_z=score.rsrs_z_score,
                            price=score.close_price,
                            reason=f"评分#{score.rank_position},RSRS突破"
                        ))

        return signals
```

- [ ] **Step 2: 验证语法**

Run: `python -m py_compile services/etf_rotation.py`
Expected: "Syntax OK"

- [ ] **Step 3: Commit**

```bash
git add backend/services/etf_rotation.py
git commit -m "feat: 实现ETF轮动核心服务"
```

---

## Task 7: Schema定义

**Files:**
- Create: `backend/schemas/etf_pool.py`
- Create: `backend/schemas/rotation_strategy.py`
- Create: `backend/schemas/rotation_backtest.py`

- [ ] **Step 1: 创建ETF池Schema**

```python
# backend/schemas/etf_pool.py
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EtfPoolCreate(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    sector: str = Field(..., max_length=50)
    is_active: bool = Field(default=True)

class EtfPoolUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    is_active: Optional[bool] = None

class EtfPoolResponse(BaseModel):
    id: int
    name: str
    code: str
    sector: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 创建策略Schema**

```python
# backend/schemas/rotation_strategy.py
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, date

class RotationStrategyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    slope_period: int = Field(default=20)
    rsrs_period: int = Field(default=18)
    rsrs_z_window: int = Field(default=100)
    rsrs_buy_threshold: float = Field(default=0.7)
    rsrs_sell_threshold: float = Field(default=-0.7)
    ma_period: int = Field(default=20)
    hold_count: int = Field(default=2)
    rebalance_freq: str = Field(default="weekly")
    execute_mode: str = Field(default="simulate")

class RotationStrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    slope_period: Optional[int] = None
    rsrs_period: Optional[int] = None
    status: Optional[str] = None

class RotationStrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    slope_period: int
    rsrs_period: int
    hold_count: int
    rebalance_freq: str
    execute_mode: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EtfScoreResponse(BaseModel):
    etf_code: str
    etf_name: Optional[str]
    momentum_score: Optional[float]
    rsrs_z_score: Optional[float]
    close_price: Optional[float]
    ma_value: Optional[float]
    rank_position: Optional[int]

class SignalResponse(BaseModel):
    id: int
    signal_date: date
    signal_type: str
    etf_code: str
    etf_name: Optional[str]
    action: str
    score: Optional[float]
    rsrs_z: Optional[float]
    price: Optional[float]
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 3: 创建回测Schema**

```python
# backend/schemas/rotation_backtest.py
from pydantic import BaseModel, Field
from datetime import date

class BacktestRequest(BaseModel):
    start_date: date
    end_date: date
    initial_capital: float = Field(default=100000)

class BacktestResponse(BaseModel):
    id: int
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    sharpe_ratio: float

    class Config:
        from_attributes = True
```

- [ ] **Step 4: 验证语法并Commit**

Run: `python -m py_compile schemas/*.py`

```bash
git add backend/schemas/etf_pool.py backend/schemas/rotation_strategy.py backend/schemas/rotation_backtest.py
git commit -m "feat: 添加ETF轮动Schema定义"
```

---

## Task 8: ETF池管理API

**Files:**
- Create: `backend/api/v1/etf_pool.py`
- Modify: `backend/main.py`

- [ ] **Step 1: 实现ETF池API**

```python
# backend/api/v1/etf_pool.py
from fastapi import APIRouter, Query
from core.response import success_response, error_response
from schemas.etf_pool import EtfPoolCreate, EtfPoolUpdate, EtfPoolResponse
from models.etf_pool import EtfPool

router = APIRouter(prefix="/api/v1/etf-pool", tags=["ETF池管理"])

@router.get("")
async def get_etf_pool_list():
    etfs = await EtfPool.all()
    return success_response([EtfPoolResponse.model_validate(e) for e in etfs])

@router.post("")
async def add_etf(data: EtfPoolCreate):
    existing = await EtfPool.filter(code=data.code).first()
    if existing:
        return error_response("ETF代码已存在")
    etf = await EtfPool.create(**data.model_dump())
    return success_response(EtfPoolResponse.model_validate(etf))

@router.put("/{id}")
async def update_etf(id: int, data: EtfPoolUpdate):
    etf = await EtfPool.filter(id=id).first()
    if not etf:
        return error_response("ETF不存在", 404)
    await etf.update(**data.model_dump(exclude_unset=True))
    return success_response(EtfPoolResponse.model_validate(etf))

@router.delete("/{id}")
async def delete_etf(id: int):
    etf = await EtfPool.filter(id=id).first()
    if not etf:
        return error_response("ETF不存在", 404)
    await etf.delete()
    return success_response(message="删除成功")
```

- [ ] **Step 2: 注册路由到main.py**

```python
# backend/main.py 添加导入和注册
from api.v1.etf_pool import router as etf_pool_router
# ...
app.include_router(etf_pool_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/api/v1/etf_pool.py backend/main.py
git commit -m "feat: 实现ETF池管理API"
```

---

## Task 9: 轮动策略API

**Files:**
- Create: `backend/api/v1/etf_rotation.py`
- Modify: `backend/main.py`

- [ ] **Step 1: 实现轮动策略API**

```python
# backend/api/v1/etf_rotation.py
from fastapi import APIRouter, Query
from datetime import date
from core.response import success_response, error_response
from schemas.rotation_strategy import (
    RotationStrategyCreate, RotationStrategyResponse,
    EtfScoreResponse, SignalResponse
)
from models.rotation_strategy import RotationStrategy
from models.etf_pool import EtfPool
from services.etf_rotation import EtfRotationService

router = APIRouter(prefix="/api/v1/rotation-strategies", tags=["轮动策略"])
service = EtfRotationService()

@router.get("")
async def get_strategies():
    strategies = await RotationStrategy.all()
    return success_response([RotationStrategyResponse.model_validate(s) for s in strategies])

@router.post("")
async def create_strategy(data: RotationStrategyCreate):
    strategy = await RotationStrategy.create(**data.model_dump())
    return success_response({"id": strategy.id, "name": strategy.name})

@router.get("/{id}")
async def get_strategy(id: int):
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)
    return success_response(RotationStrategyResponse.model_validate(strategy))

@router.put("/{id}/status")
async def update_status(id: int, status: str):
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)
    strategy.status = status
    await strategy.save()
    return success_response({"id": strategy.id, "status": strategy.status})

@router.get("/{id}/scores/latest")
async def get_latest_scores(id: int):
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)
    
    scores = await service.calculate_scores(strategy, date.today())
    
    # 获取ETF名称
    result = []
    for score in scores:
        etf = await EtfPool.filter(code=score.etf_code).first()
        result.append({
            "etf_code": score.etf_code,
            "etf_name": etf.name if etf else "",
            "momentum_score": float(score.momentum_score) if score.momentum_score else None,
            "rsrs_z_score": float(score.rsrs_z_score) if score.rsrs_z_score else None,
            "close_price": float(score.close_price) if score.close_price else None,
            "ma_value": float(score.ma_value) if score.ma_value else None,
            "rank": score.rank_position
        })
    
    return success_response({"trade_date": date.today().isoformat(), "scores": result})

@router.post("/{id}/signals/generate")
async def generate_signals(id: int):
    strategy = await RotationStrategy.filter(id=id).first()
    if not strategy:
        return error_response("策略不存在", 404)
    
    scores = await service.calculate_scores(strategy, date.today())
    signals = await service.generate_signals(strategy, scores)
    
    return success_response([{
        "signal_date": s.signal_date.isoformat(),
        "signal_type": s.signal_type,
        "etf_code": s.etf_code,
        "etf_name": s.etf_name,
        "action": s.action,
        "score": float(s.score) if s.score else None,
        "rsrs_z": float(s.rsrs_z) if s.rsrs_z else None,
        "price": float(s.price) if s.price else None,
        "reason": s.reason
    } for s in signals])
```

- [ ] **Step 2: 注册路由**

```python
# backend/main.py 添加
from api.v1.etf_rotation import router as etf_rotation_router
app.include_router(etf_rotation_router)
```

- [ ] **Step 3: Commit**

```bash
git add backend/api/v1/etf_rotation.py backend/main.py
git commit -m "feat: 实现轮动策略API"
```

---

## Task 10: 回测引擎

**Files:**
- Create: `backend/utils/backtest_engine.py`

- [ ] **Step 1: 实现回测引擎**

```python
# backend/utils/backtest_engine.py
"""
ETF轮动回测引擎
"""
import numpy as np
from typing import List, Dict
from datetime import date
from dataclasses import dataclass

@dataclass
class BacktestResult:
    total_return: float
    annual_return: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    sharpe_ratio: float

class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []

    def run(
        self,
        signals: List[Dict],
        prices: Dict[str, List[float]]
    ) -> BacktestResult:
        """
        运行回测
        
        Args:
            signals: 信号列表 [{date, action, etf_code, price}]
            prices: ETF价格历史 {etf_code: [prices]}
        """
        for signal in signals:
            self._execute_signal(signal)

        # 计算指标
        equity_values = [e['equity'] for e in self.equity_curve]
        
        total_return = (self.capital - self.initial_capital) / self.initial_capital * 100
        
        # 最大回撤
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak
        max_drawdown = np.max(drawdown) * 100
        
        # 胜率
        wins = [t for t in self.trades if t['profit'] > 0]
        win_rate = len(wins) / len(self.trades) * 100 if self.trades else 0
        
        # 夏普比率 (简化计算)
        returns = np.diff(equity_values) / equity_values[:-1]
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        
        # 年化收益
        days = len(equity_curve)
        annual_return = total_return * 252 / days if days > 0 else 0

        return BacktestResult(
            total_return=round(total_return, 2),
            annual_return=round(annual_return, 2),
            max_drawdown=round(max_drawdown, 2),
            win_rate=round(win_rate, 2),
            trade_count=len(self.trades),
            sharpe_ratio=round(sharpe_ratio, 2)
        )

    def _execute_signal(self, signal: Dict):
        """执行信号"""
        action = signal['action']
        etf_code = signal['etf_code']
        price = signal['price']
        
        if action == 'buy':
            # 模拟买入
            shares = int(self.capital * 0.5 / price)  # 50%仓位
            cost = shares * price
            self.capital -= cost
            self.positions[etf_code] = {'shares': shares, 'cost': cost, 'buy_price': price}
            
        elif action == 'sell':
            if etf_code in self.positions:
                pos = self.positions[etf_code]
                revenue = pos['shares'] * price
                profit = revenue - pos['cost']
                self.capital += revenue
                self.trades.append({
                    'etf_code': etf_code,
                    'buy_price': pos['buy_price'],
                    'sell_price': price,
                    'profit': profit
                })
                del self.positions[etf_code]

        # 记录权益
        equity = self.capital + sum(
            pos['shares'] * price for pos in self.positions.values()
        )
        self.equity_curve.append({
            'date': signal['date'],
            'equity': equity
        })
```

- [ ] **Step 2: 验证语法并Commit**

```bash
git add backend/utils/backtest_engine.py
git commit -m "feat: 实现回测引擎"
```

---

## Task 11-15: 前端开发

前端开发任务与后端类似，包含：
- TypeScript类型定义
- API封装
- Vue页面组件

具体代码在执行时生成。

---

## Task 16: 后端测试验证

- [ ] **创建集成测试文件**

```python
# backend/tests/test_etf_rotation.py
import pytest
from utils.rotation_calculator.slope_momentum import SlopeMomentumCalculator
from utils.rotation_calculator.rsrs import RSRSCalculator
from utils.rotation_calculator.ma_filter import MAFilter

def test_slope_momentum():
    calc = SlopeMomentumCalculator(5)
    result = calc.calculate([10, 11, 12, 13, 14])
    assert result['slope'] > 0
    assert result['score'] > 0

def test_rsrs():
    calc = RSRSCalculator(5, 5)
    result = calc.calculate([15, 16, 17, 18, 19], [14, 15, 16, 17, 18], [0.5]*5)
    assert result['signal'] in ['buy', 'sell', 'neutral']

def test_ma_filter():
    calc = MAFilter(5)
    result = calc.calculate([10, 11, 12, 13, 14])
    assert result == 12.0
```

---

## Task 17: 前后端联调

- [ ] 启动后端验证API
- [ ] 启动前端验证页面
- [ ] 功能测试

---

## 验收标准

| 功能 | 验收标准 |
|------|----------|
| 数据模型 | 6张表创建成功，语法正确 |
| 指标计算 | 斜率、RSRS、MA计算正确 |
| API接口 | 所有接口响应正确 |
| 前端页面 | 页面可正常访问和操作 |
| 测试 | pytest测试通过 |

---

**文档结束**