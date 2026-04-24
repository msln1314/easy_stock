"""
测试因子筛选逻辑
"""
from xtquant import xtdata

print("测试因子筛选逻辑")
print("="*50)

# 获取股票列表
stock_list = xtdata.get_stock_list_in_sector("沪深A股")
print(f"股票总数: {len(stock_list)}")

# 测试前10只股票
test_stocks = stock_list[:10]
print(f"测试股票: {test_stocks}")

for stock_code in test_stocks:
    print(f"\n--- {stock_code} ---")

    # 获取tick数据
    tick = xtdata.get_full_tick([stock_code])
    if tick and stock_code in tick:
        last_price = tick[stock_code].get('lastPrice', 0)
        print(f"lastPrice: {last_price}")

        if last_price <= 0:
            print("跳过: 价格为0")
            continue

        # 计算MA5
        # 先下载历史数据
        xtdata.download_history_data(stock_code, period='1d', start_time='', end_time='')

        # 获取数据
        kline = xtdata.get_market_data_ex(
            stock_list=[stock_code],
            period='1d',
            count=5
        )

        if kline and stock_code in kline:
            df = kline[stock_code]
            print(f"DataFrame shape: {df.shape}")
            if not df.empty and 'close' in df.columns:
                closes = df['close'].values
                print(f"close values: {closes}")
                ma5 = sum(closes) / len(closes) if len(closes) > 0 else 0
                print(f"MA5: {ma5}")

                # 判断条件: MA5 > 5
                if ma5 > 5:
                    print(f"✓ 满足条件 MA5 > 5")
                else:
                    print(f"✗ 不满足条件 MA5 > 5")
            else:
                print("DataFrame empty 或无 close 列")
        else:
            print("无法获取K线数据")
    else:
        print("无法获取tick数据")