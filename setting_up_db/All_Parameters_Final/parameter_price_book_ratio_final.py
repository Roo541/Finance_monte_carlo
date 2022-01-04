import eod_fundamental as eod
import eod_ohlc_pull as ohlc
import pandas_mcal as mcal
import pandas as pd
import datetime as dt
from datetime import timedelta
import numpy as np

def pb_data(start, end, symbol):
    #get fundamental, ohlc, and trading dates
    a = eod.fundamental_data(symbol)
    df_ohlc = ohlc.ohlc(start, end, symbol)
    df_ohlc = pd.DataFrame.from_dict(df_ohlc)
    dates = mcal.trading_days(start, end, symbol)
    for i in range(len(df_ohlc)):
        other = dt.datetime.strptime(df_ohlc['date'][i], '%Y-%m-%d')
        df_ohlc['date'][i] = other.date()

    try:
        #find keys for balance_sheet, quarterly
        balance_sheet_keys = []
        for i in a['Financials']['Balance_Sheet']['quarterly'].keys():
            balance_sheet_keys.append(i)

        #create df assets and liabilites per quarter
        assets_liabilites = {'quarter':[], 'assets':[], 'liabilities':[], 'shares_outstanding':[]}
        for i in balance_sheet_keys:
            date = dt.datetime.strptime(i, '%Y-%m-%d')
            date = date.date()
            assets_liabilites['quarter'].append(date)
            assets_liabilites['assets'].append(a['Financials']['Balance_Sheet']['quarterly'][i]['totalAssets'])
            assets_liabilites['liabilities'].append(a['Financials']['Balance_Sheet']['quarterly'][i]['totalLiab'])
            assets_liabilites['shares_outstanding'].append(a['Financials']['Balance_Sheet']['quarterly'][i]['commonStockSharesOutstanding'])

        df_financials = pd.DataFrame.from_dict(assets_liabilites)
        #making the price_book ratio df
        pb = {'date':[], 'pb_ratio':[]}
        for i in dates:
            place_holder = dates[100] - dates[0]
            pb['date'].append(i)
            #finding the correct assets, liabilities, and shares outstanding for book value
            for j in range(len(df_financials)):
                if (i - df_financials['quarter'][j]) < place_holder and (i - df_financials['quarter'][j]) > (dates[0]-dates[0]):
                    place_holder = (i - df_financials['quarter'][j])
                    try:
                        Assets = float(df_financials['assets'][j])
                        Liabilities = float(df_financials['liabilities'][j])
                        Shares = float(df_financials['shares_outstanding'][j])
                    except:
                        Shares = np.nan
            #getting the current dates adjusted close
            if Shares != np.nan and Shares != np.inf:
                temp = df_ohlc.loc[df_ohlc['date'] == i]
                temp = temp.reset_index()
                adj_close = temp['adjusted_close'][0]
                book_value = (Assets-Liabilities)/Shares
                pb['pb_ratio'].append(adj_close/book_value)
            else:
                pb['pb_ratio'].append(None)
        pb_ratio = pd.DataFrame.from_dict(pb)
        return pb_ratio

    except:
        return 0