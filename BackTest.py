import mplfinance as mpf

#繪製蠟燭圖

def ChartCandle(data, addp=[]):
    mcolor=mpf.make_marketcolors(up='r', down='g', inherit=True)
    mstyle=mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mcolor)
    mpf.plot(data, type='candle', style=mstyle, volume=True)