"""
测试 get_market_data 返回格式
"""
from xtquant import xtdata

print("测试 xtdata.get_market_data 返回格式")
print("="*50)

# 获取股票列表
stock_list = xtdata.get_stock_list_in_sector("沪深A股")
print(f"股票数量: {len(stock_list)}")
print(f"前3只股票: {stock_list[:3]}")

# 测试 get_market_data
test_stock = stock_list[0] if stock_list else "000001.SZ"
print(f"\n测试股票: {test_stock}")

# 获取5日K线
kline = xtdata.get_market_data(
    stock_list=[test_stock],
    period='1d',
    count=5
)

print(f"\n返回类型: {type(kline)}")
print(f"返回内容: {kline}")

if kline:
    print(f"\nKeys: {kline.keys() if hasattr(kline, 'keys') else 'N/A'}")
    if 'close' in kline:
        print(f"close 类型: {type(kline['close'])}")
        print(f"close 内容: {kline['close']}")

# 测试多个股票
print("\n" + "="*50)
print("测试多个股票")
kline2 = xtdata.get_market_data(
    stock_list=stock_list[:3],
    period='1d',
    count=5
)
print(f"返回类型: {type(kline2)}")
print(f"返回内容 keys: {kline2.keys() if hasattr(kline2, 'keys') else 'N/A'}")

# 测试 get_full_tick
print("\n" + "="*50)
print("测试 get_full_tick")
tick = xtdata.get_full_tick([test_stock])
print(f"tick 类型: {type(tick)}")
if tick and test_stock in tick:
    print(f"tick[{test_stock}]: {tick[test_stock]}")