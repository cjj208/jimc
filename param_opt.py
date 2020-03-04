# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 16:57:06 2019

@author: JimchanChen
"""

from pytdx.exhq import TdxExHq_API
import config as cf
import ta
import tdx_tools
import numpy as np
import pandas as pd

cflen = 2
st_period =10
st_mult =2
#%%
class makeData:
    def __init__(self,df,step,):
        self.df = df
        self.step = step
#        self.rsi_Multi = rsi_Multi
        
    def rsi_Multi(self,):
        for i in list(range(0,self.step,1)):
            df["rsi%s" % i] = ta.momentum.rsi(df.close,n=self.step,)
        return df
    def stoch_Multi(self):
        for i in list(range(0,self.step,1)):
            df["stoch%s" % i] = ta.momentum.stoch(df.high,df.low,df.close,self.step)
        return df
    def tradeaction(self):
        
        ret = df[df.superpoint!=0].reset_index()
        ret['returns'] = np.abs(ret.close.shift(periods=1,axis=0) - ret.close)#算zigzag的回报
        return ret.round(1)
if __name__ == "__main__":
    api = TdxExHq_API()
    with api.connect('218.80.248.229', 7721):
        data = api.get_instrument_bars(cf.category,
                            int(cf.cfqihuo[cflen]["marketid"]),
                            cf.cfqihuo[cflen]['code'], 0,
                            cf.categorycount)#7: 扩展行情查询k线数据
        df = pd.DataFrame(data,columns=['datetime', 'open', 'high', 'low', 'close','trade'])
        df = tdx_tools.SuperTrend(df,period=st_period,multiplier=st_mult,ohlc=['open', 'high', 'low', 'close'])
        md = makeData(df,50)
#        md.rsi_Multi()
#        md.stoch_Multi()
        ret = md.tradeaction()
        print (ret)
        #print (df)




'''
api = TdxExHq_API()
with api.connect('218.80.248.229', 7721):
    data = api.get_instrument_bars(cf.category,
                        int(cf.cfqihuo[cflen]["marketid"]),
                        cf.cfqihuo[cflen]['code'], 0,
                        cf.categorycount)#7: 扩展行情查询k线数据
    
    df = pd.DataFrame(data,columns=['datetime', 'open', 'high', 'low', 'close','trade'])
    
    #df = data[['datetime', 'open', 'high', 'low', 'close','trade']]
    df["rsi"] = ta.momentum.rsi(df.close,n=14,)
    df['stoch'] = ta.momentum.stoch(df.high,df.low,df.close,14)
    df = tdx_tools.SuperTrend(df,period=cf.st_period_fast,multiplier=cf.st_mult_fast,)
    
    df['ema'] = ta.trend.ema_indicator(df.close,n=14,fillna=True)
    df = df.round(2)
    print (df)
    #%%
'''