from pandas.core.frame import DataFrame
import parameter_EPS_final as eps_
import parameter_m_cap_final as mcap_
import parameter_pe_ratio_final as pe_ratio
import parameter_price_book_ratio_final as pb_ratio
import parameter_price_sale_ratio_final as ps_ratio
import pandas_mcal as mcal
import pandas as pd
import datetime as dt
from datetime import timedelta
import sqlalchemy
import eod_ohlc_pull as ohlc
import time
import numpy as np

#newest version 12/01/21
start = '2000-01-01'
end = '2021-11-28'

df_tickers = pd.read_csv('company_id.csv')

def roll_through(start, end, symbol, company_id):
    try:
        errors = []
        #get trading dates
        dates = mcal.trading_days(start, end, symbol)
        #get individual parameters in df format
        eps = eps_.eps_data(start, end, symbol)
        mcap = mcap_.mcap_data(start, end, symbol)
        pe = pe_ratio.pe_data(start, end, symbol)
        pb = pb_ratio.pb_data(start, end, symbol)
        ps = ps_ratio.ps_data(start, end, symbol)

        #ohlc pricing data and proper formating 
        data = ohlc.ohlc(start, end, symbol)
        df_ohlc = pd.DataFrame(data)
        for i in range(len(df_ohlc)):
            other = dt.datetime.strptime(df_ohlc['date'][i], '%Y-%m-%d')
            df_ohlc['date'][i] = other.date()

        if type(eps) == type(df_tickers) and type(mcap) == type(df_tickers) and type(pe) == type(df_tickers) and type(pb) == type(df_tickers) and type(ps) == type(df_tickers):
            #all the big stuff
            parameters = {'company_id':[], 'date':[], 'open':[], 'high':[], 'low':[], 'close':[], 
                            'adj_close':[], 'volume':[], 'market_cap':[], 'EPS':[], 'pe_ratio':[], 
                            'pb_ratio':[], 'ps_ratio':[]}
            for i in dates:
                df_pricing = df_ohlc.loc[df_ohlc['date'] == i]
                df_pricing = df_pricing.reset_index(drop=True)
                EPS = eps.loc[eps['date'] == i]
                EPS = EPS.reset_index(drop=True)
                MCAP = mcap.loc[mcap['date'] == i]
                MCAP = MCAP.reset_index(drop = True)
                price_earnings = pe.loc[pe['date'] == i]
                price_earnings = price_earnings.reset_index(drop = True)
                price_book = pb.loc[pb['date'] == i]
                price_book = price_book.reset_index(drop = True)
                price_sales = ps.loc[ps['date'] == i]
                price_sales = price_sales.reset_index(drop = True)
                parameters['company_id'].append(company_id)
                parameters['date'].append(i)
                parameters['open'].append(round(df_pricing['open'][0],4))
                parameters['high'].append(round(df_pricing['high'][0],4))
                parameters['low'].append(round(df_pricing['low'][0],4))
                parameters['close'].append(round(df_pricing['close'][0],4))
                parameters['adj_close'].append(round(df_pricing['adjusted_close'][0],4))
                parameters['volume'].append(round(df_pricing['volume'][0],4))
                parameters['market_cap'].append(round(MCAP['market_cap'][0],4))
                parameters['EPS'].append(round(EPS['EPS'][0],4))
                parameters['pe_ratio'].append(round(price_earnings['pe_ratio'][0],4))
                parameters['pb_ratio'].append(round(price_book['pb_ratio'][0],4))
                parameters['ps_ratio'].append(round(price_sales['ps_ratio'][0],4))        

            #format df properly and push to mysql database
            final = pd.DataFrame.from_dict(parameters)
            final.to_csv('ts_8.csv')
            engine = sqlalchemy.create_engine('***')
            final.to_sql('TRIAL', con=engine, index = False, if_exists = 'append')
            
            return 0 , 0
        else:
            return company_id, symbol
    except:
        return company_id, symbol

bad_tickers = {'company_id':[], 'ticker':[]}
for i in range(2616, len(df_tickers)):
    print(i, df_tickers['tickers'][i])
    fun, wow = roll_through(start, end, df_tickers['tickers'][i], df_tickers['company_id'][i])
    if fun != 0 and wow != 0:
        bad_tickers['company_id'].append(fun)
        bad_tickers['ticker'].append(wow)

df_errors = pd.DataFrame.from_dict(bad_tickers)
df_errors.to_csv('error_tickers.csv')


