"""
测试QMT获取余额

根据 xtquant 官方示例
"""
from xtquant.xttrader import XtQuantTrader
from xtquant.xttype import StockAccount

print("测试 XtQuantTrader 连接")
print("="*50)

try:
    # QMT客户端路径
    path = r"E:\Program Files\国金QMT交易端模拟\userdata_mini"

    # 会话ID - 任意整数
    session_id = 123456

    # 账号
    account_id = "91003123"

    print(f"路径: {path}")
    print(f"会话ID: {session_id}")
    print(f"账号: {account_id}")
    print()

    # 创建 Trader 实例
    trader = XtQuantTrader(path, session_id)
    print("创建 trader 成功")

    # 创建账号对象
    acc = StockAccount(account_id)
    print(f"创建账号对象成功: {acc}")

    # 启动交易线程
    trader.start()
    print("启动交易线程成功")

    # 连接交易服务器
    connect_result = trader.connect()
    if connect_result == 0:
        print("连接交易服务器成功!")
    else:
        print(f"连接失败，错误码: {connect_result}")
        exit(1)

    # 查询资产
    print("\n查询资产...")
    asset = trader.query_stock_asset(acc)
    if asset:
        print(f"总资产: {asset.total_asset}")
        print(f"可用资金: {asset.cash}")
        print(f"持仓市值: {asset.market_value}")
    else:
        print("查询资产返回空")

    # 查询持仓
    print("\n查询持仓...")
    positions = trader.query_stock_positions(acc)
    print(f"持仓数量: {len(positions)}")
    for p in positions[:5]:  # 只显示前5个
        print(f"  {p.stock_code} {getattr(p, 'stock_name', '')}: {p.volume}股")

    # 停止
    trader.stop()
    print("\n交易已停止")

except Exception as e:
    print(f"失败: {e}")
    import traceback
    traceback.print_exc()