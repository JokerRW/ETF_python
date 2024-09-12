import mplfinance as mpf
import pandas as pd 
import matplotlib.pyplot as plt

#繪製蠟燭圖

def ChartCandle(data, addp=[]):
    mcolor=mpf.make_marketcolors(up='r', down='g', inherit=True)
    mstyle=mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mcolor)
    mpf.plot(data, type='candle', style=mstyle, volume=True)

def ChartTrade(data, trade=pd.DataFrame(), addp=[], v_enable=True):
    addp = addp.copy()
    data1 = data.copy()
    # 如果有交易紀錄, 則把交易紀錄與K線彙整
    if trade.shape[0] > 0:
        #將物件複製出來，不影響原本的交易明細變數
        trade1=trade.copy()
        #取出進場明細，透過時間索引將資料合併
        buy_order_trade = trade1[[2,3]] # date and price
        buy_order_trade = buy_order_trade.set_index(2)
        buy_order_trade.columns=['buy_order']
        buy_order_trade=buy_order_trade.drop_duplicates()

        #取出出場明細，透過時間索引將資料合併
        buy_cover_trade = trade1[[4,5]] # date and price
        buy_cover_trade = buy_cover_trade.set_index(4)
        buy_cover_trade.columns=['buy_cover']
        buy_cover_trade=buy_cover_trade.drop_duplicates()

        #將交易紀錄與K線資料彙整
        data1=pd.concat([data1, buy_order_trade, buy_cover_trade], axis=1)

        #將交易紀錄透過副圖的方式繪製
        addp.append(mpf.make_addplot(data1['buy_order']
                        ,type='scatter', color='#FF4500'
                        ,marker='^', markersize=50))

        addp.append(mpf.make_addplot(data1['buy_cover']
                        ,type='scatter', color='#16982B'
                        ,marker='v', markersize=50))

        #繪製圖表
        mcolor=mpf.make_marketcolors(up='r', down='g', inherit=True)
        mstyle=mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mcolor)
        mpf.plot(data1, addplot=addp, style=mstyle, type='candle',volume=v_enable)

#計算交易績效指標
def Performance(trade=pd.DataFrame(), prodtype='ETF'):
    # 如果沒有交易紀錄，則不做接下來的計算
    if trade.shape[0]==0:
        print('沒有交易紀錄')
        return False

    # 交易成本 手續費0.1425% * 2 (無計算券商打折)
    if prodtype=='ETF':
        cost = 0.001 + 0.00285 # ETF 稅金 0.1%
    elif prodtype=='Stock':
        cost = 0.003 + 0.00285 # 股票 稅金 0.3%
    else:
        return False

    #將物件複製出來, 不影響原本的變數內容
    trade1 = trade.copy()
    trade1 = trade1.sort_values(2)
    trade1 = trade1.reset_index(drop=True)

    #給交易明細定義欄位名稱
    trade1.columns=['product','bs','order_time','order_price','cover_time','cover_price','order_unit']

    #計算每筆的報酬率
    trade1['ret']=(((trade1['cover_price']-trade1['order_price'])/trade1['order_price'])-cost)*trade1['order_unit']

    # 1. 總報酬率: 整個回測期間的總報酬率
    print('總績效 %s '%(trade1['ret'].sum().round(4)))

    # 2. 總交易次數: 整個回測的交易筆數
    print('交易次數 %s ' %(trade1.shape[0]))

    # 3. 平均報酬率 (扣除交易成本)
    print('平均績效 %s ' %(trade1['ret'].mean().round(4)))

    # 4. 平均持有時間
    onopen_day = (trade1['cover_time']-trade1['order_time']).mean()
    print('平均持有時間 %s 天' %(onopen_day.days))
    #判斷是否獲利跟虧損都有績效
    earn_trade=trade1[trade1['ret']>0]
    loss_trade=trade1[trade1['ret']<=0]
    if earn_trade.shape[0] == 0 or loss_trade.shape[0] == 0:
        print('交易資料樣本不足(樣本中需要有賺有賠)')
        return False

    # 5. 勝率: 交易次數中獲勝的占比
    earn_ratio= earn_trade.shape[0]/trade1.shape[0]
    print('勝率 %s'%(round(earn_ratio, 2)))

    # 6. 平均獲利: 
    avg_earn = earn_trade['ret'].mean().round(4)
    print('平均獲利 %s' %(avg_earn))

    # 7. 平均虧損:
    avg_loss = loss_trade['ret'].mean().round(4)
    print('平均虧損 %s' %(avg_loss))

    # 8. 賺賠筆:
    odds = abs(avg_earn/avg_loss)
    print('賺賠比 %s' %(odds.round(4)))

    # 9. 期望值: 代表每投入的金額, 可能回報多少倍的金額 (期望值 = (勝率*賺賠比) / (1 - 勝率))
    print('期望值 %s' %(((earn_ratio*odds)-(1-earn_ratio)).round(4)))

    # 10. 獲利平均持有時間: 代表獲利平均每筆交易的持有時間
    earn_onopen_day = (earn_trade['cover_time']-earn_trade['order_time']).mean()
    print('獲利平均持有天數 %s 天' %(earn_onopen_day.days))

    # 11. 虧損平均持有時間: 代表虧損平均每筆交易的持有時間 
    loss_onopen_day = (loss_trade['cover_time']-loss_trade['order_time']).mean()
    print('虧損平均持有天數 %s 天' %(loss_onopen_day.days))

    # 12. 最大連續虧損:代表連續虧損的最大幅度
    tmp_accloss = 0
    max_accloss = 0
    for ret in trade1['ret'].values:
        if ret <= 0:
            tmp_accloss *= ret
            max_accloss = min(max_accloss, tmp_accloss)
        else:
            tmp_accloss = 0

    # 優先計算累計報酬率 並將累計報酬率的初始值改為1 繪圖比較容易閱讀
    trade1['acc_ret'] = (1 + trade1['ret']).cumprod()
    trade1.loc[-1,'acc_ret'] = 1 #增加一個raw index is -1, 然後column'acc_ret'的位置設為1 (dataframe['columnname] 增加一整個column的值，dataframe.loc['rowname']可以增加一個raw的值)
    trade1.index = trade1.index+1
    trade1.sort_index(inplace=True)

    # 13. 最大資金回落: 代表資金從最高點回落至最低點的幅度
    trade1['acc_max_cap'] = trade1['acc_ret'].cummax()
    trade1['dd'] = (trade1['acc_ret']/trade1['acc_max_cap'])
    trade1.loc[trade1['acc_ret'] == trade1['acc_max_cap'], 'new_high']= trade1['acc_ret']
    print('最大資金回落', round(1-trade1['dd'].min(),4))

    # 繪製資金曲線圖 (用幾何報酬計算)
    ax = plt.subplot(111)
    ax.plot(trade1['acc_ret'], 'b-', label='Profit')
    ax.plot(trade1['dd'], '-', color='#00A600', label='MDD')
    ax.plot(trade1['new_high'], 'o', color='#FF0000', label='Equity high')
    ax.legend()
    plt.show()



