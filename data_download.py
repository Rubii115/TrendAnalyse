'''
i use this program to download candledata and save them
'''

from binance.spot import Spot
import pandas as pd
from datetime import datetime
import os

# 只是下载数据，不需要输入您的API Key和Secret Key
client = Spot()

# 输入您要获取历史数据的虚拟货币
symbol = 'BTCUSDT'
interval='1m'

# 输入您要获取历史数据的时间范围
date_string = '2019-01-01T00:00:00Z'
date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
start = int(date_object.timestamp() * 1000)


# 获取历史数据
klines = client.klines(symbol, interval , startTime=start , limit=1000)
klines_all=klines.copy()
while len(klines)>1:
    start_date = klines_all[-1][0]
    klines = client.klines(symbol, interval , startTime=start_date , limit=1000 )
    if klines_all[-1][0] == klines[0][0]:
        klines = klines[1:]
    klines_all+=klines
    print(datetime.utcfromtimestamp(klines_all[-1][0]/1000))

# 将数据转换为Pandas数据框
df = pd.DataFrame(klines_all, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

# 将时间戳转换为日期
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')

# 删除无用的列
df = df.drop(['timestamp', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'], axis=1)

#如果没有Candle_data/文件夹就创建一个
folder_name = 'Candle_data'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 将数据保存为CSV文件
df.to_csv(folder_name +'/'+interval+'history_data.csv', index=False)
