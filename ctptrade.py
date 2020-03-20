# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 09:36:38 2020

@author: JimchanChen
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
__title__ = 'test py ctp of se'
__author__ = 'HaiFeng'
__mtime__ = '20190506'

from py_ctp.trade import CtpTrade
from py_ctp.quote import CtpQuote
from py_ctp.enums import *
import time


class TestTrade(object):
    def __init__(self, addr: str, broker: str, investor: str, pwd: str, appid: str, auth_code: str, proc: str):
        self.front = addr
        self.broker = broker
        self.investor = investor
        self.pwd = pwd
        self.appid = appid
        self.authcode = auth_code
        self.proc = proc

        self.t = CtpTrade()
        self.t.OnConnected = self.on_connect
        self.t.OnUserLogin = lambda o, x: print('Trade logon:', x)
        self.t.OnDisConnected = lambda o, x: print(x)
        self.t.OnRtnNotice = lambda obj, time, msg: print(f'OnNotice: {time}:{msg}')
        self.t.OnErrRtnQuote = lambda obj, quote, info: None
        self.t.OnErrRtnQuoteInsert = lambda obj, o: None
        self.t.OnOrder = lambda obj, o: None
        self.t.OnErrOrder = lambda obj, f, info: None
        self.t.OnTrade = lambda obj, o: None
        self.t.OnInstrumentStatus = lambda obj, inst, stat: None




    def on_connect(self, obj):
        self.t.ReqUserLogin(self.investor, self.pwd, self.broker, self.proc, self.appid, self.authcode)

    def run(self):
        self.t.ReqConnect(self.front)
        # self.t.ReqConnect('tcp://192.168.52.4:41205')

    def release(self):
        self.t.ReqUserLogout()


class TestQuote(object):
    """TestQuote"""

    def __init__(self, addr: str, broker: str, investor: str, pwd: str):
        """"""
        self.front = addr
        self.broker = broker
        self.investor = investor
        self.pwd = pwd

        self.q = CtpQuote()
        self.q.OnConnected = lambda x: self.q.ReqUserLogin(self.investor, self.pwd, self.broker)
        self.q.OnUserLogin = lambda o, i: self.q.ReqSubscribeMarketData('ap2005')
        
    def run(self):
        self.q.ReqConnect(self.front)
       
    def release(self):
        self.q.ReqUserLogout()


if __name__ == "__main__":
    
    front_trade = 'tcp://180.168.146.187:10101'#7*24端口10130 
    front_quote = 'tcp://180.168.146.187:10111'
    broker = '9999'
    investor = '090828'
    pwd = 'jimc1230'
    appid = 'simnow_client_test'
    auth_code = '0000000000000000'
    proc = ''
    
    front_trade = 'tcp://183.11.217.235:41207'#7*24端口10130 
    front_quote = 'tcp://183.11.217.235:41215'
    broker = '6020'
    investor = '117889998'
    pwd = '262010'
    appid = 'simnow_client_test'
    auth_code = '0000000000000000'
    proc = ''
    
    '''
BrokerID统一为：9999
标准CTP：
    第一组：Trade Front：180.168.146.187:10100，Market Front：180.168.146.187:10110；【电信】
    第二组：Trade Front：180.168.146.187:10101，Market Front：180.168.146.187:10111；【电信】
    第三组：Trade Front： 218.202.237.33 :10102，Market Front：218.202.237.33 :10112；【移动】
7*24小时环境：
    第一组：Trade Front： 180.168.146.187:10130，Market Front：180.168.146.187:10131；【电信】
    '''
    
    if investor == '':
        investor = input('invesotr:')
        pwd = input('password:')
        appid = input('appid:')
        auth_code = input('auth code:')
        proc = input('product info:')
    tt = TestTrade(front_trade, broker, investor, pwd, appid,)
    tt.run()
    
    time.sleep(3)
    print ("+"*30)
    for i in tt.t.positions:print (tt.t.positions[i])
    
    cbj = tt.t.trades
    obj = tt.t.positions
    for key in obj:
        print(key)
        itm = obj[key]
        print("CloseProfit",itm.CloseProfit)
        print("Commission",itm.Commission)
        print("InstrumentID",itm.InstrumentID) 
        

  

#    time.sleep(5)
    #买入限价单
     #tt.t.ReqOrderInsert('AP005', DirectType.Buy, OffsetType.Open, 6805, 1)
     #卖出限价单
#    tt.t.ReqOrderInsert('fu2005', DirectType.Sell, OffsetType.Open, 2009, 1)
     #平仓
#    tt.t.ReqOrderInsert('fu2005', DirectType.Sell, OffsetType.Open, 2044, 1)
     
#    tt.t.ReqOrderInsert('rb2005', DirectType.Sell, OffsetType.Close, 3421, 1)
     #撤单
    #tt.t.ReqOrderAction(list(tt.t.orders)[-1])#撤单
    #tt.t.ReqOrderInsert('ag2006', DirectType.Buy, OffsetType.Open, 4120, 1)
    
#    qq.q.ReqConnect(qq.front)
#    tt.t._OnRspQryPositionDetail
         
    #全撤
    for i in list(tt.t.orders.keys()):
        tt.t.ReqOrderAction(i)#撤单)
#    time.sleep(3)
    qq = TestQuote(front_quote, broker, investor, pwd)
#    qq.q.ReqSubscribeMarketData
    qq.q.ReqConnect(qq.front) 

#    qq.run()
    
 
    # time.sleep(6)
  #  for inst in tt.t.instruments.values():
       # print(inst)
#    input()
#    tt.release()
#    qq.release()
#    input()