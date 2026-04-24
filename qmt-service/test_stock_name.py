"""
测试获取股票名称的方法
"""
from xtquant import xtdata

print("测试获取股票名称")
print("="*50)

stock_code = "600051.SH"

# 方法1: get_stock_name (已知不存在)
print("1. get_stock_name:")
try:
    name = xtdata.get_stock_name(stock_code)
    print(f"结果: {name}")
except AttributeError as e:
    print(f"不存在: {e}")

# 方法2: 从tick数据获取
print("\n2. 从tick获取:")
tick = xtdata.get_full_tick([stock_code])
print(f"tick keys: {tick[stock_code].keys() if tick and stock_code in tick else 'N/A'}")

# 方法3: download_history_data 返回值
print("\n3. download_history_data 返回值:")
result = xtdata.download_history_data(stock_code, period='1d', start_time='', end_time='')
print(f"返回类型: {type(result)}")
print(f"返回值: {result}")

# 方法4: get_instrument_detail
print("\n4. get_instrument_detail:")
try:
    detail = xtdata.get_instrument_detail(stock_code)
    print(f"返回类型: {type(detail)}")
    print(f"返回值: {detail}")
except AttributeError as e:
    print(f"不存在: {e}")

# 检查xtdata所有属性
print("\n5. xtdata 所有方法:")
attrs = [a for a in dir(xtdata) if not a.startswith('_')]
print(attrs)