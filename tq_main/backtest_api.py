#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'

from datetime import date
from tqsdk import TqApi, TqBacktest, TargetPosTask,TqReplay
from tqsdk.ta import SAR

from tqsdk.tafunc import ma

'''
如果当前价格大于5分钟K线的MA15则开多仓
如果小于则平仓
回测从 2018-05-01 到 2018-10-01
'''
# 在创建 api 实例时传入 TqBacktest 就会进入回测模式
api = TqApi(backtest=TqBacktest(start_dt=date(2020, 3, 1), end_dt=date(2020, 3, 16)),web_gui="0.0.0.0:9876")#"0.0.0.0:9876"
# api = TqApi(backtest=TqReplay(date(2020, 3, 16)),web_gui=True)
# 获得 m1901 5分钟K线的引用
klines = api.get_kline_serial("SHFE.rb2005", 5 * 60, data_length=300)
# 创建 m1901 的目标持仓 task，该 task 负责调整 m1901 的仓位到指定的目标仓位
target_pos = TargetPosTask(api, "SHFE.rb2005")

while True:
    api.wait_update()
    api.draw_text(klines, "--", x=-1, y=klines.iloc[-1].high, color=0xFFFF3333)


    if api.is_changing(klines.iloc[-1], "datetime"):  # 产生新k线:重新计算SMA
        klines["ma5"]=ma(klines["close"], 5) 
        klines["ma10"]=ma(klines["close"], 10)  
        klines["ma89"]=ma(klines["close"], 89)
        klines["ma144"]=ma(klines["close"], 144)
        sar=SAR(klines, 4, 0.02, 0.2)
        if klines["ma5"].iloc[-2] < klines["ma10"].iloc[-2]and klines["ma10"].iloc[-1] > klines["ma5"].iloc[-1]:
            target_pos.set_target_volume(-1)
            print("均线下穿，做空")
            
            # print("空头开仓:",position.position_price_short)

        # 均线上穿，做多
        if klines["ma5"].iloc[-2] < klines["ma10"].iloc[-2] and klines["ma5"].iloc[-1] > klines["ma10"].iloc[-1]:
            target_pos.set_target_volume(1)
            print("均线上穿，做多")
            # print("多头开仓均价:",position.position_price_long)
