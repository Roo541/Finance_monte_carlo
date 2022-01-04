import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import sqlalchemy
import pandas_mcal
import eod_fundamental
import eod_ohlc_pull

def mcap_data(start, end, symbol):
    other = pandas_mcal.trading_days(start, end, symbol)
    #get fundamental data from EOD
    data = eod_fundamental.fundamental_data(symbol)

    try:
        #taking the fundamental data needed for market cap
        quarterly_keys = []
        for i in data['outstandingShares']['quarterly'].keys():
            quarterly_keys.append(i)

        quarters = {'date':[], 'sharesOutstanding':[]}
        for i in quarterly_keys:
            stuff = data['outstandingShares']['quarterly'][i]['dateFormatted']
            hello = dt.strptime(stuff, '%Y-%m-%d')
            quarters['date'].append(hello.date())
            quarters['sharesOutstanding'].append(data['outstandingShares']['quarterly'][i]['shares'])

        df_quarterly = pd.DataFrame.from_dict(quarters)
        final = {'date':[], 'shares':[]}

        for i in other:
            place_holder = other[100] - other[0]
            final['date'].append(i)
            for j in range(len(df_quarterly)):
                if (i - df_quarterly['date'][j]) < place_holder and (i - df_quarterly['date'][j]) > (other[0]-other[0]):
                    place_holder = (i - df_quarterly['date'][j])
                    value = df_quarterly['sharesOutstanding'][j]
            final['shares'].append(value)

        duh = pd.DataFrame.from_dict(final)

        #getting the ohlc data needed for market cap
        ohlc = eod_ohlc_pull.ohlc(start, end, symbol)

        we = {'date':[], 'adj_close':[]}
        for i in range(len(ohlc)):
            date = dt.strptime(ohlc[i]['date'], '%Y-%m-%d')
            date = date.date()
            we['date'].append(date)
            we['adj_close'].append(ohlc[i]['adjusted_close'])

        df_we = pd.DataFrame.from_dict(we)
        finale = {'date':[], 'market_cap':[]}

        for i in range(len(df_we)):
            stuff =  duh[(duh['date']== df_we['date'][i])]
            stuff = stuff.reset_index(drop = True,inplace=False)
            finale['date'].append(df_we['date'][i])
            mcap = df_we['adj_close'][i]* stuff['shares'][0]
            finale['market_cap'].append(mcap)

        #final df of DATE and MCAP for symbol
        kitten = pd.DataFrame.from_dict(finale)
        return kitten
    
    except:
        return 0



