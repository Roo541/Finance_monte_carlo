from numpy import sign
import pandas as pd 
import pandas_mcal as mcal
import sqlalchemy
import datetime as dt
import trigger_dates as td
import time
engine = sqlalchemy.create_engine('***')


def strategy(p1, p2, p3, p4, p5, start, end):
    start = start
    end = end

    signals = {'date':[], 'ticker':[], 'action':[]}

    df_trigger, list_trigger_below = td.trigger_date_func_below(start, end)
    df_trigger, list_trigger_above = td.trigger_date_func_above(start, end)

    signals = {'date':[], 'ticker':[], 'action':[], 'score':[]}

    for key in range(len(list_trigger_below)):
        query = "SELECT * FROM test_table WHERE date = '{}';".format(list_trigger_below[key])
        df = pd.read_sql_query(query, engine)

        df = df.dropna()

        df['score_1'] = df['score_2'] = df['score_3'] = df['score_4'] = df['score_5'] = df['score_total'] = 0.0

        #score 1 for market cap (low market cap low score)
        df =df.sort_values(by='market_cap', ascending=True)
        df = df.reset_index(drop=True)
        df['score_1']= df.index
        df['score_1'] = df['score_1']*p1

        #score 2 for EPS    (low eps low score)
        df =df.sort_values(by='EPS', ascending=True)
        df = df.reset_index(drop=True)
        df['score_2']= df.index
        df['score_2'] = df['score_2']*p2
        #score 3 for P/E        (negative) (Low p/e high score)
        df =df.sort_values(by='pe_ratio', ascending=True)
        df = df.reset_index(drop=True)
        #loop through to rank score 3 0 -> positive -> negative high negative worst
        count = 0
        for i in range(len(df)):
            if df['pe_ratio'][i] < 0:
                df['score_3'][i] = count
                count += 1
        # going from most positive to zero
        df =df.sort_values(by='pe_ratio', ascending=False)
        df = df.reset_index(drop=True)
        for i in range(len(df)):
            if df['pe_ratio'][i] >= 0:
                df['score_3'][i] = count
                count +=1
        df['score_3'] = df['score_3']*p3

        #score 4 for pb_ratio  (negative issue) (Low pb high score)
        df =df.sort_values(by='pb_ratio', ascending=True)   #want most negative
        df = df.reset_index(drop=True)
        count = 0
        for i in range(len(df)):
            if df['pb_ratio'][i] < 0:
                df['score_4'][i] = count
                count += 1
        # going from most positive to zero
        df =df.sort_values(by='pb_ratio', ascending=False) # want biggest positive
        df = df.reset_index(drop=True)
        for i in range(len(df)):
            if df['pb_ratio'][i] >= 0:
                df['score_4'][i] = count
                count +=1
        df['score_4'] = df['score_4']*p4

        #score 5 for ps_ratio       (low ps high score) negative is worst
        df =df.sort_values(by='ps_ratio', ascending=True)
        df = df.reset_index(drop=True)
        count = 0
        for i in range(len(df)):
            if df['ps_ratio'][i] < 0:
                df['score_5'][i] = count
                count += 1
        # going from most positive to zero
        df =df.sort_values(by='ps_ratio', ascending=False) #want biggest positive
        df = df.reset_index(drop=True)
        for i in range(len(df)):
            if df['ps_ratio'][i] >= 0:
                df['score_5'][i] = count
                count +=1
        df['score_5'] = df['score_5']*p5

        df['score_total'] = df['score_1'] + df['score_2'] + df['score_3'] + df['score_4'] + df['score_5']

        #longs
        df = df.sort_values(by='score_total', ascending=False)
        df = df.reset_index(drop=True)
        for i in range(30):
            signals['date'].append(list_trigger_above[key])
            signals['ticker'].append(df['company_id'][i])
            signals['action'].append('LONG')       
            signals['score'].append(df['score_total'][i])      
        #shorts
        df = df.sort_values(by='score_total', ascending=True)
        df = df.reset_index(drop=True)
        for i in range(30):
            signals['date'].append(list_trigger_above[key])
            signals['ticker'].append(df['company_id'][i])
            signals['action'].append('SHORT')
            signals['score'].append(df['score_total'][i])      

    #write signals to csv
    df_signals = pd.DataFrame.from_dict(signals)
    df_signals.to_csv("***")
    
    return
