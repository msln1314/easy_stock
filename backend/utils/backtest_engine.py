"""
ETF轮动回测引擎

支持:
- 基于历史K线数据的策略回测
- 计算总收益、年化收益、最大回撤、胜率、夏普比率等指标
- 生成收益曲线数据
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class TradeRecord:
    """交易记录"""
    etf_code: str
    etf_name: str
    action: str  # buy/sell
    trade_date: date
    price: float
    shares: int
    amount: float
    profit: float = 0.0  # 卖出时的盈亏


@dataclass
class EquityPoint:
    """权益曲线点"""
    date: date
    equity: float
    cash: float
    position_value: float


@dataclass
class BacktestResult:
    """回测结果"""
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    win_rate: float
    trade_count: int
    win_count: int
    loss_count: int
    sharpe_ratio: float
    calmar_ratio: float
    benchmark_return: float = 0.0
    excess_return: float = 0.0
    trades: List[TradeRecord] = field(default_factory=list)
    equity_curve: List[EquityPoint] = field(default_factory=list)


class BacktestEngine:
    """ETF轮动回测引擎"""

    def __init__(self, initial_capital: float = 100000):
        """
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: Dict[str, Dict] = {}  # {etf_code: {shares, buy_price, buy_date}}
        self.trades: List[TradeRecord] = []
        self.equity_curve: List[EquityPoint] = []

    def run(
        self,
        klines: Dict[str, Dict],  # {etf_code: {dates, closes, highs, lows}}
        signals: List[Dict],  # [{date, action, etf_code, price}]
        benchmark_returns: Optional[List[float]] = None
    ) -> BacktestResult:
        """
        运行回测

        Args:
            klines: ETF历史K线数据
            signals: 策略信号序列
            benchmark_returns: 基准收益序列（如沪深300）

        Returns:
            BacktestResult
        """
        if not signals:
            logger.warning("无信号数据，回测终止")
            return self._create_empty_result()

        # 重置状态
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []

        # 按日期排序信号
        sorted_signals = sorted(signals, key=lambda x: x['date'])

        start_date = sorted_signals[0]['date']
        end_date = sorted_signals[-1]['date']

        # 执行每个信号
        for signal in sorted_signals:
            self._execute_signal(signal)
            self._record_equity(signal['date'], klines)

        # 计算指标
        result = self._calculate_metrics(start_date, end_date, benchmark_returns)

        logger.info(f"回测完成: 总收益 {result.total_return:.2f}%, 夏普 {result.sharpe_ratio:.2f}")

        return result

    def _execute_signal(self, signal: Dict):
        """执行交易信号"""
        action = signal['action']
        etf_code = signal['etf_code']
        price = signal.get('price', 0)
        trade_date = signal['date']
        etf_name = signal.get('etf_name', etf_code)

        if action == 'buy':
            self._buy(etf_code, etf_name, price, trade_date)
        elif action == 'sell':
            self._sell(etf_code, etf_name, price, trade_date)

    def _buy(self, etf_code: str, etf_name: str, price: float, trade_date: date):
        """买入操作"""
        if price <= 0:
            return

        # 计算可买入股数（整数，100股为单位）
        available_cash = self.capital * 0.95  # 保留5%现金
        shares = int(available_cash / price / 100) * 100

        if shares < 100:
            logger.debug(f"{trade_date} {etf_code} 资金不足，无法买入")
            return

        amount = shares * price
        self.capital -= amount

        self.positions[etf_code] = {
            'shares': shares,
            'buy_price': price,
            'buy_date': trade_date,
            'etf_name': etf_name
        }

        trade = TradeRecord(
            etf_code=etf_code,
            etf_name=etf_name,
            action='buy',
            trade_date=trade_date,
            price=price,
            shares=shares,
            amount=amount
        )
        self.trades.append(trade)

        logger.debug(f"{trade_date} 买入 {etf_name} {shares}股 @ {price}, 金额 {amount:.2f}")

    def _sell(self, etf_code: str, etf_name: str, price: float, trade_date: date):
        """卖出操作"""
        if etf_code not in self.positions:
            logger.debug(f"{trade_date} {etf_code} 无持仓，无法卖出")
            return

        pos = self.positions[etf_code]
        shares = pos['shares']
        buy_price = pos['buy_price']

        amount = shares * price
        profit = amount - shares * buy_price
        self.capital += amount

        trade = TradeRecord(
            etf_code=etf_code,
            etf_name=etf_name,
            action='sell',
            trade_date=trade_date,
            price=price,
            shares=shares,
            amount=amount,
            profit=profit
        )
        self.trades.append(trade)

        del self.positions[etf_code]

        logger.debug(f"{trade_date} 卖出 {etf_name} {shares}股 @ {price}, 盈亏 {profit:.2f}")

    def _record_equity(self, trade_date: date, klines: Dict[str, Dict]):
        """记录权益曲线"""
        # 计算持仓市值
        position_value = 0.0
        for etf_code, pos in self.positions.items():
            # 使用最新价格计算市值
            if etf_code in klines:
                closes = klines[etf_code]['close']
                if closes:
                    latest_price = closes[-1]
                    position_value += pos['shares'] * latest_price
            else:
                position_value += pos['shares'] * pos['buy_price']

        equity = self.capital + position_value

        point = EquityPoint(
            date=trade_date,
            equity=equity,
            cash=self.capital,
            position_value=position_value
        )
        self.equity_curve.append(point)

    def _calculate_metrics(
        self,
        start_date: date,
        end_date: date,
        benchmark_returns: Optional[List[float]] = None
    ) -> BacktestResult:
        """计算回测指标"""
        if not self.equity_curve:
            return self._create_empty_result(start_date, end_date)

        equity_values = [p.equity for p in self.equity_curve]
        final_capital = equity_values[-1]

        # 总收益率
        total_return = (final_capital - self.initial_capital) / self.initial_capital * 100

        # 年化收益率
        days = (end_date - start_date).days
        years = days / 365 if days > 0 else 1
        annual_return = total_return / years if years > 0 else 0

        # 最大回撤
        peak = np.maximum.accumulate(equity_values)
        drawdown = (peak - equity_values) / peak * 100
        max_drawdown = np.max(drawdown)

        # 胜率
        sell_trades = [t for t in self.trades if t.action == 'sell']
        win_trades = [t for t in sell_trades if t.profit > 0]
        loss_trades = [t for t in sell_trades if t.profit <= 0]
        win_rate = len(win_trades) / len(sell_trades) * 100 if sell_trades else 0

        # 夏普比率
        if len(equity_values) > 1:
            returns = np.diff(equity_values) / equity_values[:-1]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # 卡尔马比率
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0

        # 基准收益
        benchmark_return = 0.0
        if benchmark_returns:
            benchmark_return = (benchmark_returns[-1] - benchmark_returns[0]) / benchmark_returns[0] * 100

        excess_return = total_return - benchmark_return

        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=round(total_return, 2),
            annual_return=round(annual_return, 2),
            max_drawdown=round(max_drawdown, 2),
            win_rate=round(win_rate, 2),
            trade_count=len(self.trades),
            win_count=len(win_trades),
            loss_count=len(loss_trades),
            sharpe_ratio=round(sharpe_ratio, 2),
            calmar_ratio=round(calmar_ratio, 2),
            benchmark_return=round(benchmark_return, 2),
            excess_return=round(excess_return, 2),
            trades=self.trades,
            equity_curve=self.equity_curve
        )

    def _create_empty_result(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> BacktestResult:
        """创建空结果"""
        return BacktestResult(
            start_date=start_date or date.today(),
            end_date=end_date or date.today(),
            initial_capital=self.initial_capital,
            final_capital=self.initial_capital,
            total_return=0,
            annual_return=0,
            max_drawdown=0,
            win_rate=0,
            trade_count=0,
            win_count=0,
            loss_count=0,
            sharpe_ratio=0,
            calmar_ratio=0
        )

    def get_equity_curve_data(self) -> Dict:
        """获取权益曲线数据（用于前端图表）"""
        return {
            'dates': [p.date.isoformat() for p in self.equity_curve],
            'equity': [p.equity for p in self.equity_curve],
            'cash': [p.cash for p in self.equity_curve],
            'position_value': [p.position_value for p in self.equity_curve]
        }

    def get_trade_records(self) -> List[Dict]:
        """获取交易记录（用于前端展示）"""
        return [
            {
                'etf_code': t.etf_code,
                'etf_name': t.etf_name,
                'action': t.action,
                'action_display': '买入' if t.action == 'buy' else '卖出',
                'trade_date': t.trade_date.isoformat(),
                'price': t.price,
                'shares': t.shares,
                'amount': round(t.amount, 2),
                'profit': round(t.profit, 2)
            }
            for t in self.trades
        ]


# 单例实例
backtest_engine = BacktestEngine()