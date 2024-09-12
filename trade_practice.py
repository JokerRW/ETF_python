from Data import getData #自製的用yfinance抓取資料
from Data import getDataFinMind #自製的用finmind抓取資料
from BackTest import ChartCandle, ChartTrade, Performance #自製Trade圖
import pandas as pd 


# 抓取00878 回測資料
prod='00878'
data = getData(prod, '2020-01-01', '2024-09-01')

# 初始部位
position=0
trade=pd.DataFrame()

# 開始回測
for i in range(data.shape[0]-1):
    # 取得策略會用到的變數
    c_time=data.index[i]
    c_open=data.loc[c_time, 'open']
    c_high=data.loc[c_time, 'high']
    c_low=data.loc[c_time, 'low']
    c_close=data.loc[c_time, 'close']

    # 下一期資料作為進場資料
    n_time=data.index[i+1]
    n_open=data.loc[n_time,'open']

    # 進場程序
    if position == 0 :
        # 進場邏輯
        if c_close > c_open and (c_close-c_open) * 2 < (c_open-c_low):
            position = 1
            order_i = i
            order_time = n_time
            order_price = n_open
            order_unit = 1
           # print(c_time, '觸發進場訊號 隔日進場', order_time, '進場價', order_price, '進場', order_unit, '單位')

    # 出場程序
    elif position == 1 :
        # 出場邏輯
        if i > order_i + 3 and c_close > c_open :
            position = 0
            cover_time=n_time
            cover_price=n_open
            # print(c_time, '觸發出場訊號 隔日出場', cover_time, '出場價', cover_price)
            # 交易紀錄
            trade=pd.concat([trade, pd.DataFrame([[prod, 'Buy', order_time, order_price, cover_time, cover_price, order_unit]])], ignore_index=True)

# 顯示交易紀錄

# print(trade)
# print(data.head())

# 繪製K線圖與交易明細
ChartTrade(data, trade)

# 績效分析
Performance(trade, 'ETF')