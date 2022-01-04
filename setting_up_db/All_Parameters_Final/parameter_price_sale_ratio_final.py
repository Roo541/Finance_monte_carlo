import eod_fundamental as eod
import eod_ohlc_pull as ohlc
import pandas_mcal as mcal
import datetime as dt
from datetime import timedelta
import pandas as pd 
import numpy as np

def ps_data(start, end, symbol):
    a = eod.fundamental_data(symbol)
    df_ohlc = ohlc.ohlc(start, end, symbol)
    df_ohlc = pd.DataFrame.from_dict(df_ohlc)
    dates = mcal.trading_days(start, end, symbol)
    for i in range(len(df_ohlc)):
        other = dt.datetime.strptime(df_ohlc['date'][i], '%Y-%m-%d')
        df_ohlc['date'][i] = other.date()

    try:
        #income statement keys for totalRevenue
        income_statement_keys = []
        for i in a['Financials']['Income_Statement']['quarterly'].keys():
            income_statement_keys.append(i)

        #create df assets and liabilites per quarter
        quarter_revenue_shares = {'quarter':[], 'totalRevenue':[],'shares_outstanding':[]}
        for i in income_statement_keys:
            date = dt.datetime.strptime(i, '%Y-%m-%d')
            date = date.date()
            quarter_revenue_shares['quarter'].append(date)
            quarter_revenue_shares['totalRevenue'].append(a['Financials']['Income_Statement']['quarterly'][i]['totalRevenue'])
            quarter_revenue_shares['shares_outstanding'].append(a['Financials']['Balance_Sheet']['quarterly'][i]['commonStockSharesOutstanding'])

        df_revenue = pd.DataFrame.from_dict(quarter_revenue_shares)

        #go through the dates and make the price_sale_ratio
        ps = {'date':[], 'ps_ratio':[]}
        for i in dates:
            previous = i - dt.timedelta(days=365)
            place_holder = dates[100] - dates[0]
            ps['date'].append(i)
            revenue_sum = 0.0
            #finding the correct assets, liabilities, and shares outstanding for book value
            for j in range(len(df_revenue)):
                if df_revenue['quarter'][j] > previous and df_revenue['quarter'][j] < i:
                    try:
                        revenue_sum += float(df_revenue['totalRevenue'][j])
                    except:
                        revenue_sum = np.nan
                if (i - df_revenue['quarter'][j]) < place_holder and (i - df_revenue['quarter'][j]) > (dates[0]-dates[0]):
                    try:
                        Shares = float(df_revenue['shares_outstanding'][j])
                    except:
                        Shares = np.nan
            #getting the current dates adjusted close
            if revenue_sum != np.nan and Shares != np.nan:
                temp = df_ohlc.loc[df_ohlc['date'] == i]
                temp = temp.reset_index()
                adj_close = temp['adjusted_close'][0]
                sales_share = (revenue_sum)/Shares
                if sales_share != np.inf and sales_share != np.nan:
                    ps['ps_ratio'].append(adj_close/sales_share)
                else:
                    ps['ps_ratio'].append(None)
            else:
                ps['ps_ratio'].append(None)

        ps_ratio = pd.DataFrame.from_dict(ps)
        return ps_ratio
    
    except:
        return 0