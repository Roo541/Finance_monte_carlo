import pandas as pd
import pandas_mcal as mcal
import datetime as dt


def nearest_above(trading_dates, given):
    return min(i for i in trading_dates if i >= given)

def nearest_below(trading_dates, given):
    return max(i for i in trading_dates if i < given)

def trigger_date_func_above(start, end):
    symbol = 'INTC'
    trading_dates = mcal.trading_days(start, end, symbol)   #trading dates
    a = pd.date_range(start, end, freq='BMS') #1st business day of month 

    values = []
    for i in range(len(a)): values.append(a[i].date())

    trigger_dates = {'trigger_date':[]}
    trigger_date_list = []
    for i in range(len(values)):
        var = nearest_above(trading_dates,values[i])
        trigger_dates['trigger_date'].append(var)
        trigger_date_list.append(var)

    final_trigger_dates = pd.DataFrame.from_dict(trigger_dates)
    return final_trigger_dates, trigger_date_list

def trigger_date_func_below(start, end):
    symbol = 'INTC'
    trading_dates = mcal.trading_days(start, end, symbol)   #trading dates
    a = pd.date_range(start, end, freq='BMS') #1st business day of month 

    values = []
    for i in range(len(a)): values.append(a[i].date())

    trigger_dates = {'trigger_date':[]}
    trigger_date_list = []
    for i in range(len(values)):
        var = nearest_below(trading_dates,values[i])
        trigger_dates['trigger_date'].append(var)
        trigger_date_list.append(var)

    final_trigger_dates = pd.DataFrame.from_dict(trigger_dates)
    return final_trigger_dates, trigger_date_list
