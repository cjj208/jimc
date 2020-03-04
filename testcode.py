# -*- coding: utf-8 -*-

from pytdx.exhq import TdxExHq_API
import ta
api = TdxExHq_API()
with api.connect('218.80.248.229', 7721):
    #查询市场中商品数量
    marketsID = api.to_df(api.get_markets())
    #查询五档行情
    quote =api.to_df(api.get_instrument_quote(47, "IFL8"))
    #查询分时行情
    markets_fenshi = api.to_df(api.get_minute_time_data(47, "IFL8"))
    #查询历史分时行情
    historydata = api.to_df(api.get_history_minute_time_data(47, "IFL8", 20170811))
    #查询k线数据
    kdata = api.to_df(api.get_instrument_bars(0, 47, "IFL8", 0, 700))
    #查询当前分笔成交
    fenbi = api.to_df(api.get_transaction_data(47, "IFL8"))
    
    #查询历史分笔成交
    fenbi_history = api.to_df(api.get_history_transaction_data(47, "IFL8", 20191204, start=1800))
    #查询当天分笔成交
    fenbi_chenjiao = api.to_df(api.get_history_transaction_data(47, "IFL8", 20191204,))
    
    
    
    print (marketsID)
    
    print (quote)
    print (kdata)
    df = kdata
    df["rsi"] = ta.momentum.rsi(df.close,n=14,)
    df['stoch'] = ta.momentum.stoch(df.high,df.low,df.close,14)
    
    
    
    
    
    
    # some codes
    
    