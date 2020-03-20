# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 15:54:42 2019

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
import time
import matplotlib.animation as animation
import Indicators
from ta.trend import MACD
cflen=2

def actionOrder(df):
    '''
    多单进场 →Buy
    多单平仓 →Sell
    空单进场 →SellShort
    空单平仓 →BuytoCover
    ▲▼▽△
    '''

    
    order = []
    tradeLen = 3 #最多可开多少手
    longCount = 0
    shortCount = 0
    
    for i in df.index:
        #time.sleep(0.1)

        buy = (df.iloc[i,df.columns.get_loc("superpoint")]==1) & (df.iloc[i,df.columns.get_loc("sma89144")]==1)
        sell = df.iloc[i,df.columns.get_loc("sma5")] < df.iloc[i,df.columns.get_loc("sma10")]
        sellshort = (df.iloc[i,df.columns.get_loc("superpoint")]==1) & (df.iloc[i,df.columns.get_loc("sma89144")]==-1)
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
    print(df[df.order!='0'])
    return df
def GainLoss():

    gainLoss = []
    openIndex = []
    openPrice = []
    
    for i in list(df["order"].index):
#        print(gainLoss)
        if df.iloc[i]["order"] == "Buy":
            openIndex.append(i)
            openPrice.append(df.iloc[i]["close"])
            ax.text(i,df.iloc[i]["close"],(r'▲'),fontsize=10,color='red',alpha=0.5)
            
            #ax.annotate(s="Buy",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "r",headlength = 5, headwidth =5, width = 5))
        elif df.iloc[i]["order"] == "Sell":
#            print("头寸位置",openIndex)
#            print("头寸价格",openPrice)
            gain = df.iloc[i]["close"]-openPrice[-1]
            gainLoss.append(tuple([i,gain]))
            openIndex.append(i)
            openPrice.append(df.iloc[i]["close"])
            ax.plot(openIndex,openPrice,color='r')
#            ax.text(i,df.iloc[i]["low"],(r'------'),fontsize=10,color='b',alpha=1)
            ax.text(i,df.iloc[i]["low"],(gain),fontsize=10,color='r',alpha=1)
            #ax.annotate(s="Sell",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "g", headlength = 5, headwidth =5, width = 5))
            openIndex = []
            openPrice = []
        elif df.iloc[i]["order"] == "SellShort":
            
            openIndex.append(i)
            openPrice.append(df.iloc[i]["close"])
            ax.text(i,df.iloc[i]["close"],(r'▼'),fontsize=10,color='darkgreen',alpha=1)
            
            #ax.annotate(s="空开",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "g", headlength = 5, headwidth =5, width = 5))          
            
        elif df.iloc[i]["order"] == "buyToCover":
            gain = openPrice[-1] - df.iloc[i]["close"]#开仓价减平仓价
            gainLoss.append(tuple([i,gain]))
            openIndex.append(i)
            openPrice.append(df.iloc[i]["close"])
#            ax.text(i,df.iloc[i]["low"],(r'------'),fontsize=10,color='b',alpha=1)
            ax.plot(openIndex,openPrice,color='black')
            ax.text(i,df.iloc[i]["low"],(gain),fontsize=10,color='g',alpha=1)
            openIndex = []
            openPrice = []
            #ax.annotate(s="空开",xy=(i,df.iloc[i]["close"]),arrowprops = dict(facecolor = "g", headlength = 5, headwidth =5, width = 5))          
        else:
            pass
#    for gain in df.index
    gainLoss = pd.DataFrame(gainLoss,)
    
    print ("交易明细：",gainLoss)
    print ("gainLoss",gainLoss[1].sum())
    return gainLoss

  
if __name__ == "__main__":
    
    
    #%%画K线主图
    datacent = go.Datacent()
    if datacent.qihuo_connectSer():
        
        qihuocount = list(range(len(cf.cfqihuo))) 
        df = datacent.qihuoK(cflen)
      
        df = tdx_tools.SuperTrend(df,period=cf.st_period_fast,multiplier=cf.st_mult_fast,)
        df = tdx_tools.StochRSI(df,m=14,p=7)
        dfmacd = MACD(df['close'],n_slow=10,n_fast=5,n_sign=89)
        df["macd"] = dfmacd.macd()
        df['diff'] = dfmacd.macd_diff()
        df['macd_signal'] = dfmacd.macd_signal()
        
        df = df.iloc[100:]
        
        weekday_quotes=[tuple([i]+list(quote[1:])) for i,quote in enumerate(df.values,)]
        fig = plt.figure(figsize=(1000 / 72, 500 / 72),facecolor='#CCCCCC', edgecolor='#CCCCCC')
        
        df = df.reset_index()    
        df = actionOrder(df)
        
        
        #%%画K线主图
        ax = fig.add_subplot(4,1,(1,2))
        ax.set_facecolor('#CCCCCC')
        ax.set_ylabel('K线主图')
        GainLoss()
        ax2 = fig.add_subplot(4,1,3)
        ax2.set_facecolor('#CCCCCC')
        
        ax3 = fig.add_subplot(4,1,4)
        ax3.set_facecolor('#CCCCCC')    
        
    
    
        #%%画K线主图
        
        date_tickers=df.datetime.values
        def format_date(x,pos=None):
            if x<0 or x>len(date_tickers)-1:
                return ''
            return date_tickers[int(x)]
        ax.plot(df["supertrend"],color="#ff9900",linewidth=0.5,linestyle="-")
        ax.plot(df["sma5"],color="black",linewidth=0.5,linestyle="-")
        ax.plot(df["sma10"],color="black",linewidth=0.5,linestyle="-")
    #    ax.plot(df["sma20"],color="black",linewidth=0.5,linestyle="-")
        ax.plot(df["sma89"],color="black",linewidth=0.5,linestyle="-")
    #    ax.plot(df["sma144"],color="black",linewidth=0.5,linestyle="-")
        ax.set_title("{%s}{%s}{%s}" % (cf.cfqihuo[cflen]["stockname"],cf.cfqihuo[cflen]["code"],tdx_tools.k_zhouqi()))
        candlelist = ['看涨抱线','看涨刺透','看涨孕线','看跌吞没','看跌孕线','看涨一线穿','看跌一线穿']
        candlelist = ['看跌一线穿',]
    
    
        
        # for j in list(df[df["order"]=="sell"].index):
        #     ax.annotate(s="Sell",xy=(j,df.iloc[j]["close"]),arrowprops = dict(facecolor = "g", 
        #                 headlength = 5, headwidth =5, width = 5))
        
        for z in list(df[df["superpoint"]==-1].index):
            ax.text(z,df.iloc[z]["supertrend"],r'--',fontsize=1,bbox=dict(facecolor='red', alpha=0.5))
            #supertrend转折处
            #ax.annotate(s="supS",xy=(z,df.iloc[z]["supertrend"]),arrowprops = dict(facecolor = "b", headlength = 5, headwidth =5, width = 5))
        
        
        '''
        for cand in candlelist:
            for i in df[df[cand]==1].index.tolist():
                #print (i)
    #            plt.text(i,df.iloc[i]["high"],'看涨抱线',fontsize=6,verticalalignment="top",horizontalalignment="right")
                ax.annotate(s=cand, xy=(i,df.iloc[i]["low"]),
                             arrowprops = dict(facecolor = "r", headlength = 6, headwidth =6, width = 10))
                # 如果arrowprops中有arrowstyle,就不应该有其他的属性，xy代表的是箭头的位置，xytext代表的是箭头文本的位置。
        '''
    
        #plt.xticks(rotation = 90) 
        ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        
        ax.grid(True)
        #%% 指标栏
        ax2.hlines(50,150,5, colors = "black", linestyles = "dashed")
        ax2.plot(df.stochfastk,'black',alpha=0.8,linewidth=0.8,label='14日均线')
        ax2.plot(df.stochfastd,'gray',alpha=0.8,linewidth=0.8,label='14日均线')

        ax2.set_ylabel('StochRSI')
    #    ax2.set_title('stoch')
        ax2.xaxis.set_major_locator(ticker.MultipleLocator(30))
        ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        ax2.grid(True)
        #%% RSI指标
    #     ax3.set_ylabel('RSI')
    #     ax3.plot(df.rsi,'gray',alpha=0.8,linewidth=0.8,label='14日均线')
    # #    ax3.set_title('RSI')
    #     ax3.xaxis.set_major_locator(ticker.MultipleLocator(30))
    #     ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    #     ax3.grid(True)
        #%% MACD指标
        ax3.set_ylabel('MACD')
        ax3.plot(df.macd,'#3e4145',alpha=0.8,linewidth=0.8,label='12 26 9日均线')
        ax3.plot(df.macd_signal,'#3e4145',alpha=0.8,linewidth=0.8,label='12 26 9日均线')
        ax3.bar(range(df.shape[0]),df['diff'],facecolor = '#464547',)
        # ax3.set_title('MACD')
        ax3.xaxis.set_major_locator(ticker.MultipleLocator(100))
        ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        ax3.grid(True)

        
         #%% 结束画图
        fig.autofmt_xdate()
        plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
        plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
        candlestick_ohlc(ax,weekday_quotes,colordown='#53c156', colorup='#ff1717',width=0.5)
        plt.show()
    
    else:
        print ("没有连接")
        
