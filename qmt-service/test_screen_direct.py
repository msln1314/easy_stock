"""
直接测试因子筛选服务逻辑
"""
import sys
sys.path.insert(0, 'd:/project/other/easy_rich/backend/qmt-service')

from xtquant import xtdata

print("测试因子筛选")
print("="*50)

# 获取股票列表
stock_list = xtdata.get_stock_list_in_sector("沪深A股")
print(f"股票总数: {len(stock_list)}")

# 测试筛选逻辑 - 只处理前20只股票
results = []
for stock_code in stock_list[:20]:
    try:
        # 获取tick数据
        tick = xtdata.get_full_tick([stock_code])
        if not tick or stock_code not in tick:
            print(f"Skip {stock_code}: no tick data")
            continue

        last_price = tick[stock_code].get('lastPrice', 0)
        if last_price <= 0:
            print(f"Skip {stock_code}: price <= 0")
            continue

        # 计算MA5 - 需要先下载历史数据
        xtdata.download_history_data(stock_code, period='1d', start_time='', end_time='')
        kline = xtdata.get_market_data_ex(
            stock_list=[stock_code],
            period='1d',
            count=5
        )

        if kline and stock_code in kline:
            df = kline[stock_code]
            if not df.empty and 'close' in df.columns:
                closes = df['close'].values
                ma5 = sum(closes) / len(closes) if len(closes) > 0 else 0

                # 判断条件: MA5 > 5
                if ma5 > 5:
                    results.append({
                        'stock_code': stock_code,
                        'ma5': round(ma5, 2),
                        'last_price': last_price
                    })
                    print(f"Match: {stock_code} MA5={ma5:.2f} Price={last_price}")
                else:
                    print(f"No match: {stock_code} MA5={ma5:.2f} <= 5")
            else:
                print(f"Skip {stock_code}: empty dataframe or no close")
        else:
            print(f"Skip {stock_code}: no kline data")
    except Exception as e:
        print(f"Error {stock_code}: {e}")

print(f"\n匹配股票数: {len(results)}")
print(f"匹配股票: {results}")