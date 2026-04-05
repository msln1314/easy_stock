"""
预警评估服务

根据预警条件规则，调用指标计算工具判断是否触发预警

使用方式：
    from utils.warning_evaluator import warning_evaluator

    # K线数据（标准格式）
    klines = [
        {'open': 10.0, 'close': 10.2, 'high': 10.5, 'low': 9.8, 'volume': 100000},
        ...
    ]

    # 评估预警
    triggered, values = warning_evaluator.evaluate(klines, condition)
"""
import json
from typing import Dict, List, Tuple
from utils.indicator_calculator import calculator


class WarningEvaluator:
    """预警条件评估服务"""

    def evaluate(self, klines: List[Dict], condition: Dict, quote: Dict = None) -> Tuple[bool, Dict]:
        """
        评估预警条件

        Args:
            klines: K线数据列表
            condition: 预警条件配置
            quote: 实时行情数据（阈值指标判断用）

        Returns:
            (是否触发, 触发时的指标值)
        """
        rule = json.loads(condition['condition_rule'])
        rule_type = rule.get('rule_type')

        # 技术指标类（需要K线计算）
        if rule_type == 'cross':
            return self._evaluate_cross(klines, condition, rule)
        elif rule_type == 'break':
            return self._evaluate_break(klines, condition, rule)
        elif rule_type == 'threshold':
            return self._evaluate_threshold(klines, condition, rule)
        # 行情/基本面阈值类
        elif rule_type == 'quote_threshold':
            return self._evaluate_quote_threshold(quote or {}, condition, rule)

        return False, {}

    def _evaluate_cross(self, klines: List[Dict], condition: Dict, rule: Dict) -> Tuple[bool, Dict]:
        """
        评估交叉类条件（死叉/金叉）

        适用于: MA死叉、MACD死叉、KDJ死叉等
        """
        # 计算主指标
        result1 = calculator.calculate(
            condition['indicator_key'],
            klines,
            rule.get('indicator_params', {})
        )

        # 计算副指标（如果需要两个指标比较）
        if condition.get('indicator_key2'):
            result2 = calculator.calculate(
                condition['indicator_key2'],
                klines,
                rule.get('indicator2_params', {})
            )
        else:
            # 同一指标的两个字段比较（如MACD的dif和dea）
            result2 = result1

        # 获取比较字段
        field1 = rule.get('field1', 'values')
        field2 = rule.get('field2', 'values')

        # 获取值列表
        values1 = result1.get(field1, [])
        values2 = result2.get(field2, [])

        # 如果字段不存在，尝试使用values
        if not values1 and field1 != 'values':
            values1 = result1.get('values', [])
        if not values2 and field2 != 'values':
            values2 = result2.get('values', [])

        # 确保是列表
        if not isinstance(values1, list):
            values1 = [values1] if values1 is not None else []
        if not isinstance(values2, list):
            values2 = [values2] if values2 is not None else []

        # 获取最新两个有效值
        valid_values1 = [v for v in values1 if v is not None]
        valid_values2 = [v for v in values2 if v is not None]

        if len(valid_values1) < 2 or len(valid_values2) < 2:
            return False, {}

        prev_val1, curr_val1 = valid_values1[-2], valid_values1[-1]
        prev_val2, curr_val2 = valid_values2[-2], valid_values2[-1]

        # 判断交叉
        triggered = False
        if rule['direction'] == 'down':  # 死叉：前一日val1>val2，当日val1<val2
            triggered = prev_val1 > prev_val2 and curr_val1 < curr_val2
        else:  # 金叉
            triggered = prev_val1 < prev_val2 and curr_val1 > curr_val2

        trigger_value = {
            'prev_val1': round(prev_val1, 4) if prev_val1 else None,
            'curr_val1': round(curr_val1, 4) if curr_val1 else None,
            'prev_val2': round(prev_val2, 4) if prev_val2 else None,
            'curr_val2': round(curr_val2, 4) if curr_val2 else None,
        }

        return triggered, trigger_value

    def _evaluate_break(self, klines: List[Dict], condition: Dict, rule: Dict) -> Tuple[bool, Dict]:
        """
        评估突破/跌破类条件

        适用于: EXPMA跌破、布林带下轨跌破等
        """
        # 计算指标
        result = calculator.calculate(
            condition['indicator_key'],
            klines,
            rule.get('indicator_params', {})
        )

        # 获取指标值
        field = rule.get('indicator_field', 'latest')

        if field == 'latest':
            indicator_value = result.get('latest')
            if isinstance(indicator_value, dict):
                indicator_value = indicator_value.get('value') or indicator_value.get('lower')
        else:
            values = result.get(field, [])
            indicator_value = values[-1] if values else None

        # 获取价格（从K线数组中获取最后一根K线的收盘价）
        close = klines[-1].get('close') if klines else None

        if indicator_value is None:
            return False, {}

        # 判断突破/跌破
        triggered = False
        if rule['direction'] == 'down':  # 跌破
            triggered = close < indicator_value
        else:  # 突破
            triggered = close > indicator_value

        trigger_value = {
            'close': round(close, 4),
            'indicator_value': round(indicator_value, 4)
        }

        return triggered, trigger_value

    def _evaluate_threshold(self, klines: List[Dict], condition: Dict, rule: Dict) -> Tuple[bool, Dict]:
        """
        评估阈值类条件

        适用于: RSI超买、KDJ超买等
        """
        # 计算指标
        result = calculator.calculate(
            condition['indicator_key'],
            klines,
            rule.get('indicator_params', {})
        )

        # 获取指标值
        field = rule.get('indicator_field', 'latest')

        if field == 'latest':
            value = result.get('latest')
            if isinstance(value, dict):
                value = value.get('value') or value.get('k') or value.get('values')
        else:
            values = result.get(field, [])
            value = values[-1] if values else None

        threshold = rule['threshold']

        if value is None:
            return False, {}

        # 比较操作
        ops = {
            'gt': lambda v, t: v > t,
            'lt': lambda v, t: v < t,
            'ge': lambda v, t: v >= t,
            'le': lambda v, t: v <= t,
            'eq': lambda v, t: v == t,
        }

        triggered = ops[rule['compare_op']](value, threshold)

        trigger_value = {
            'indicator_value': round(value, 4),
            'threshold': threshold
        }

        return triggered, trigger_value

    def _evaluate_quote_threshold(self, quote: Dict, condition: Dict, rule: Dict) -> Tuple[bool, Dict]:
        """评估行情/基本面阈值类条件"""
        indicator_key = rule.get('indicator_key')
        params = rule.get('params', {})

        if indicator_key == 'THRESHOLD_CHANGE':
            return self._eval_change_threshold(quote, params)
        elif indicator_key == 'THRESHOLD_TURNOVER':
            return self._eval_turnover_threshold(quote, params)
        elif indicator_key == 'THRESHOLD_VOLUME_RATIO':
            return self._eval_volume_ratio_threshold(quote, params)
        elif indicator_key == 'THRESHOLD_AMOUNT':
            return self._eval_amount_threshold(quote, params)
        elif indicator_key == 'THRESHOLD_MARKET_VALUE':
            return self._eval_market_value_threshold(quote, params)
        elif indicator_key == 'THRESHOLD_PE':
            return self._eval_pe_threshold(quote, params)
        elif indicator_key == 'THRESHOLD_PB':
            return self._eval_pb_threshold(quote, params)

        return False, {}

    def _eval_change_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估涨跌幅阈值"""
        start_date = params.get('start_date')
        threshold_percent = params.get('threshold_percent', 5)
        compare_op = params.get('compare_op', 'gt')

        start_price = quote.get('history_prices', {}).get(start_date)
        current_price = quote.get('price')

        if start_price is None or current_price is None or start_price == 0:
            return False, {}

        actual_change = (current_price - start_price) / start_price * 100

        ops = {
            'gt': lambda v, t: v > t,
            'lt': lambda v, t: v < t,
            'ge': lambda v, t: v >= t,
            'le': lambda v, t: v <= t,
        }

        triggered = ops.get(compare_op, ops['gt'])(actual_change, threshold_percent)

        return triggered, {
            'triggered': triggered,
            'actual_change_percent': round(actual_change, 4),
            'threshold_percent': threshold_percent,
            'start_price': round(start_price, 4),
            'current_price': round(current_price, 4),
            'start_date': start_date
        }

    def _eval_turnover_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估换手率阈值"""
        threshold = params.get('threshold', 10)
        compare_op = params.get('compare_op', 'gt')

        actual_turnover = quote.get('turnover_rate')
        if actual_turnover is None:
            return False, {}

        ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
               'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}

        triggered = ops.get(compare_op, ops['gt'])(actual_turnover, threshold)

        return triggered, {
            'triggered': triggered,
            'actual_turnover': round(actual_turnover, 4),
            'threshold': threshold
        }

    def _eval_volume_ratio_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估量比阈值"""
        threshold = params.get('threshold', 2)
        compare_op = params.get('compare_op', 'gt')

        actual_ratio = quote.get('volume_ratio')
        if actual_ratio is None:
            return False, {}

        ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
               'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}

        triggered = ops.get(compare_op, ops['gt'])(actual_ratio, threshold)

        return triggered, {
            'triggered': triggered,
            'actual_volume_ratio': round(actual_ratio, 4),
            'threshold': threshold
        }

    def _eval_amount_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估成交额阈值"""
        threshold = params.get('threshold', 1)
        unit = params.get('unit', '亿')
        compare_op = params.get('compare_op', 'gt')

        actual_amount = quote.get('amount', 0)
        # 转换单位
        if unit == '亿':
            actual_amount = actual_amount / 100000000
        elif unit == '万':
            actual_amount = actual_amount / 10000

        ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
               'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}

        triggered = ops.get(compare_op, ops['gt'])(actual_amount, threshold)

        return triggered, {
            'triggered': triggered,
            'actual_amount': round(actual_amount, 4),
            'threshold': threshold,
            'unit': unit
        }

    def _eval_market_value_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估市值阈值"""
        threshold = params.get('threshold', 50)
        unit = params.get('unit', '亿')
        compare_op = params.get('compare_op', 'lt')

        actual_value = quote.get('market_value', 0)
        if unit == '亿':
            actual_value = actual_value / 100000000
        elif unit == '万':
            actual_value = actual_value / 10000

        ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
               'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}

        triggered = ops.get(compare_op, ops['lt'])(actual_value, threshold)

        return triggered, {
            'triggered': triggered,
            'actual_value': round(actual_value, 4),
            'threshold': threshold,
            'unit': unit
        }

    def _eval_pe_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估市盈率阈值"""
        threshold = params.get('threshold', 30)
        compare_op = params.get('compare_op', 'lt')

        actual_pe = quote.get('pe')
        if actual_pe is None:
            return False, {}

        ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
               'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}

        triggered = ops.get(compare_op, ops['lt'])(actual_pe, threshold)

        return triggered, {
            'triggered': triggered,
            'actual_pe': round(actual_pe, 4),
            'threshold': threshold
        }

    def _eval_pb_threshold(self, quote: Dict, params: Dict) -> Tuple[bool, Dict]:
        """评估市净率阈值"""
        threshold = params.get('threshold', 3)
        compare_op = params.get('compare_op', 'lt')

        actual_pb = quote.get('pb')
        if actual_pb is None:
            return False, {}

        ops = {'gt': lambda v, t: v > t, 'lt': lambda v, t: v < t,
               'ge': lambda v, t: v >= t, 'le': lambda v, t: v <= t}

        triggered = ops.get(compare_op, ops['lt'])(actual_pb, threshold)

        return triggered, {
            'triggered': triggered,
            'actual_pb': round(actual_pb, 4),
            'threshold': threshold
        }

    def evaluate_group(self, klines: List[Dict], quote: Dict, group: Dict) -> Tuple[bool, Dict]:
        """
        评估组合条件组（支持嵌套）

        Args:
            klines: K线数据
            quote: 实时行情数据
            group: 组合条件组（包含 conditions 和 subgroups）

        Returns:
            (是否触发, 触发详情)
        """
        logic_type = group.get('logic_type', 'AND')

        # 评估当前组的所有条件项
        condition_results = []
        for item in group.get('conditions', []):
            condition = {
                'indicator_key': item.get('indicator_key'),
                'indicator_key2': item.get('indicator_key2'),
                'condition_rule': item.get('condition_rule'),
                'condition_key': item.get('condition_key'),
                'condition_name': item.get('condition_name'),
            }
            triggered, value = self.evaluate(klines, condition, quote)
            condition_results.append({
                'condition_key': item.get('condition_key'),
                'condition_name': item.get('condition_name'),
                'triggered': triggered,
                'trigger_value': value
            })

        # 递归评估子分组
        subgroup_results = []
        for subgroup in group.get('subgroups', []):
            triggered, sub_detail = self.evaluate_group(klines, quote, subgroup)
            subgroup_results.append({
                'group_key': subgroup.get('group_key'),
                'group_name': subgroup.get('group_name'),
                'triggered': triggered,
                'details': sub_detail
            })

        # 合并结果，按逻辑类型判断
        all_results = condition_results + subgroup_results
        triggered_flags = [r['triggered'] for r in all_results]

        if not triggered_flags:
            return False, {}

        if logic_type == 'AND':
            group_triggered = all(triggered_flags)
        else:
            group_triggered = any(triggered_flags)

        return group_triggered, {
            'group_name': group.get('group_name'),
            'logic_type': logic_type,
            'condition_results': condition_results,
            'subgroup_results': subgroup_results,
            'triggered_count': sum(triggered_flags),
            'total_count': len(all_results)
        }


# 预警条件预置数据
WARNING_CONDITIONS_PRESET = [
    {
        'condition_key': 'MA_DEAD_CROSS_30',
        'condition_name': '30分钟MA死叉',
        'indicator_key': 'MA',
        'indicator_key2': 'MA',
        'period': '30min',
        'condition_rule': json.dumps({
            'rule_type': 'cross',
            'direction': 'down',
            'indicator_params': {'period': 5},
            'indicator2_params': {'period': 10}
        }),
        'priority': 'critical',
        'description': '30分钟周期，5日均线下穿10日均线'
    },
    {
        'condition_key': 'MA_DEAD_CROSS_60',
        'condition_name': '60分钟MA死叉',
        'indicator_key': 'MA',
        'indicator_key2': 'MA',
        'period': '60min',
        'condition_rule': json.dumps({
            'rule_type': 'cross',
            'direction': 'down',
            'indicator_params': {'period': 5},
            'indicator2_params': {'period': 10}
        }),
        'priority': 'critical',
        'description': '60分钟周期，5日均线下穿10日均线'
    },
    {
        'condition_key': 'MA_DEAD_CROSS_DAILY',
        'condition_name': '日线MA死叉',
        'indicator_key': 'MA',
        'indicator_key2': 'MA',
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'cross',
            'direction': 'down',
            'indicator_params': {'period': 5},
            'indicator2_params': {'period': 10}
        }),
        'priority': 'critical',
        'description': '日线周期，5日均线下穿10日均线'
    },
    {
        'condition_key': 'EXPMA_BREAK_8',
        'condition_name': 'EXPMA8跌破',
        'indicator_key': 'EXPMA',
        'indicator_key2': None,
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'break',
            'direction': 'down',
            'indicator_params': {'period': 8}
        }),
        'priority': 'warning',
        'description': '股价跌破EXPMA8日线'
    },
    {
        'condition_key': 'EXPMA_BREAK_12',
        'condition_name': 'EXPMA12跌破',
        'indicator_key': 'EXPMA',
        'indicator_key2': None,
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'break',
            'direction': 'down',
            'indicator_params': {'period': 12}
        }),
        'priority': 'warning',
        'description': '股价跌破EXPMA12日线'
    },
    {
        'condition_key': 'MACD_DEAD_CROSS',
        'condition_name': 'MACD死叉',
        'indicator_key': 'MACD',
        'indicator_key2': None,
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'cross',
            'direction': 'down',
            'field1': 'dif',
            'field2': 'dea'
        }),
        'priority': 'critical',
        'description': 'MACD的DIF线下穿DEA线'
    },
    {
        'condition_key': 'KDJ_DEAD_CROSS',
        'condition_name': 'KDJ死叉',
        'indicator_key': 'KDJ',
        'indicator_key2': None,
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'cross',
            'direction': 'down',
            'field1': 'k',
            'field2': 'd'
        }),
        'priority': 'critical',
        'description': 'KDJ的K线下穿D线'
    },
    {
        'condition_key': 'RSI_OVERBOUGHT',
        'condition_name': 'RSI超买',
        'indicator_key': 'RSI',
        'indicator_key2': None,
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'threshold',
            'compare_op': 'gt',
            'threshold': 80
        }),
        'priority': 'warning',
        'description': 'RSI指标超过80进入超买区'
    },
    {
        'condition_key': 'RSI_OVERSOLD',
        'condition_name': 'RSI超卖',
        'indicator_key': 'RSI',
        'indicator_key2': None,
        'period': 'daily',
        'condition_rule': json.dumps({
            'rule_type': 'threshold',
            'compare_op': 'lt',
            'threshold': 20
        }),
        'priority': 'info',
        'description': 'RSI指标低于20进入超卖区'
    },
]


# 单例实例
warning_evaluator = WarningEvaluator()