#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'chengzhi'
import subprocess
from tqsdk import TqApi,TqAccount
import nest_asyncio
nest_asyncio.apply()
# api = TqApi(TqAccount("H华安期货", "117889998", "262010",front_broker='6020',front_url='tcp://183.11.217.235:41207'),web_gui="0.0.0.0:9876")
# api = TqApi(TqAccount("快期模拟", "cjj208", "Chenjj1230"))
api = TqApi(TqAccount("simnow", "090828", "jimc1230",front_broker='9999',front_url='tcp://180.168.146.187:10100'),web_gui="0.0.0.0:9876")

# 获得 m2005 的持仓引用，当持仓有变化时 position 中的字段会对应更新
position = api.get_position("SHFE.rb2005")
# 获得资金账户引用，当账户有变化时 account 中的字段会对应更新
account = api.get_account()
# 下单并返回委托单的引用，当该委托单有变化时 order 中的字段会对应更新
order = api.insert_order(symbol="SHFE.rb2005", direction="BUY", offset="OPEN", volume=2, limit_price=3521)
#canorder = api.cancel_order(order)

while True:
    api.wait_update()  
    if api.is_changing(order, ["status", "volume_orign", "volume_left"]):
         #subprocess.call("cls",shell=True)  
        print("单状态: %s, 已成交: %d 手" % (order.status, order.volume_orign - order.volume_left))
    if api.is_changing(position, "pos_long_today"):
        print("今多头: %d 手" % (position.pos_long_today))
    if api.is_changing(account, "available"):
        print("可用资金: %.2f" % (account.available))
