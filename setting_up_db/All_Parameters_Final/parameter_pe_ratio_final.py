import eod_fundamental as eod
import eod_ohlc_pull as ohlc
import pandas_mcal as mcal
import pandas as pd
import datetime as dt
from datetime import timedelta
import numpy as np

def pe_data(start, end, symbol):
    #pull fundamental, trading dates, and ohlc data
    a = eod.fundamental_data(symbol)
    dates = mcal.trading_days(start, end, symbol)
    data = ohlc.ohlc(start, end, symbol)
    df_ohlc = pd.DataFrame.from_dict(data)
    for i in range(len(df_ohlc)):
        other = dt.datetime.strptime(df_ohlc['date'][i], '%Y-%m-%d')
        df_ohlc['date'][i] = other.date()

    try:
        #get the keys for fundamental EPS history dates
        eps_keys = []
        for i in a['Earnings']['History']:
            eps_keys.append(i)
        #go through EPS history fundamentals and save EPS with quarter
        trial ={'date':[], 'epsActual':[]}
        for i in eps_keys:
            theta = a['Earnings']['History'][i]['reportDate']
            theta = dt.datetime.strptime(theta, '%Y-%m-%d')
            theta = theta.date()
            phi = a['Earnings']['History'][i]['epsActual']
            trial['date'].append(theta)
            trial['epsActual'].append(phi)
        #eps df with date and epsActual
        eps_df = pd.DataFrame.from_dict(trial)
        #find the pe_ratio for each trading date
        pe_ratio = {'date':[], 'pe_ratio':[]}
        for i in dates:
            previous = i - dt.timedelta(days=365)
            summation = 0.0
            temp = df_ohlc.loc[df_ohlc['date'] == i]
            temp = temp.reset_index()
            adj_close = temp['adjusted_close'][0]
            pe_ratio['date'].append(i)
            for j in range(len(eps_df)):
                if eps_df['date'][j] > previous and eps_df['date'][j] < i:
                    #print(eps_df['date'][j], eps_df['epsActual'][j])
                    summation += eps_df['epsActual'][j]
            pe = adj_close/summation
            if pe != np.nan and pe != np.inf:
                pe_ratio['pe_ratio'].append(pe)
            else:
                pe_ratio['pe_ratio'].append(None)

        #final df with date and pe_ratio
        df_pe = pd.DataFrame.from_dict(pe_ratio)
        return df_pe

    except:
        return 0