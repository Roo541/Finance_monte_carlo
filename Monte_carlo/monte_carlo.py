import sqlalchemy 
import pandas as pd 
import strategy_creator as strategy
import random as rand 
import backtest 
import datetime as dt
import math

#define length of simulation
start = '2015-12-31'
end = '2016-12-31'
start_time = dt.datetime.now()
returns = {'iteration':[], 'return':[], 'p1':[],'p2':[] ,'p3':[], 'p4':[], 'p5':[]}
#make strategy 
for i in range(500):
    v1 = rand.randint(-100,100)
    v2 = rand.randint(-100,100)
    v3 = rand.randint(-100,100)
    v4 = rand.randint(-100,100)
    v5 = rand.randint(-100,100)

    mag = math.sqrt(v1*v1+v2*v2+v3*v3+v4*v4+v5*v5)

    p1 = (v1/mag)
    p2 = (v2/mag)
    p3 = (v3/mag)
    p4 = (v4/mag)
    p5 = (v5/mag) 

    strategy.strategy(p1, p2, p3, p4, p5, start, end)
    alpha = backtest.backtesting(start, end, i)

    returns['iteration'].append(i)
    returns['return'].append(alpha)
    returns['p1'].append(p1)
    returns['p2'].append(p2)
    returns['p3'].append(p3)
    returns['p4'].append(p4)
    returns['p5'].append(p5)

    df_returns = pd.DataFrame.from_dict(returns)
    df_returns.to_csv('***')

end_time = dt.datetime.now()
elapsed = end_time - start_time
print('time total monte carlo', elapsed)
