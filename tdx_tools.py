﻿# -*- coding: utf-8 -*-
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

def MACD(df, short, long, m):
    """
    异同移动平均线

    Args:
        df (pandas.DataFrame): Dataframe格式的K线序列

        short (int): 短周期

        long (int): 长周期

        m (int): 移动平均线的周期

    Returns:
        pandas.DataFrame: 返回的DataFrame包含3列, 是"diff", "dea"和"bar", 分别代表离差值, DIFF的指数加权移动平均线, MACD的柱状线

        (注: 因 DataFrame 有diff()函数，因此获取到此指标后："diff"字段使用 macd["diff"] 方式来取值，而非 macd.diff )

    Example::

        # 获取 CFFEX.IF1903 合约的异同移动平均线
        from tqsdk import TqApi, TqSim
        from tqsdk.ta import MACD

        api = TqApi(TqSim())
        klines = api.get_kline_serial("CFFEX.IF1903", 24 * 60 * 60)
        macd = MACD(klines, 12, 26, 9)
        print(list(macd["diff"]))
        print(list(macd["dea"]))
        print(list(macd["bar"]))

        # 预计的输出是这样的:
        [..., 149.58313904045826, 155.50790712365142, 160.27622505636737, ...]
        [..., 121.46944573796466, 128.27713801510203, 134.6769554233551, ...]
        [..., 56.2273866049872, 54.46153821709879, 51.19853926602451, ...]
    """
    new_df = pd.DataFrame()
    eshort = EMA(df["close"], short)
    elong = EMA(df["close"], long)
    new_df["diff"] = eshort - elong
    new_df["dea"] = EMA(new_df["diff"], m)
    new_df["bar"] = 2 * (new_df["diff"] - new_df["dea"])
    return new_df
