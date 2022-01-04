import sqlalchemy 
import pandas as pd 
import strategy_creator as strategy
import random as rand 
import backtest 

#define length of simulation
start = '2019-12-31'
end = '2020-12-31'

returns = {'iteration':[], 'return':[], 'p1':[],'p2':[] ,'p3':[], 'p4':[], 'p5':[]}
#make strategy 
for i in range(100):
    print(i)
    if i == 0:
        p1=p2=p3=p4=p5= 1
    else:
        p1 = i/100
        p2 = 0.5
        p3 = 0.5
        p4 = 0.5
        p5 = 0.5

    strategy.strategy(p1, p2, p3, p4, p5, start, end)
    print('done')
    alpha = backtest.backtesting(start, end, i)

    returns['iteration'].append(i)
    returns['return'].append(alpha)
    returns['p1'].append(p1)
    returns['p2'].append(p2)
    returns['p3'].append(p3)
    returns['p4'].append(p4)
    returns['p5'].append(p5)


df_returns = pd.DataFrame.from_dict(returns)
df_returns.to_csv('****')

