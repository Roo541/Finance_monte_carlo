import eod_fundamental as eod
import pandas_mcal as mcal
import datetime as dt
from datetime import timedelta
import pandas as pd
import time

def eps_data(start, end, symbol):
    try:
        #pull the fundamental and trading days 
        a = eod.fundamental_data(symbol)
        dates = mcal.trading_days(start, end, symbol)

        #run through fundamentals and extract the keys for EPS first
        eod_final = {'date':[], 'EPS':[]}
        eps_keys = []
        for i in a['Earnings']['History'].keys():
            eps_keys.append(i)
        #take the EPS and convert string date to datetime.date
        for i in eps_keys:
            reportDate = a['Earnings']['History'][i]['reportDate']
            epsActual = a['Earnings']['History'][i]['epsActual']
            hello = dt.datetime.strptime(reportDate, '%Y-%m-%d')
            eod_final['date'].append(hello.date())
            eod_final['EPS'].append(epsActual)

        #eod reported date and EPS now in df
        eod_df = pd.DataFrame.from_dict(eod_final)

        #run through the trading dates and find the correct EPS for that day by comparing with reported EPS 
        final = {'date':[], 'EPS':[]}
        for i in dates:
            place_holder = dates[100] - dates[0]
            final['date'].append(i)
            for j in range(len(eod_df)):
                if (i - eod_df['date'][j]) < place_holder and (i - eod_df['date'][j]) > (dates[0]-dates[0]):
                    place_holder = (i - eod_df['date'][j])
                    value = eod_df['EPS'][j]
            final['EPS'].append(value)

        #final df of trading day and eps
        df_eps = pd.DataFrame.from_dict(final)
        return df_eps
    
    except:
        pass
        return 0

