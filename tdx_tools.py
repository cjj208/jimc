# -*- coding: utf-8 -*-
"""
Created on Tue May  8 15:43:25 2018

@author: JimchanChen
"""
#from art import tprint 
import time as t
#import win32com.client
#import winsound
import ta
import numpy as np
import pandas as pd
import prettytable as pt
import datetime
import config
from email.header import Header 
from email.mime.text import MIMEText
import smtplib
import platform
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt

def show_menu():
    """显示菜单"""
    print ("欢迎使用【股票期货预警系统】V1.0")
    print ("*"*60)
    print ("actionStock",)
    print ("*"*60)    
def beep():
    count = 0
    while (count < 1):
        t.sleep(0.5)
#        spk = win32com.client.Dispatch("SAPI.SpVoice")
#        spk.Speak("priceAction")
        #winsound.Beep(1500, 500)
        #winsound.Beep(1500, 500)
        pass
        count += 1


def oncetime():
    #设置间隔时间
    cate = config.category
    if cate == 7:
        if datetime.datetime.now().minute%1==0:  #一分钟
            return True
        else:
            return False
        
    if cate == 0:
        if (datetime.datetime.now().minute%5==4) & (datetime.datetime.now().second>=50):#五分钟
            return True
        else:
            return False  
    if cate == 1:
        if (datetime.datetime.now().minute%15 == 0) & (datetime.datetime.now().second<=5):#15分钟    
            return True
        else:
            return False  
    if cate == 3:
        if (datetime.datetime.now().minute==59) & (datetime.datetime.now().second>=50):#一小时  
            return True
        else:
            return False  
        

    
def winorlinux():
    #判断是否是windows或是linux系统执行不同的清屏命令
    sysname = platform.system()
    if sysname == "Windows":    
        return "cls"
        
    else:
        return "clear"
        
def k_zhouqi():
    
    if config.category ==0:
        return "5分钟K线"
    if config.category ==1:
        return "15分钟K线 "
    if config.category ==2:
        return "30分钟K线"
    if config.category ==3:
        return "1小时K线"
    if config.category ==4:
        return "日K线"
    if config.category ==5:
        return "周K线"
    if config.category ==6:
        return "月K线"
    if config.category ==7:
        return "1分钟"    
    

def SuperTrend(df, period, multiplier, ohlc=['open', 'high', 'low', 'close']):


    ATR(df, period, ohlc=ohlc)
    atr = 'ATR_' + str(period)
    #st = 'ST_' + str(period) + '_' + str(multiplier)
    st = 'supertrend'
    stx = 'STX_' + str(period) + '_' + str(multiplier)
    stx = 'st_reverse'


    # Compute basic upper and lower bands
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands
    df['final_ub'] = 0.00
    df['final_lb'] = 0.00
    for i in range(period, len(df)):
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] > df['final_ub'].iat[i - 1] else \
        df['final_ub'].iat[i - 1]
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or \
                                                         df[ohlc[3]].iat[i - 1] < df['final_lb'].iat[i - 1] else \
        df['final_lb'].iat[i - 1]

    # Set the Supertrend value
    df[st] = 0.00
    for i in range(period, len(df)):
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[
            i] <= df['final_ub'].iat[i] else \
            df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df[ohlc[3]].iat[i] > \
                                     df['final_ub'].iat[i] else \
                df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] >= \
                                         df['final_lb'].iat[i] else \
                    df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df[ohlc[3]].iat[i] < \
                                             df['final_lb'].iat[i] else 0.00

        # Mark the trend direction up/down
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down', 'up'), np.NaN)
    df['superpoint'] = np.where(
            (df["st_reverse"] != df["st_reverse"].shift(1)) 
            & (df.st_reverse=='up'),1,np.where((df["st_reverse"] 
            != df["st_reverse"].shift(1)) & (df.st_reverse=='down')
            ,-1,0))#当st_f=1则发生短期反转

    # Remove basic and final bands from the columns
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb','TR',atr], inplace=True, axis=1)

    df.fillna(0, inplace=True)

    return df


def ATR(df, period, ohlc=['open', 'high', 'low', 'close']):

    atr = 'ATR_' + str(period)

    # Compute true range only if it is not computed and stored earlier in the df
    if not 'TR' in df.columns:
        df['h-l'] = df[ohlc[1]] - df[ohlc[2]]
        df['h-yc'] = abs(df[ohlc[1]] - df[ohlc[3]].shift())
        df['l-yc'] = abs(df[ohlc[2]] - df[ohlc[3]].shift())

        df['TR'] = df[['h-l', 'h-yc', 'l-yc']].max(axis=1)

        df.drop(['h-l', 'h-yc', 'l-yc'], inplace=True, axis=1)

    # Compute EMA of true range using ATR formula after ignoring first row
    EMA(df, 'TR', atr, period, alpha=True)

    return df


def SMA(df, base, target, period):
    """
    Function to compute Simple Moving Average (SMA)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the SMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles

    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    df[target] = df[base].rolling(window=period).mean()
    df[target].fillna(0, inplace=True)

    return df


def EMA(df, base, target, period, alpha=False):
    """
    Function to compute Exponential Moving Average (EMA)

    Args :
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns
        base : String indicating the column name from which the EMA needs to be computed from
        target : String indicates the column name to which the computed data needs to be stored
        period : Integer indicates the period of computation in terms of number of candles
        alpha : Boolean if True indicates to use the formula for computing EMA using alpha (default is False)

    Returns :
        df : Pandas DataFrame with new column added with name 'target'
    """

    con = pd.concat([df[:period][base].rolling(window=period).mean(), df[period:][base]])

    if (alpha == True):
        # (1 - alpha) * previous_val + alpha * current_val where alpha = 1 / period
        df[target] = con.ewm(alpha=1 / period, adjust=False).mean()
    else:
        # ((current_val - previous_val) * coeff) + previous_val where coeff = 2 / (period + 1)
        df[target] = con.ewm(span=period, adjust=False).mean()

    df[target].fillna(0, inplace=True)
    return df

def sohu_sendmail(mail,sub,mesg):

    try:
        mail_host="smtp.sohu.com"  #设置服务器  
        mail_user=("cjj208@sohu.com")    #用户名  
        mail_pass="123qwe@@"   #口令,QQ邮箱是输入授权码，在qq邮箱设置 里用验证过的手机发送短信获得，不含空格  
        sender = 'cjj208@sohu.com'  
        receivers = [(mail)]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱  
        message = MIMEText(mesg, 'plain', 'utf-8')  
        message['From'] = Header(mail_user, 'utf-8')  
        message['To'] =  Header(sender, 'utf-8')  
        subject = (sub)
        message['Subject'] = Header(subject, 'utf-8')  
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)   
        smtpObj.login(mail_user,mail_pass)    
        smtpObj.sendmail(sender, receivers, message.as_string())  
        smtpObj.quit()  
    except Exception as e:
        print ("未发送邮件！%s"% e)
    
def StochRSI(df,m,p):
      df["rsi"] = ta.momentum.rsi(df.close,n=m,)

      RSI = df.rsi
      print(RSI)
      LLV= RSI.rolling(window=m).min()
      HHV= RSI.rolling(window=m).max()
      stochRSI = (RSI  - LLV) / (HHV - LLV) * 100
     
#      fastk = RSI.MA(np.array(stochRSI)  , p)
#      fastd = RSI.MA(np.array(fastk), p)

      
      df['stochfastk'] = stochRSI.rolling(window=p).mean()
      df['stochfastk'].fillna(0, inplace=True)
      
      df['stochfastd'] = df['stochfastk'].rolling(window=p).mean()
      df['stochfastd'].fillna(0, inplace=True)
      return df 

    
def donchian_channel_hband(close, n=20, fillna=False):
    """Donchian channel (DC)

    The upper band marks the highest price of an issue for n periods.

    https://www.investopedia.com/terms/d/donchianchannels.asp

    Args:
        close(pandas.Series): dataset 'Close' column.
        n(int): n period.

    Returns:
        pandas.Series: New feature generated.
    """
    hband = close.rolling(n).max()
    if fillna:
        hband = hband.replace([np.inf, -np.inf], np.nan).fillna(method='backfill')
    return pd.Series(hband, name='dchband')


def donchian_channel_lband(close, n=20, fillna=False):
    """Donchian channel (DC)

    The lower band marks the lowest price for n periods.

    https://www.investopedia.com/terms/d/donchianchannels.asp

    Args:
        close(pandas.Series): dataset 'Close' column.
        n(int): n period.

    Returns:
        pandas.Series: New feature generated.
    """
    lband = close.rolling(n).min()
    if fillna:
        lband = lband.replace([np.inf, -np.inf], np.nan).fillna(method='backfill')
    return pd.Series(lband, name='dclband')

def charts(df,cflen):
    #%%画K线主图
    weekday_quotes=[tuple([i]+list(quote[1:])) for i,quote in enumerate(df.values,)]
    fig = plt.figure(figsize=(1000 / 72, 500 / 72),facecolor='#CCCCCC', edgecolor='#CCCCCC')
    ax = fig.add_subplot(4,1,(1,2))
    ax.set_facecolor('#CCCCCC')

    ax.set_ylabel('K线主图')
            
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
#    ax.plot(df["sma5"],color="black",linewidth=0.5,linestyle="-")
#    ax.plot(df["sma10"],color="black",linewidth=0.5,linestyle="-")
#    ax.plot(df["sma20"],color="black",linewidth=0.5,linestyle="-")
    ax.plot(df["sma89"],color="black",linewidth=0.5,linestyle="-")
    ax.plot(df["sma144"],color="black",linewidth=0.5,linestyle="-")
    ax.set_title("||%s||%s||%s" % (config.cfqihuo[cflen]["stockname"],config.cfqihuo[cflen]["code"],k_zhouqi()))
    candlelist = ['看涨抱线','看涨刺透','看涨孕线','看跌吞没','看跌孕线','看涨一线穿','看跌一线穿']
    candlelist = ['看跌一线穿',]
    for i in list(df[df["superpoint"]==1].index):
     
        ax.annotate(s="superPoint",xy=(i,df.iloc[i]["low"]),arrowprops = dict(facecolor = "r", 
                    headlength = 10, headwidth =10, width = 20))
        
    for cand in candlelist:
        for i in df[df[cand]==1].index.tolist():
            #print (i)
    #        plt.text(i,df.iloc[i]["high"],'看涨抱线',fontsize=6,verticalalignment="top",horizontalalignment="right")
            ax.annotate(s=cand, xy=(i,df.iloc[i]["low"]),
                         arrowprops = dict(facecolor = "r", headlength = 6, headwidth =6, width = 10))
            # 如果arrowprops中有arrowstyle,就不应该有其他的属性，xy代表的是箭头的位置，xytext代表的是箭头文本的位置。
    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
    #plt.xticks(rotation = 90) 
    ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    
    ax.grid(True)
    #%% 指标栏
    ax2.hlines(50,150,5, colors = "black", linestyles = "dashed")
    ax2.plot(df.stoch,'gray',alpha=0.8,linewidth=0.8,label='14日均线')
    ax2.set_ylabel('STOCH')
#    ax2.set_title('stoch')
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(30))
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax2.grid(True)
    #%% RSI指标
    ax3.set_ylabel('RSI')
    ax3.plot(df.rsi,'gray',alpha=0.8,linewidth=0.8,label='14日均线')
#    ax3.set_title('RSI')
    ax3.xaxis.set_major_locator(ticker.MultipleLocator(30))
    ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    ax3.grid(True)
    fig.autofmt_xdate()
    
    candlestick_ohlc(ax,weekday_quotes,colordown='#53c156', colorup='#ff1717',width=0.5)
    
    plt.show()

if __name__ == '__main__':
    import tdx_tools
    import config
    from pytdx.hq import TdxHq_API
    import matplotlib.pyplot as plt
    from mpl_finance import candlestick_ohlc
    cf = config

    api = TdxHq_API()
    
    for i in cf.cfstock:
            
        code = i['code']
        marketid = i['marketid']
        stockname = i['stockname']
        with api.connect("58.63.254.191",7709):
            
            
            stocklist = config.cfstock
            data = api.get_security_bars(3,marketid,code,0,400) 
            #sh = api.to_df(api.get_index_bars(0,1,"000001",1,400))  #获得指数 0 5分钟K线 1 15分钟K线 2 30分钟K线 3 1小时K线 4 日K线 
#            kzhqData = kzhqapi.get_instrument_bars(TDXParams.KLINE_TYPE_5MIN, int(cfkz.get(i,"marketID")), cfkz.get(i,"code"), 0, 200)#7: 扩展行情查询k线数据
            df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close'],)

            
            df["datetime"] = pd.to_datetime(df["datetime"],format="%Y-%m-%d %H:%M:%S")
            df['dc_hband'] = tdx_tools.donchian_channel_hband(df.close,10)
            df['dc_lband'] = tdx_tools.donchian_channel_lband(df.close,10)
            
            df['stockname'] = stockname
            df['code'] = code
            df['dc_hband'] = tdx_tools.donchian_channel_hband(df.close,cf.dc_count)
            df['dc_lband'] = tdx_tools.donchian_channel_lband(df.close,cf.dc_count)
            
            df['dc_break'] = np.where((df['close'] > df['dc_hband'].shift(1)),1,
                    np.where((df['close'] < df['dc_lband'].shift(1)),-1,0))
            #这里是算突破的信号，当往上突破为1，当往下突破为-1，震荡区间为0
    
            df = df.set_index('datetime')
            df["sma5"] = df['close'].rolling(5).mean()
            df["sma10"] = df['close'].rolling(10).mean()
            df["sma20"] = df['close'].rolling(20).mean()
            df["sma89"] = df['close'].rolling(89).mean()
            df["sma144"] = df['close'].rolling(144).mean()
            df["sma89144"] = np.where(df['close']>df['sma89'],1,np.where(df['close']<df['sma144'],-1,0))
            df["sma51020"] = np.where(df['close']>df['sma5'],1,np.where(df['close']<df['sma20'],-1,0))

            df = df.dropna()
            df = tdx_tools.SuperTrend(df,period=cf.st_period_fast,multiplier=cf.st_mult_fast,)
#            df = tdx_tools.SuperTrendSlow(df,period=cf.st_period_slow,multiplier=cf.st_mult_slow,)
            
            df = df[20:]
#       
            df = df.reset_index()
    
        
            tdx_tools.charts(df,2)
            '''
            weekday_quotes=[tuple([i]+list(quote[1:])) for i,quote in enumerate(df.values,)]
            df = df.reset_index()    
            fig, ax = plt.subplots(figsize=(1200 / 72, 480 / 72), facecolor='#CCCCCC', edgecolor='black')
        
            plt.subplots_adjust(top=0.944, bottom=0.148, left=0.034, right=0.969, hspace=0.2, wspace=0.2)
            ax.set_facecolor('#FFFFFF')
            ax.set_title("||%s||%s" % (stockname,code))
            ax.plot(df["supertrend"],color="#ff9900",linewidth=0.5,linestyle="-")
#            ax.plot(df["supertrendSlow"],color="#ff9900",linewidth=0.5,linestyle="-")
            ax.plot(df["sma5"],color="black",linewidth=0.5,linestyle="-")
            ax.plot(df["sma10"],color="black",linewidth=0.5,linestyle="-")
            ax.plot(df["sma20"],color="black",linewidth=0.5,linestyle="-")
            ax.plot(df["sma89"],color="#CCCCCC",linewidth=1,linestyle="-")
            ax.plot(df["sma144"],color="#CCCCCC",linewidth=1,linestyle="-")
            ax.plot(df["dc_hband"],color="black",linewidth=1,linestyle="-")
            ax.plot(df["dc_lband"],color="black",linewidth=1,linestyle="-")

            candlestick_ohlc(ax, weekday_quotes, colordown='#009900', colorup='#ff6666', width=0.5)
    

                             
            date_tickers=df.datetime.values
            def format_date(x,pos=None):
                if x<0 or x>len(date_tickers)-1:
                    return ''
                return date_tickers[int(x)]
            ax.xaxis.set_major_locator(ticker.MultipleLocator(6))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
            ax.grid(True)
            fig.autofmt_xdate()
        
            candlestick_ohlc(ax,weekday_quotes,colordown='#53c156', colorup='#ff1717',width=0.5)
            plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
            plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
            plt.show()
            '''