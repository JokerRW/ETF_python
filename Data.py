import yfinance as yf #載入yahoo finance 套件
import pandas as pd
import os
from FinMind.data import DataLoader

#下載0050 ETF
# a = yf.download('0050.tw',start='2020-01-01', end='2024-09-01')
# print(a.tail())

#下載00878 ETF, 期間是前7天，頻率為分Ｋ
# ETF00878 = yf.download('00878.tw',period='5d', interval='1m')
# print(ETF00878.tail())

# res_finmind = getDataFinMind('00878', '2023-01-01', '2024-09-01')
# print(res_finmind.tail())

datapath = "data" #資料存放路徑

# 用yfinance抓資料
def getData(prod, st, en):
    bakfile = 'data//YF_%s_%s_%s_stock_daily_adj.csv' % (prod, st, en)
    if os.path.exists(bakfile):
        data = pd.read_csv(bakfile)
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.set_index('Date')
    else:
        data = yf.download(f"{prod}.TW", start=st, end=en)
        data.columns = [i.lower() for i in data.columns]
        #除錯 如果沒有資料
        if data.shape[0] == 0:
            print('沒有資料')
            return pd.DataFrame()
        #將資料寫入備份檔
        data.to_csv(bakfile)
    return data


# 用finmind抓資料
def getDataFinMind(prod, st, en):
    bakfile = 'data//YF_%s_%s_%s_stock_daily_adj_finmind.csv' % (prod, st, en)
    if os.path.exists(bakfile):
        data = pd.read_csv(bakfile)
        data['date'] = pd.to_datetime(data['date'])
        data = data.set_index('date')
    else:
        FM = DataLoader()
        data = FM.taiwan_stock_daily(stock_id=prod, start_date=st, end_date=en)
        data.columns = [i.lower() for i in data.columns]
        #除錯 如果沒有資料
        if data.shape[0] == 0:
            print('沒有資料')
            return pd.DataFrame()
        #將資料寫入備份檔
        data.to_csv(bakfile)
    return data
