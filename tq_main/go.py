#  -*- coding: utf-8 -*-
from tqsdk import TqApi, TqSim,TqAccount
import time
import subprocess
'''
下单

order = api.insert_order(symbol="SHFE.rb2005", direction="BUY", offset="OPEN", volume=1, limit_price=3570)
CFFEX: 中金所 SHFE: 上期所 DCE: 大商所 CZCE: 郑商所 INE: 能源交易所(原油)

'''
try:
    # api = TqApi(TqAccount("H华安期货", "117889998", "262010",front_broker='6020',front_url='tcp://183.11.217.235:41207'),web_gui="0.0.0.0:9876")
    api = TqApi(TqAccount("快期模拟", "cjj208", "Chenjj1230"))
    # api = TqApi(TqAccount("simnow", "090828", "jimc1230",front_broker='9999',front_url='tcp://180.168.146.187:10100'),web_gui="0.0.0.0:9876")#web_gui="0.0.0.0:9876"
    account = api.get_account()  # 获取用户账户资金信息
    klines = api.get_kline_serial('SHFE.rb2005', 5*60,data_length=500)#获取k线序列数据
    position = api.get_position('SHFE.rb2005')#指定一个品种查看持仓相关信息
    order = api.get_order('SHFE.rb2005')# 获取用户委托单信息
    quote = api.get_quote('SHFE.rb2005')#获取指定合约的盘口行情.
    api.is_changing(position, "pos_long_today")#判定obj最近是否有更新
    # orderinsert = api.insert_order(symbol="SHFE.rb2005", direction="BUY", offset="OPEN", volume=1, limit_price=3570)
except Exception as e:
    print("行情服务连不上, 或者期货公司服务器关了, 或者账号密码错了, 总之就是有问题")

# 监听下单后有没有成交
api.wait_update()
order = api.insert_order(symbol="SHFE.rb2005", direction="BUY", offset="CLOSE", volume=5,limit_price=3549)
print("单状态: %s, 已成交: %d 手" % (order.status, order.volume_orign - order.volume_left))


while True:
    # time.sleep(1)
    api.wait_update()


    # subprocess.call("cls",shell=True)  
    # print ("========||品种||========")
    # print ("该品种细则",position.orders)
    # print ("该品种交易所简写：",position.exchange_id)
    # print ("该品种ID：",position.instrument_id)
    # print ("该品种持仓占用：",position.margin)
    # print ("该品种盈亏：",position.float_profit)
    # print ("该品种开仓均价：",position.open_price_long)
    # print ("========||帐户||========")
    # print ("帐户ID：",account.user_id)
    # print ("账户权益",account.balance)
    # print ("浮动盈亏：",account.position_profit)
    # print ("保证金占用：",account.margin)
    # print ("帐户手续费：",account.commission)
    # print ("可用资金：",account.available)
    # print ("=="*10)
