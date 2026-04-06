"""
测试数据初始化脚本

初始化预警条件、监控股票池、计划任务等测试数据
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from loguru import logger

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from config.database import TORTOISE_ORM
from models.warning import WarningCondition, IndicatorLibrary, WarningStockPool
from models.monitor_pool import MonitorStock
from models.scheduler import SchedulerTask
from utils.warning_evaluator import WARNING_CONDITIONS_PRESET


# 指标库预设数据
INDICATOR_LIBRARY_PRESET = [
    {
        'indicator_key': 'MA',
        'indicator_name': '移动平均线',
        'category': 'TREND',
        'description': '移动平均线是最基本的技术指标，用于判断趋势方向',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 5, 'min': 1, 'max': 100}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
    {
        'indicator_key': 'EMA',
        'indicator_name': '指数移动平均',
        'category': 'TREND',
        'description': '指数移动平均对近期价格赋予更大权重',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 12}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
    {
        'indicator_key': 'EXPMA',
        'indicator_name': 'EXPMA指标',
        'category': 'TREND',
        'description': 'EXPMA与EMA相同，常用于短线交易',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 12}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
    {
        'indicator_key': 'BOLL',
        'indicator_name': '布林带',
        'category': 'TREND',
        'description': '布林带由三条轨道线组成，用于判断价格的波动区间',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 20}, {'key': 'std_dev', 'type': 'float', 'default': 2.0}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'upper', 'type': 'float'}, {'key': 'middle', 'type': 'float'}, {'key': 'lower', 'type': 'float'}]})
    },
    {
        'indicator_key': 'MACD',
        'indicator_name': 'MACD指标',
        'category': 'MOMENTUM',
        'description': 'MACD是趋势跟踪指标，由DIF、DEA和MACD柱组成',
        'parameters': json.dumps({'params': [{'key': 'fast', 'type': 'int', 'default': 12}, {'key': 'slow', 'type': 'int', 'default': 26}, {'key': 'signal', 'type': 'int', 'default': 9}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'dif', 'type': 'float'}, {'key': 'dea', 'type': 'float'}, {'key': 'macd_bar', 'type': 'float'}]})
    },
    {
        'indicator_key': 'KDJ',
        'indicator_name': 'KDJ指标',
        'category': 'MOMENTUM',
        'description': 'KDJ是随机指标，用于判断超买超卖',
        'parameters': json.dumps({'params': [{'key': 'n', 'type': 'int', 'default': 9}, {'key': 'm1', 'type': 'int', 'default': 3}, {'key': 'm2', 'type': 'int', 'default': 3}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'k', 'type': 'float'}, {'key': 'd', 'type': 'float'}, {'key': 'j', 'type': 'float'}]})
    },
    {
        'indicator_key': 'RSI',
        'indicator_name': 'RSI指标',
        'category': 'OSCILLATOR',
        'description': 'RSI是相对强弱指标，用于判断超买超卖',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 6}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
    {
        'indicator_key': 'CCI',
        'indicator_name': 'CCI指标',
        'category': 'OSCILLATOR',
        'description': 'CCI是顺势指标，用于判断趋势强度',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 14}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
    {
        'indicator_key': 'VOL_MA',
        'indicator_name': '成交量均线',
        'category': 'VOLUME',
        'description': '成交量移动平均线',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 5}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
    {
        'indicator_key': 'VOL_RATIO',
        'indicator_name': '量比',
        'category': 'VOLUME',
        'description': '量比是当前成交量与平均成交量的比值',
        'parameters': json.dumps({'params': [{'key': 'period', 'type': 'int', 'default': 5}]}),
        'output_fields': json.dumps({'outputs': [{'key': 'value', 'type': 'float'}]})
    },
]


# 测试监控股票数据
TEST_MONITOR_STOCKS = [
    {
        'stock_code': '000001',
        'stock_name': '平安银行',
        'monitor_type': 'hold',
        'conditions': ['MA_DEAD_CROSS_DAILY', 'MACD_DEAD_CROSS', 'KDJ_DEAD_CROSS'],
        'remark': '持仓监控测试'
    },
    {
        'stock_code': '600519',
        'stock_name': '贵州茅台',
        'monitor_type': 'hold',
        'conditions': ['MA_DEAD_CROSS_DAILY', 'EXPMA_BREAK_8'],
        'remark': '持仓监控测试'
    },
    {
        'stock_code': '000858',
        'stock_name': '五粮液',
        'monitor_type': 'watch',
        'conditions': ['MA_DEAD_CROSS_DAILY', 'RSI_OVERBOUGHT'],
        'remark': '关注监控测试'
    },
    {
        'stock_code': '601318',
        'stock_name': '中国平安',
        'monitor_type': 'hold',
        'conditions': None,  # 使用全部预警条件
        'remark': '全条件监控测试'
    },
]


# 默认计划任务
DEFAULT_SCHEDULER_TASKS = [
    {
        'task_key': 'detect_warning_signals',
        'task_name': '预警信号检测',
        'task_type': 'monitor',
        'trigger_type': 'cron',
        'trigger_config': '*/15 9-15 * * 1-5',  # 交易时间每15分钟
        'job_path': 'jobs.warning_detector.detect_warnings',
        'description': '定期检查监控股票池，根据预警条件生成预警通知',
        'is_enabled': True
    },
    {
        'task_key': 'monitor_sell_warning',
        'task_name': '监控卖出预警信息',
        'task_type': 'monitor',
        'trigger_type': 'cron',
        'trigger_config': '*/10 9-15 * * 1-5',  # 交易时间每10分钟
        'job_path': 'jobs.monitor_tasks.check_sell_warnings',
        'description': '定时检查预警股票池，生成卖出信号',
        'is_enabled': True
    },
    {
        'task_key': 'daily_report',
        'task_name': '每日策略报告',
        'task_type': 'report',
        'trigger_type': 'cron',
        'trigger_config': '0 16 * * 1-5',  # 每个交易日16点
        'job_path': 'jobs.monitor_tasks.generate_daily_report',
        'description': '生成每日策略运行报告',
        'is_enabled': True
    },
    {
        'task_key': 'cleanup_logs',
        'task_name': '清理过期日志',
        'task_type': 'maintenance',
        'trigger_type': 'cron',
        'trigger_config': '0 0 * * 0',  # 每周日凌晨
        'job_path': 'jobs.monitor_tasks.cleanup_old_logs',
        'description': '清理30天前的任务日志',
        'is_enabled': True
    },
]


async def init_indicator_library():
    """初始化指标库数据"""
    logger.info("初始化指标库...")
    count = 0
    for indicator in INDICATOR_LIBRARY_PRESET:
        existing = await IndicatorLibrary.get_or_none(indicator_key=indicator['indicator_key'])
        if not existing:
            await IndicatorLibrary.create(**indicator)
            count += 1
    logger.info(f"指标库初始化完成: 新增 {count} 条记录")


async def init_warning_conditions():
    """初始化预警条件数据"""
    logger.info("初始化预警条件...")
    count = 0
    for condition in WARNING_CONDITIONS_PRESET:
        existing = await WarningCondition.get_or_none(condition_key=condition['condition_key'])
        if not existing:
            await WarningCondition.create(**condition)
            count += 1
    logger.info(f"预警条件初始化完成: 新增 {count} 条记录")


async def init_monitor_stocks():
    """初始化监控股票池数据"""
    logger.info("初始化监控股票池...")
    count = 0
    for stock in TEST_MONITOR_STOCKS:
        existing = await MonitorStock.get_or_none(stock_code=stock['stock_code'])
        if not existing:
            await MonitorStock.create(**stock)
            count += 1
    logger.info(f"监控股票池初始化完成: 新增 {count} 条记录")


async def init_scheduler_tasks():
    """初始化计划任务数据"""
    logger.info("初始化计划任务...")
    count = 0
    for task in DEFAULT_SCHEDULER_TASKS:
        existing = await SchedulerTask.get_or_none(task_key=task['task_key'])
        if not existing:
            await SchedulerTask.create(**task)
            count += 1
    logger.info(f"计划任务初始化完成: 新增 {count} 条记录")


async def create_test_warnings():
    """创建测试预警数据（模拟已触发的预警）"""
    logger.info("创建测试预警数据...")

    # 清理旧的测试预警
    await WarningStockPool.filter(stock_code__in=['000001', '600519']).delete()

    # 创建模拟预警数据
    test_warnings = [
        {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'price': 12.35,
            'change_percent': -1.25,
            'condition_key': 'MA_DEAD_CROSS_DAILY',
            'condition_name': '日线MA死叉',
            'warning_level': 'critical',
            'trigger_time': datetime.now() - timedelta(hours=2),
            'trigger_value': {
                'prev_val1': 12.50,
                'curr_val1': 12.35,
                'prev_val2': 12.40,
                'curr_val2': 12.45
            },
            'is_handled': False
        },
        {
            'stock_code': '600519',
            'stock_name': '贵州茅台',
            'price': 1920.00,
            'change_percent': -0.58,
            'condition_key': 'EXPMA_BREAK_8',
            'condition_name': 'EXPMA8跌破',
            'warning_level': 'warning',
            'trigger_time': datetime.now() - timedelta(hours=1),
            'trigger_value': {
                'close': 1920.00,
                'indicator_value': 1925.50
            },
            'is_handled': False
        },
        {
            'stock_code': '000001',
            'stock_name': '平安银行',
            'price': 12.30,
            'change_percent': -1.65,
            'condition_key': 'KDJ_DEAD_CROSS',
            'condition_name': 'KDJ死叉',
            'warning_level': 'critical',
            'trigger_time': datetime.now() - timedelta(minutes=30),
            'trigger_value': {
                'prev_val1': 75.2,
                'curr_val1': 68.5,
                'prev_val2': 72.1,
                'curr_val2': 70.8
            },
            'is_handled': False
        },
    ]

    count = 0
    for warning in test_warnings:
        await WarningStockPool.create(**warning)
        count += 1

    logger.info(f"测试预警数据创建完成: 新增 {count} 条记录")


async def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始初始化测试数据...")
    logger.info("=" * 50)

    # 初始化数据库连接 - 使用 db_url 格式
    db_url = "mysql://root:1qaz2wsx@localhost:3306/stock_policy"

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["models.warning", "models.monitor_pool", "models.scheduler", "aerich.models"]},
        use_timezone="Asia/Shanghai",
    )

    try:
        # 初始化各模块数据
        await init_indicator_library()
        await init_warning_conditions()
        await init_monitor_stocks()
        await init_scheduler_tasks()
        await create_test_warnings()

        # 统计数据
        indicator_count = await IndicatorLibrary.all().count()
        condition_count = await WarningCondition.all().count()
        stock_count = await MonitorStock.all().count()
        task_count = await SchedulerTask.all().count()
        warning_count = await WarningStockPool.all().count()

        logger.info("=" * 50)
        logger.info("测试数据初始化完成!")
        logger.info(f"指标库: {indicator_count} 条")
        logger.info(f"预警条件: {condition_count} 条")
        logger.info(f"监控股票: {stock_count} 条")
        logger.info(f"计划任务: {task_count} 条")
        logger.info(f"预警记录: {warning_count} 条")
        logger.info("=" * 50)

    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())