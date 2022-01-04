#import eod_fundamental as eod_fund
#import eod_ohlc_pull as eod_ohlc
import pandas_mcal as mcal
import trigger_dates as td
import pandas as pd
import datetime as dt
import sqlalchemy
import math
import time

def backtesting(start, end, iteration):
    start_time = dt.datetime.now()
    engine = sqlalchemy.create_engine('***')
    start = start
    end = end
    dates = mcal.trading_days(start, end, 'INTC')

    #define the trigger dates
    df_trigger_dates, list_trigger_dates_above = td.trigger_date_func_above(start, end)
    df_trigger_dates_below, list_trigger_dates_below = td.trigger_date_func_below(start, end)

    #creating the portfolio tracker df *****************
    signal_tickers = pd.read_csv('***')
    company_id = []
    for i in signal_tickers['ticker']:
        if i not in company_id:
            company_id.append(i)

    tickers = []
    for i in company_id:
        query = "SELECT ticker FROM company_id_sector WHERE company_id = {}".format(i)
        temporary = pd.read_sql_query(query, engine)
        tickers.append(temporary['ticker'][0])

    trading_portfolio = {'date':[]}
    for i in dates:
        trading_portfolio['date'].append(i)

    for i in tickers:
        trading_portfolio[i] = [0]*len(trading_portfolio['date'])

    df_portfolio = pd.DataFrame.from_dict(trading_portfolio)
    df_portfolio = df_portfolio.set_index('date')
    #End of portfolio tracker************************

    #creating networth cash tracker *****************
    portfolio = {'date':[], 'networth':[], 'cash':[]}
    for i in dates:
        portfolio['date'].append(i)
        portfolio['networth'].append(0.0)
        portfolio['cash'].append(0.0)

    df_networth = pd.DataFrame.from_dict(portfolio)
    df_networth = df_networth.set_index('date')
    #End of networth portfolio***********************

    def temp_table(signals, start, end):
        query = "CREATE TABLE temp_table (company_id INT, date date, open FLOAT, high FLOAT, low FLOAT, close FLOAT, adj_close FLOAT, volume FLOAT, market_cap Float, EPS FLOAT, pe_ratio FLOAT,pb_ratio FLOAT, ps_ratio FLOAT);"
        con = engine.connect()
        con.execute(query)

        signals = signals.drop_duplicates('ticker')
        signals = signals[signals.action != 'SHORT']
        
        for i in signals.ticker:
            query = "SELECT * FROM test_table WHERE company_id = {} AND date between '{}' AND '{}'; ".format(i, start, end)
            df = pd.read_sql_query(query, engine)
            df.to_sql('temp_table', con = engine, index = False, if_exists ='append')

        return

    def drop_table():
        query = "DROP TABLE temp_table;"
        con = engine.connect()
        con.execute(query)

        return

    def liquidate(date, date_before, df_networth, df_portfolio):
        cash = 0.00
        tickers = []
        row_before = df_portfolio[df_portfolio.index == date_before] #gets the row before to know what the positions are

        #Update portfolio current date row with day befores postion size 
        for x in df_portfolio.keys(): tickers.append(x)
        with_position = []
        for x in tickers:
            df_portfolio[x][date] = row_before[x][0]
            if row_before[x][0] > 0:
                with_position.append(x)
        
        for i in with_position:  
            #get the company_id for the ticker
            query = "SELECT company_id FROM company_id_sector WHERE ticker = '{}'".format(i)
            df_company_id = pd.read_sql_query(query, engine)
            company_id = df_company_id['company_id'][0]
            query = "SELECT adj_close FROM temp_table WHERE company_id ={} AND date = '{}';".format(company_id, date)
            price = pd.read_sql_query(query, engine)
            price = price['adj_close'][0]
            position_value = float(df_portfolio[i][date])*float(price)
            cash += position_value
            df_portfolio[i][date] = 0
            #print(i, df_portfolio[i][date], position_value, cash)

        df_networth['cash'][date] = df_networth['cash'][date_before] + cash
        df_networth['networth'][date] = df_networth['cash'][date]
        
        return 

    def buy(date_now, date_before, df_networth, df_portfolio, df_long):
        cash = df_networth['cash'][date_now]
        networth = 0.0
        positions = len(df_long)
        pos_size = cash/positions
        #print(pos_size)
        for i in range(len(df_long)): #date ticker action score
            query = "SELECT ticker FROM company_id_sector WHERE company_id = {}".format(df_long['ticker'][i])
            ticker = pd.read_sql_query(query, engine)
            ticker = ticker['ticker'][0]
            query = "SELECT adj_close FROM temp_table WHERE company_id ={} AND date = '{}';".format(df_long['ticker'][i], date_now)
            price = pd.read_sql_query(query, engine)
            price = price['adj_close'][0]

            amount = math.floor(pos_size/price)
            cash -= amount*price
            networth += amount*price
            df_portfolio[ticker][date_now] = amount

        df_networth['cash'][date_now] = cash
        df_networth['networth'][date_now] = networth + cash
        return

    def portfolio_calculator(date, date_before, df_networth, df_portfolio, list_trigger_dates_above):
        networth_temp = 0.00
        tickers = []
        if date in list_trigger_dates_above:
            row = df_portfolio[df_portfolio.index == date]
        else:
            row = df_portfolio[df_portfolio.index == date_before] #gets the row before to know what the positions are

        #Update portfolio current date row with day befores postion size 
        for x in df_portfolio.keys(): tickers.append(x)
        with_position = []
        for x in tickers:
            df_portfolio[x][date] = row[x][0]
            if row[x][0] > 0:
                with_position.append(x)

        #Going through tickers and adding up the current networth
        for i in with_position:  
            #get the company_id for the ticker
            query = "SELECT company_id FROM company_id_sector WHERE ticker = '{}'".format(i)
            df_company_id = pd.read_sql_query(query, engine)
            company_id = df_company_id['company_id'][0]
            query = "SELECT adj_close FROM temp_table WHERE company_id ={} AND date = '{}';".format(company_id, date)
            price = pd.read_sql_query(query, engine)
            price = price['adj_close'][0]
            position_value = float(df_portfolio[i][date])*float(price)
            networth_temp += position_value
            #print(i, position_value, networth_temp)

        df_networth['cash'][date] = df_networth['cash'][date_before]
        df_networth['networth'][date] = networth_temp + df_networth['cash'][date]
        return

    cash = 100000.00 #100k 
    df_networth['cash'][df_networth.index[0]] = cash
    df_networth['cash'][df_networth.index[1]] = cash
    df_networth['networth'][df_networth.index[0]] = cash
    df_networth['networth'][df_networth.index[1]] = cash

    signals = pd.read_csv('***')
    signals = signals.drop(columns='Unnamed: 0')


    for i in range(len(signals)):
        value = dt.datetime.strptime(signals['date'][i], '%Y-%m-%d')
        signals['date'][i] = value.date()

    #create the temporary table
    temp_table(signals, start, end)

    date_before = dates[0]
    liquidate_date = dates[22]
    for i in dates:
        #print(i)
        #call function to check if it a trigger date below
        if i in list_trigger_dates_below:
            pass
            #liquidate function
        if i in list_trigger_dates_above:
            if i != dates[1]:
                liquidate(i, date_before, df_networth, df_portfolio)

            df_long = signals[(signals['date'] == i) & (signals['action'] == 'LONG')]
            df_long = df_long.reset_index(drop=True)
            df_long = df_long.head(30)
            #print('longs', df_long)
            buy(i, date_before, df_networth, df_portfolio, df_long)

        if date_before != dates[0] and i not in list_trigger_dates_above:
            portfolio_calculator(i, date_before, df_networth, df_portfolio, list_trigger_dates_above) #purpose is to calculate value of portfolio

        date_before = i
        
    #write to csv df_netwroth, df_portfolio
    df_networth.to_csv("***{}.csv".format(iteration))
    df_portfolio.to_csv("***{}.csv".format(iteration))

    total_return = ((df_networth['networth'][-1]/df_networth['networth'][0]) -1)
    drop_table()
    end_time = dt.datetime.now()
    elapsed = end_time - start_time
    print(start_time, end_time, elapsed)

    return total_return
