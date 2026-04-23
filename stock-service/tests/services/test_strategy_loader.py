#!/usr/bin/python
# -*- coding: utf-8 -*-
"""策略加载器单元测试"""

import pytest
from app.services.backtest.strategy_loader import (
    StrategyLoader,
    StrategySecurityError,
    StrategyLoadError
)


class TestStrategyLoader:
    """策略加载器测试类"""

    @pytest.fixture
    def loader(self):
        """创建策略加载器实例"""
        return StrategyLoader()

    # ========== 安全测试 ==========

    def test_forbidden_import_os(self, loader):
        """测试禁止导入 os 模块"""
        code = """
import os
class Strategy:
    pass
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "禁止导入模块" in str(exc_info.value)
        assert "os" in str(exc_info.value)

    def test_forbidden_import_subprocess(self, loader):
        """测试禁止导入 subprocess 模块"""
        code = """
import subprocess
class Strategy:
    pass
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "subprocess" in str(exc_info.value)

    def test_forbidden_import_from_requests(self, loader):
        """测试禁止从 requests 导入"""
        code = """
from requests import get
class Strategy:
    pass
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "requests" in str(exc_info.value)

    def test_forbidden_function_eval(self, loader):
        """测试禁止调用 eval 函数"""
        code = """
class Strategy:
    def run(self):
        eval("1+1")
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "eval" in str(exc_info.value)

    def test_forbidden_function_exec(self, loader):
        """测试禁止调用 exec 函数"""
        code = """
class Strategy:
    def run(self):
        exec("print(1)")
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "exec" in str(exc_info.value)

    def test_forbidden_function_open(self, loader):
        """测试禁止调用 open 函数"""
        code = """
class Strategy:
    def run(self):
        open("/etc/passwd")
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "open" in str(exc_info.value)

    def test_forbidden_function_getattr(self, loader):
        """测试禁止调用 getattr 函数"""
        code = """
class Strategy:
    def run(self):
        getattr(self, 'test')
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "getattr" in str(exc_info.value)

    def test_forbidden_function_globals(self, loader):
        """测试禁止调用 globals 函数"""
        code = """
class Strategy:
    def run(self):
        globals()
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "globals" in str(exc_info.value)

    def test_forbidden_attr_builtins(self, loader):
        """测试禁止访问 __builtins__ 属性"""
        code = """
class Strategy:
    def run(self):
        x = self.__builtins__
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "__builtins__" in str(exc_info.value)

    def test_forbidden_attr_class(self, loader):
        """测试禁止访问 __class__ 属性"""
        code = """
class Strategy:
    def run(self):
        x = self.__class__
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "__class__" in str(exc_info.value)

    def test_forbidden_attr_subclasses(self, loader):
        """测试禁止访问 __subclasses__ 属性"""
        code = """
class Strategy:
    def run(self):
        x = object.__subclasses__()
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "__subclasses__" in str(exc_info.value)

    # ========== 语法错误测试 ==========

    def test_syntax_error(self, loader):
        """测试语法错误"""
        code = """
class Strategy
    pass  # 缺少冒号
"""
        with pytest.raises(StrategyLoadError) as exc_info:
            loader.load_from_code(code)
        assert "语法错误" in str(exc_info.value)

    # ========== 策略验证测试 ==========

    def test_missing_strategy_class(self, loader):
        """测试缺少 Strategy 类"""
        code = """
class MyStrategy:
    pass
"""
        with pytest.raises(StrategyLoadError) as exc_info:
            loader.load_from_code(code)
        assert "必须定义名为 'Strategy' 的类" in str(exc_info.value)

    def test_invalid_strategy_not_bt_strategy(self, loader):
        """测试 Strategy 类不继承 bt.Strategy"""
        code = """
class Strategy:
    pass
"""
        with pytest.raises(StrategyLoadError) as exc_info:
            loader.load_from_code(code)
        assert "必须继承 bt.Strategy" in str(exc_info.value)

    def test_valid_strategy(self, loader):
        """测试有效的策略代码"""
        code = """
import backtrader as bt

class Strategy(bt.Strategy):
    params = (
        ('period', 20),
    )

    def __init__(self):
        self.ma = bt.indicators.SMA(period=self.params.period)

    def next(self):
        if self.data.close > self.ma:
            self.buy()
"""
        strategy_class = loader.load_from_code(code)
        assert strategy_class is not None
        assert strategy_class.__name__ == "Strategy"
        assert hasattr(strategy_class, 'params')

    # ========== 安全命名空间测试 ==========

    def test_safe_namespace_bt_available(self, loader):
        """测试 bt 在安全命名空间中可用"""
        code = """
class Strategy(bt.Strategy):
    pass
"""
        strategy_class = loader.load_from_code(code)
        assert strategy_class is not None

    def test_safe_namespace_numpy_available(self, loader):
        """测试 numpy 在安全命名空间中可用"""
        code = """
import backtrader as bt
import numpy as np

class Strategy(bt.Strategy):
    def __init__(self):
        self.values = np.array([1, 2, 3])
"""
        strategy_class = loader.load_from_code(code)
        assert strategy_class is not None

    def test_safe_namespace_pandas_available(self, loader):
        """测试 pandas 在安全命名空间中可用"""
        code = """
import backtrader as bt
import pandas as pd

class Strategy(bt.Strategy):
    def __init__(self):
        self.df = pd.DataFrame()
"""
        strategy_class = loader.load_from_code(code)
        assert strategy_class is not None

    # ========== 模板加载测试 ==========

    def test_load_from_template(self, loader):
        """测试从模板加载策略"""
        template_code = """
import backtrader as bt

class Strategy(bt.Strategy):
    params = (
        ('period', ${period}),
    )

    def __init__(self):
        self.ma = bt.indicators.SMA(period=self.params.period)
"""
        strategy_class = loader.load_from_template(template_code, {"period": 10})
        assert strategy_class is not None
        assert strategy_class.params.period == 10

    def test_load_from_template_multiple_params(self, loader):
        """测试从模板加载多个参数"""
        template_code = """
import backtrader as bt

class Strategy(bt.Strategy):
    params = (
        ('fast', ${fast}),
        ('slow', ${slow}),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(period=self.params.fast)
        self.slow_ma = bt.indicators.SMA(period=self.params.slow)
"""
        strategy_class = loader.load_from_template(template_code, {"fast": 5, "slow": 20})
        assert strategy_class is not None
        assert strategy_class.params.fast == 5
        assert strategy_class.params.slow == 20

    # ========== 复杂安全绕过测试 ==========

    def test_attribute_access_bypass(self, loader):
        """测试通过属性访问绕过安全检查"""
        code = """
class Strategy:
    def __init__(self):
        # 尝试通过属性链访问
        self.x = getattr
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "getattr" in str(exc_info.value)

    def test_importlib_bypass(self, loader):
        """测试使用 importlib 绕过"""
        code = """
import importlib
class Strategy:
    pass
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "importlib" in str(exc_info.value)

    def test_type_function_bypass(self, loader):
        """测试使用 type 函数绕过"""
        code = """
class Strategy:
    def run(self):
        t = type('x', (), {})
"""
        with pytest.raises(StrategySecurityError) as exc_info:
            loader.load_from_code(code)
        assert "type" in str(exc_info.value)