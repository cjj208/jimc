# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 14:43:52 2019

@author: JimchanChen
"""


import tdx_tools
import config as cf
from pytdx.exhq import TdxExHq_API
from pytdx.hq import TdxHq_API
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import pandas as pd
import numpy as np
import matplotlib.ticker as ticker
import go
import matplotlib.animation as animation
import ta
import Indicators 

class ParScan:
    def __init__(self,):
        self.df = df


    def actionOrder(df):
        '''
        多单进场 →Buy
        多单平仓 →Sell
        空单进场 →SellShort
        空单平仓 →BuytoCover
        ▲▼▽△
        '''
    
        #买卖规则
        order = []
        tradeLen = 3 #最多可开多少手
        longCount = 0
        shortCount = 0
        
        for i in df.index:
            #time.sleep(0.1)
    
            buy = (df.iloc[i,df.columns.get_loc("superpoint")]==1) & \
                    (df.iloc[i,df.columns.get_loc("stoch")]>90)
            sell = df.iloc[i,df.columns.get_loc("sma5")] < df.iloc[i,df.columns.get_loc("sma10")]
            
            sellshort = (df.iloc[i,df.columns.get_loc("superpoint")]==-1)  &  \
                        (df.iloc[i,df.columns.get_loc("stoch")]<10)
            buyToCover = df.iloc[i,df.columns.get_loc("sma5")] > df.iloc[i,df.columns.get_loc("sma10")]
            if (buy==True) & (longCount <=tradeLen) & (shortCount ==0):
                longCount += 1
    #            print("__"*50)
                order.append("Buy")
    #            print("多单进场:",longCount)
                
            elif (sell == True) & (longCount != 0):
                longCount = 0
    #            print("__"*50)
                order.append("Sell")
    #            print("多单平仓",longCount)
            elif (sellshort==True) & (shortCount <=tradeLen) & (longCount ==0) :
                shortCount += 1
    #            print("__"*50)
                order.append("SellShort")
    #            print("空单进场",shortCount)
            elif (buyToCover==True) & (shortCount != 0):
                shortCount = 0
    #            print("__"*50)
                order.append("buyToCover")
    #            print("空单平仓",shortCount)
            else:
                order.append("0")
    
        df["order"] = pd.Series(order,)
        #print(df[df.order!='0'])
        return df
    
    def GainLoss(df):
        #计算收益
        gainLoss = []
        openIndex = []
        openPrice = []
        
        for i in list(df["order"].index):
    #        print(gainLoss)
            if df.iloc[i]["order"] == "Buy":
                openIndex.append(i)
                openPrice.append(df.iloc[i]["close"])
    #            ax.text(i,df.iloc[i]["close"],(r'▲'),fontsize=10,color='red',alpha=0.5)
                
                #ax.annotate(s="Buy",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "r",headlength = 5, headwidth =5, width = 5))
            elif df.iloc[i]["order"] == "Sell":
    #            print("头寸位置",openIndex)
    #            print("头寸价格",openPrice)
                gain = df.iloc[i]["close"]-openPrice[-1]
                gainLoss.append(gain)
                openIndex.append(i)
                openPrice.append(df.iloc[i]["close"])
    #            ax.plot(openIndex,openPrice,color='r')
    #            ax.text(i,df.iloc[i]["low"],(r'------'),fontsize=10,color='b',alpha=1)
    #            ax.text(i,df.iloc[i]["low"],(gain),fontsize=10,color='r',alpha=1)
                #ax.annotate(s="Sell",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "g", headlength = 5, headwidth =5, width = 5))
                openIndex = []
                openPrice = []
            elif df.iloc[i]["order"] == "SellShort":
                
                openIndex.append(i)
                openPrice.append(df.iloc[i]["close"])
    #            ax.text(i,df.iloc[i]["close"],(r'▼'),fontsize=10,color='darkgreen',alpha=1)
                
                #ax.annotate(s="空开",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "g", headlength = 5, headwidth =5, width = 5))          
                
            elif df.iloc[i]["order"] == "buyToCover":
                gain = openPrice[-1] - df.iloc[i]["close"]#开仓价减平仓价
                gainLoss.append(gain)
                openIndex.append(i)
                openPrice.append(df.iloc[i]["close"])
    #            ax.text(i,df.iloc[i]["low"],(r'------'),fontsize=10,color='b',alpha=1)
    #            ax.plot(openIndex,openPrice,color='black')
    #            ax.text(i,df.iloc[i]["low"],(gain),fontsize=10,color='g',alpha=1)
                openIndex = []
                openPrice = []
                #ax.annotate(s="空开",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "g", headlength = 5, headwidth =5, width = 5))          
            else:
                pass
    #    for gain in df.index
        gainLoss = pd.DataFrame(gainLoss,)
        
#        gldict = dict(zip(['交易笔数', '交易总盈利', '最大亏损','最大盈利','平均盈亏','中位数'], 
#                          [gainLoss.count(), gainLoss.sum(), gainLoss.min(),gainLoss.max(),gainLoss.mean(),gainLoss.median()]))
#        
#        
#        print(gainLoss)
        

        
#        gldict = {"交易笔数"：gainLoss.count(),
#                "交易总盈利"：gainLoss.sum(),
#                "最大亏损"：gainLoss.min(),
#                "最大盈利"：gainLoss.max(),
#                "平均盈亏"：gainLoss.mean(),
#                "中位数"：gainLoss.median()}

        gainLoss.append(gainLoss)
        return gainLoss
    
    def StochParaData(df,co):
        df['stoch%s'%co] = ta.momentum.stoch(df.high,df.low,df.close,co)
        
        '''
        co=100
        for i in list(range(5,co,5)):
            print(i)
            df['stoch%s'%i] = ta.momentum.stoch(df.high,df.low,df.close,i)
        return df
        '''
        return df
    def SuperParaData(df,co):
        df = tdx_tools.SuperTrend(df,period=co,multiplier=2,ohlc=['open', 'high', 'low', 'close'])
        
        '''
        co=100
        for i in list(range(5,co,5)):
            df = Indicators.SuperTrend(df,period=i,multiplier=2,ohlc=['open', 'high', 'low', 'close'])
            
        #print(df)
        '''
        return df
if __name__ == "__main__":

    cflen=2
    datacent = go.Datacent()
    
    if datacent.qihuo_connectSer() and datacent.gupiao_connectSer():
        qihuocount = list(range(len(cf.cfqihuo))) 
        df = datacent.qihuoK(cflen)
        df = df.iloc[50:]
        df = df.reset_index()    
#        df = tdx_tools.SuperTrend(df,period=cf.st_period_fast,multiplier=cf.st_mult_fast,)
        supCount = 20
        stochCount = 50
        gl = []
        for sup in list(range(5,supCount,2)):
            ParScan.SuperParaData(df,sup)
            for stoch in list(range(5,stochCount,2)):
                ParScan.StochParaData(df,100)
                ParScan.actionOrder(df)
                gldata = ParScan.GainLoss(df)
                
                totalGl = {
                "参数":"Sup%s-stoch%s" % (sup,stoch),
                "交易笔数":gldata.count()[0],
                "交易总盈利":gldata.sum()[0],
                "最大亏损":gldata.min()[0],
                "最大盈利":gldata.max()[0].round(2),
                "平均盈亏":gldata.mean()[0].round(2),
                "中位数":gldata.median()[0],
                }
                print(totalGl)
                gl.append(totalGl)
                print("SuperTend:%s\n"%sup,"Stoch:%s\n"%stoch)
                print("_"*100)
                
        gl = pd.DataFrame(gl)
        print(gl)