import pandas_market_calendars as mcal
import eod_ohlc_pull as ohlc
import eod_fundamental as eod

def trading_days(start, end, symbol):
    a = ohlc.ohlc(start, end, symbol)
    start  = a[-1]['date']
    end = a[0]['date']

    nyse = mcal.get_calendar('NYSE')
    early = nyse.schedule(start_date = start, end_date= end)
    other = []
    for i in early.index:
        other.append(i.date())
        
    
    return other

