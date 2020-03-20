
#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

'''
双均线策略
'''
from tqsdk import TqApi, TqSim, TargetPosTask,TqAccount,TqBacktest
from tqsdk.ta import MA,SMA,SAR
from datetime import date
from tqsdk import TqReplay
from tqsdk.ta import MACD
from tqsdk.tafunc import ma
from supert import ST
import numpy as np
import pandas as pd  


def ATR(df, period, ohlc=['open', 'high', 'low', 'close']):  

    """  
    Function to compute Average True Range (ATR)  
    Args :  
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns  
        period : Integer indicates the period of computation in terms of number of candles  
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])  
    Returns :  
        df : Pandas DataFrame with new columns added for  
            True Range (TR)  
            ATR (ATR_$period)  
    """  
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

def SuperTrend(df, period, multiplier, ohlc=['open', 'high', 'low', 'close']):  
    """  
    Function to compute SuperTrend  
    Args :  
        df : Pandas DataFrame which contains ['date', 'open', 'high', 'low', 'close', 'volume'] columns  
        period : Integer indicates the period of computation in terms of number of candles  
        multiplier : Integer indicates value to multiply the ATR  
        ohlc: List defining OHLC Column names (default ['Open', 'High', 'Low', 'Close'])  
    Returns :  
        df : Pandas DataFrame with new columns added for  
            True Range (TR), ATR (ATR_$period)  
            SuperTrend (ST_$period_$multiplier)  
            SuperTrend Direction (STX_$period_$multiplier)  
    """

    ATR(df, period, ohlc=ohlc)  
    atr = 'ATR_' + str(period)  
    st = 'ST_' + str(period) + '_' + str(multiplier)  
    stx = 'STX_' + str(period) + '_' + str(multiplier)  
    """  
    SuperTrend Algorithm :  
        BASIC UPPERBAND = (HIGH + LOW) / 2 + Multiplier * ATR  
        BASIC LOWERBAND = (HIGH + LOW) / 2 - Multiplier * ATR  
        FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous Close > Previous FINAL UPPERBAND))  
                            THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)  
        FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous Close < Previous FINAL LOWERBAND))  
                            THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)  
        SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close <= Current FINAL UPPERBAND)) THEN  
                        Current FINAL UPPERBAND  
                    ELSE  
                        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current Close > Current FINAL UPPERBAND)) THEN  
                            Current FINAL LOWERBAND  
                        ELSE  
                            IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close >= Current FINAL LOWERBAND)) THEN  
                                Current FINAL LOWERBAND  
                            ELSE  
                                IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current Close < Current FINAL LOWERBAND)) THEN  
                                    Current FINAL UPPERBAND  
    """  
    # Compute basic upper and lower bands  
    df['basic_ub'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 + multiplier * df[atr]  
    df['basic_lb'] = (df[ohlc[1]] + df[ohlc[2]]) / 2 - multiplier * df[atr]

    # Compute final upper and lower bands  
    df['final_ub'] = 0.00  
    df['final_lb'] = 0.00  
    for i in range(period, len(df)):  
        df['final_ub'].iat[i] = df['basic_ub'].iat[i] if df['basic_ub'].iat[i] < df['final_ub'].iat[i - 1] or df['Close'].iat[i - 1] > df['final_ub'].iat[i - 1] else df['final_ub'].iat[i - 1]  
        df['final_lb'].iat[i] = df['basic_lb'].iat[i] if df['basic_lb'].iat[i] > df['final_lb'].iat[i - 1] or df['Close'].iat[i - 1] < df['final_lb'].iat[i - 1] else df['final_lb'].iat[i - 1]  
    # Set the Supertrend value  
    df[st] = 0.00  
    for i in range(period, len(df)):  
        df[st].iat[i] = df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df['Close'].iat[i] <= df['final_ub'].iat[i] else 0
                        df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_ub'].iat[i - 1] and df['Close'].iat[i] >  df['final_ub'].iat[i] else 0
                        df['final_lb'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df['Close'].iat[i] >= df['final_lb'].iat[i] else 0
                        df['final_ub'].iat[i] if df[st].iat[i - 1] == df['final_lb'].iat[i - 1] and df['Close'].iat[i] <  df['final_lb'].iat[i] else 0.00  
    # Mark the trend direction up/down  
    df[stx] = np.where((df[st] > 0.00), np.where((df[ohlc[3]] < df[st]), 'down',  'up'), np.NaN)

    # Remove basic and final bands from the columns  
    df.drop(['basic_ub', 'basic_lb', 'final_ub', 'final_lb'], inplace=True, axis=1)  
    df.fillna(0, inplace=True)

    return df





if __name__ == "__main__":

    data_length = 200  # k线数据长度
    SYMBOL = "SHFE.rb2005"  # 合约代码
    # api = TqApi(TqAccount("simnow", "090828", "jimc1230",front_broker='9999',front_url='tcp://180.168.146.187:10100'),web_gui="0.0.0.0:9876")#web_gui="0.0.0.0:9876"
    api = TqApi(backtest=TqBacktest(start_dt=date(2020, 3,1), end_dt=date(2020, 3, 18)),web_gui=True)#"0.0.0.0:9876"
    print("策略开始运行")

    # "duration_seconds=60"为一分钟线, 日线的duration_seconds参数为: 24*60*60
    klines = api.get_kline_serial(SYMBOL, duration_seconds=3*60, data_length=data_length)

    #收盘后不可查
    target_pos = TargetPosTask(api, SYMBOL)
    position = api.get_position(SYMBOL)#指定一个品种查看持仓相关信息
    account = api.get_account()#获取用户账户资金信息

    while True:
        api.wait_update()
        klines["ma5"]=ma(klines["close"], 5) 
        klines["ma10"]=ma(klines["close"], 10)  
        klines["ma89"]=ma(klines["close"], 89)
        klines["ma144"]=ma(klines["close"], 144)
        sar=SAR(klines, 4, 0.02, 0.2)
        st = SuperTrend(klines, period=10,multiplier=2)
        print (st.columns)
        print (st)
        if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算SMA

            if klines['close'].iloc[-1] < klines['ma89'].iloc[-2]:
                if klines["ma5"].iloc[-2] < klines["ma10"].iloc[-2] and klines["ma10"].iloc[-1] > klines["ma5"].iloc[-1]:
                    target_pos.set_target_volume(-1)
                    print("均线下穿，做空")
                elif klines["close"].iloc[-2] > klines["ma5"].iloc[-2]:
                    target_pos.set_target_volume(0)
                    print("均线上穿，平空")

            # 均线上穿，做多


            else:
                if klines["ma5"].iloc[-2] < klines["ma10"].iloc[-2] and klines["ma5"].iloc[-1] > klines["ma10"].iloc[-1]:
                    target_pos.set_target_volume(1)
                    print("均线上穿，做多")
                    # print("多头开仓均价:",position.position_price_long)
                elif  klines["close"].iloc[-2] < klines["ma5"].iloc[-2]:

                    target_pos.set_target_volume(0)
                    print("均线下穿，平多")
