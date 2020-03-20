from tqsdk import TqApi

api = TqApi(web_gui=True,)#web_gui="http://172.20.155.135:62964"要将你订阅的K线或策略图形化显示, 只需在 TqApi() 中传入参数 web_gui = True即可:
quote = api.get_quote("SHFE.rb2005")
print (quote.last_price, quote.volume)


klines = api.get_kline_serial("SHFE.rb2005", 1*60)# 获取K线 pandas结构 60是秒数

#klines = api.get_kline_serial(["SHFE.rb2005","DCE.i2005", "CZCE.AP005"], 60)  # 入一个合约列表作为参数，来获取包含多个合约数据的K线:
ticks = api.get_tick_serial("SHFE.rb2005",data_length=1,)

# for i in klines.iterrows():
#     print (i)
    
#
while True:
    api.wait_update()

    print (ticks.to_dict())

    # print("最后一根K线收盘价", klines.close.iloc[-1])
    # print (quote.datetime, quote.last_price)