"""
测试不同的数据获取方法
"""
from xtquant import xtdata
import pandas as pd

print("测试不同的数据获取方法")
print("="*50)

# 获取股票列表
stock_list = xtdata.get_stock_list_in_sector("沪深A股")
test_stock = stock_list[0] if stock_list else "000001.SZ"
print(f"测试股票: {test_stock}")

# 方法1: get_market_data (已知返回空)
print("\n1. get_market_data:")
kline1 = xtdata.get_market_data(
    stock_list=[test_stock],
    period='1d',
    count=5
)
print(f"close DataFrame empty: {kline1['close'].empty}")
print(f"close shape: {kline1['close'].shape}")

# 方法2: get_history_data
print("\n2. get_history_data:")
try:
    kline2 = xtdata.get_history_data(
        stock_code=test_stock,
        period='1d',
        count=5,
        dividend_type='none'
    )
    print(f"返回类型: {type(kline2)}")
    if kline2:
        print(f"返回内容: {kline2}")
except Exception as e:
    print(f"错误: {e}")

# 方法3: get_market_data_ex
print("\n3. get_market_data_ex:")
try:
    kline3 = xtdata.get_market_data_ex(
        stock_list=[test_stock],
        period='1d',
        count=5
    )
    print(f"返回类型: {type(kline3)}")
    if kline3:
        print(f"返回keys: {kline3.keys() if hasattr(kline3, 'keys') else 'N/A'}")
        if test_stock in kline3:
            print(f"stock data: {kline3[test_stock]}")
            if hasattr(kline3[test_stock], 'columns'):
                print(f"columns: {kline3[test_stock].columns}")
                if 'close' in kline3[test_stock].columns:
                    closes = kline3[test_stock]['close']
                    print(f"close values: {closes.values}")
                    print(f"MA5: {closes.mean()}")
except Exception as e:
    print(f"错误: {e}")

# 方法4: download_history_data + get_market_data
print("\n4. 先下载历史数据:")
try:
    # 先下载历史数据
    xtdata.download_history_data(test_stock, period='1d', start_time='', end_time='')
    print("下载完成")

    # 再获取
    kline4 = xtdata.get_market_data_ex(
        stock_list=[test_stock],
        period='1d',
        count=5
    )
    print(f"返回类型: {type(kline4)}")
    if kline4 and test_stock in kline4:
        df = kline4[test_stock]
        print(f"DataFrame shape: {df.shape}")
        print(f"columns: {df.columns}")
        if not df.empty and 'close' in df.columns:
            closes = df['close']
            print(f"close values: {closes.values}")
            print(f"MA5: {closes.mean()}")
except Exception as e:
    print(f"错误: {e}")

# 方法5: 使用get_full_tick获取当前价格
print("\n5. get_full_tick (已知可用):")
tick = xtdata.get_full_tick([test_stock])
if tick and test_stock in tick:
    print(f"lastPrice: {tick[test_stock]['lastPrice']}")
    print(f"preClose: {tick[test_stock]['lastClose']}")