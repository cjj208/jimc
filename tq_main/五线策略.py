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
from tqsdk.tafunc import ma
data_length = 200  # k线数据长度

SYMBOL = "SHFE.rb2005"  # 合约代码
api = TqApi(TqAccount("simnow", "090828", "jimc1230",front_broker='9999',front_url='tcp://180.168.146.187:10100'),web_gui="0.0.0.0:9876")#web_gui="0.0.0.0:9876"
# api = TqApi(backtest=TqBacktest(start_dt=date(2020, 3,10), end_dt=date(2020, 3, 19)),web_gui="0.0.0.0:9876")#"0.0.0.0:9876"#回测模式
# api = TqApi(backtest = TqReplay(date(2020,3,18)),web_gui="0.0.0.0:9876")#复盘模式
print("策略开始运行")


# "duration_seconds=60"为一分钟线, 日线的duration_seconds参数为: 24*60*60
klines = api.get_kline_serial(SYMBOL, duration_seconds=1*60, data_length=data_length)

#收盘后不可查
target_pos = TargetPosTask(api, SYMBOL)
position = api.get_position(SYMBOL)#指定一个品种查看持仓相关信息
account = api.get_account()#获取用户账户资金信息

while True:
    api.wait_update()
    
    

    if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算SMA
        klines["ma5"]=ma(klines["close"], 5) 
        klines["ma10"]=ma(klines["close"], 10)  
        klines["ma89"]=ma(klines["close"], 89)
        klines["ma144"]=ma(klines["close"], 144)
        sar=SAR(klines, 4, 0.02, 0.2)
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
